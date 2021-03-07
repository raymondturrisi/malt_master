############################################
############   Description   ###############
############################################



############################################
##############   INCLUDES   ################
############################################

import math as m
import serial
import time as time
import tkinter as tk
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import os
import serial.tools.list_ports


############################################
########   WINDOW CONSTRUCTION   ###########
############################################

##Window Geometry
ar = 1.777777777777777777777 ##aspect ratio of 16:9 for standard scaleable gui's
w = 1200
h = int(w/ar)
fontSize = int(16*h/500)

##Window Construction
window = tk.Tk()
window.title("Malt Master - Hub")
window.geometry(f'{w}x{h}')


############################################
##############   Variables   ###############
############################################

##Input variables

#local variables which are loaded by the UI, before added into a job
#stage 1: wash cycle
des_wash_duration = 0 #hours, positive real number
des_wash_tumble_rate = 0 #cycles per hour
des_wash_tumble_duration = 0 #for how long to tumble the germ, seconds
des_wash_volume = 0 #gallons: determined by weight of the silo, or time
des_wash_cycles = 0 #number of cycles to perform with the above conditions
#stage 2: steep cycle
des_steep_duration = 0 #hours
des_steep_tumble_rate = 0 #cycles per hour
des_steep_tumble_duration = 0 #for how long to tumble the germ, seconds
des_steep_water_vol = 0 #gallons: determined by ultrasonic sensor, weight, or time
des_steep_temp = 0 #farenheight 
des_steep_cycles = 0 # number of cycles to perform with the above conditions
#stage 3: germination cycle
des_germ_duration = 0 #hours, positive real number
des_germ_tumble_rate = 0 #cycles per hour
des_germ_tumble_duration = 0 #for how long to tumble the germ, seconds
des_germ_mist_rate = 0 #the % time on the valve will be open during a tumble process
des_germ_o2 = 0 #seconds to keep the oxygen valve open

cs_state = 0
#stage 4: kiln/drying phase
des_cs_duration = 0 #hours, positive real number
des_cs_tumble_rate = 0 #cycles per hour
des_cs_tumble_duration = 0 #for how long to tumble the germ, seconds
des_cs_temperature = 0 #farenheight

#Received variables, which are used for plotting, and describing the state of the current job
gs_state = 0

gs_water_level = 0
gs_initial_weight = 0
gs_current_weight = 0
gs_power = 0
gs_temperature = 0

gs_recent_tumble = 0
cs_power = 0


#Builds temporary time and temp objects for tk.Entry
temp_timeOBJ = tk.DoubleVar()
temp_time = 0.000
temp_tempOBJ = tk.DoubleVar()
temp_temp = 0.000

#Pre initializes objects to later be updated and called as a global variable between functions
job_time_seconds_entry = tk.Entry()
job_temp_entry = tk.Entry()
fig = Figure(figsize = (5, 5), dpi = 90) 
canvas = FigureCanvasTkAgg(fig, master = window)
plot_main = fig.add_subplot(111)
arduino = serial.Serial()

kilnInfo = tk.Text()
gsInfo = tk.Text()

#Reading from arduino
button_on_board = 0
a_read = 0;

#Timers and global flags
inc_time_monitor = 0.00
ahead_simulator_time = 0
ahead_time_processmgr = 0;
buttonPressFlag = False


#Message types
#types
# - input to arduino
#   - loading a job -> build message, send message, listen for confirmation message has been received
#   - pause/unpause -> turn off all operations and save state of system, or unpack recent state, listen for confirmation that message has been received
#   1,[all job information]
#   2, [0,1] (meaning its a control flow command, and either paused (not running), or not paused (running)
#   3 (close application, purge system)
# - received from arduino
#   - message received -> confirmation that message has been received by arduino
#   9 (a single number signifying that a message has been received, which the type of 9 is outside of all other message prefixes)
#   - stage, state, [relevant information] -> condition information received by arduino
#   4,5,[conditions], signifying that it is the drying stage at state 5


#Job class
class job:
    ##stage and state tracking of the current job
    #########Consider changing all the variables to constituents of a map
    stage = 0 # [1,2,3,4] -> Washing, Steeping, Germination, Drying
    state = 0 #unique to states for each stage

    ##Desired parameters for the job, to be sent to the arduino
    #stage 1: wash cycle
    des_wash_duration = 0 #hours, positive real number
    des_wash_tumble_rate = 0 #cycles per hour
    des_wash_tumble_duration = 0 #for how long to tumble the germ, seconds
    des_wash_volume = 0 #gallons: determined by weight of the silo, or time
    des_wash_cycles = 0 #number of cycles to perform with the above conditions
    #stage 2: steep cycle
    des_steep_duration = 0 #hours
    des_steep_tumble_rate = 0 #cycles per hour
    des_steep_tumble_duration = 0 #for how long to tumble the germ, seconds
    des_steep_water_vol = 0 #gallons: determined by ultrasonic sensor, weight, or time
    des_steep_temp = 0 #farenheight 
    des_steep_cycles = 0 # number of cycles to perform with the above conditions
    #stage 3: germination cycle
    des_germ_duration = 0 #hours, positive real number
    des_germ_tumble_rate = 0 #cycles per hour
    des_germ_tumble_duration = 0 #for how long to tumble the germ, seconds
    des_germ_temp = 0 #farenheight 
    des_germ_mist_rate = 0 #the % time on the valve will be open during a tumble process
    des_germ_o2 = 0 #seconds to keep the oxygen valve open

    cs_state = 0
    #stage 4: kiln/drying phase
    des_cs_duration = 0 #hours, positive real number
    des_cs_tumble_rate = 0 #cycles per hour
    des_cs_tumble_duration = 0 #for how long to tumble the germ, seconds
    des_cs_temp = 0 #farenheight

    ##Current parameters communicated to the user, received by the arduino
    #synonomous with all stages
    rem_time = 0 #remaining time in hours, for the current reporting stage
    rec_tumble = 0 #most recent tumble
    def temp_general(self):
        if self.stage == 1:
            return ["NA", self.cur_temp]
        elif self.stage == 2:
            return [self.des_steep_temp, self.cur_temp]
        elif self.stage == 3: 
            return [self.des_germ_temp, self.cur_temp]
        elif self.stage == 4:
            return [self.des_cs_temp, self.cur_temp]
        else:
            return ["NA","NA"]

    def getStep(self):
        #make embedded switch case statements describing the stage and state
        return 0

    def getGSTimes(self):
        #make function which returns the remaining time for the current step, and the total time remaining for the GS, and returns a nice string
        return "0H/0H"
    cur_water_vol = 0 #current volume of water in gallons
    rem_cycles = 0 #number of cycles remaining
    cur_temp = 0 #farenheight

    #unique to stages 1-3
    cur_water_height = 0 #inches, from top
    cur_weight = 0 #pounds
    cur_power_cs = 0 #watts

    #unique to germination stage
    rec_germ_mist = 0 #the % time on the valve will be open during a tumble process
    rec_germ_o2 = 0 #seconds to keep the oxygen valve open

    #unique to convection stage
    cur_cs_humidity = 0

    ##variables for logging data
    job_name = "" #the prefix/name for the .csv file

    #information is stored in the job until completion, then written all at once to minimize the number of concurrently open file streams
    #stages are stored in separate .csv files due to varying job lengths and uniqueness of each stage
    stage1_time_log = [] #time stamps for stage 1 activity
    stage1_temp_log = [] #temp log for stage 1 activity
    stage1_state_log = [] #discrete state log for stage 1 activity, will be stored in integers but associated to a key to describe activity
    stage1_weight_log = []
    stage2_time_log = [] 
    stage2_temp_log = [] 
    stage2_state_log = [] 
    stage3_time_log = [] 
    stage3_temp_log = [] 
    stage3_state_log = [] 
    stage4_time_log = [] 
    stage4_temp_log = [] 
    stage4_humidity_log = [] 
    stage4_state_log = [] 

    
    def __init__(self):
        pass
        
    def __init__(self, _time,_temp):
        pass


############################################
###########   PAGES AND GO TO'S  ###########
############################################
combox_General_home = tk.Label()
#page variables
pageNum = 0
def homePage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)

    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Home Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General_home.place(x =0.45*w, y = 0.12*h)	

    #Add job button
    addJob_Button = tk.Button(window, text = "Add Job", width = int(0.015*w), height = int(0.002*h), command = goAddJob, font = ('Helvetica',fontSize))
    addJob_Button.place(x=0.075*w,y=0.1*h)
    
    #View log button
    viewLog_Button = tk.Button(window, text = "View Log", width = int(0.015*w), height = int(0.002*h), command = goViewLog, font = ('Helvetica',fontSize))
    viewLog_Button.place(x=0.075*w,y=0.2*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)

    #Monitors
    kilnInfo = tk.Text(fg = "black", bg = "white", width = int(0.04*w), height = int(0.005*h), font = ('Helvetica',round(fontSize*0.75)))
    kilnInfo.place(x =0.45*w, y = 0.2*h)	
    gsInfo = tk.Text(fg = "black", bg = "white", width = int(0.04*w), height = int(0.025*h), font = ('Helvetica',round(fontSize*0.75)))
    gsInfo.place(x =0.45*w, y = 0.325*h)	


def goHome():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 1
    homePage()


def addJobPage():
    global window, h, w, canvas, queue, pageNum, temp_timeOBJ, temp_tempOBJ, temp_time, temp_temp, job_time_seconds_entry, job_temp_entry
    page = tk.Frame(window)
    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Adding Job", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox.place(x =0.45*w, y = 0.12*h)	

    job_time_seconds_entry = tk.Entry(window, textvariable = temp_timeOBJ, width = int(0.015*w), font = ('Helvetica',fontSize))
    job_temp_entry = tk.Entry(window, textvariable = temp_tempOBJ, width = int(0.015*w), font = ('Helvetica',fontSize))

    job_time_seconds_entry.place(x =0.62*w, y = 0.2*h)
    tsEntry_Label = tk.Label(fg = "black", bg = "white", text = "Job Time (s)", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    tsEntry_Label.place(x =0.45*w, y = 0.2*h)
    
    job_temp_entry.place(x =0.62*w, y = 0.26*h)
    tempEntry_Label = tk.Label(fg = "black", bg = "white", text = "Job Temp (C)", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    tempEntry_Label.place(x =0.45*w, y = 0.26*h)
    
    #Build job button
    buildJob_Button = tk.Button(window, text = "Build Job!", width = int(0.015*w), height = int(0.002*h), command = getJob, font = ('Helvetica',fontSize))
    buildJob_Button.place(x =0.45*w, y = 0.35*h)
    
    #Go home button
    goHome_Button = tk.Button(window, text = "Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)

def getJob():
        global temp_timeOBJ, temp_tempOBJ, temp_time, temp_temp, queue,job_time_seconds_entry,job_temp_entry
        temp_time = job_time_seconds_entry.get()
        temp_temp = job_temp_entry.get()
        if(len(str(temp_time)) != 0 and len(str(temp_temp)) != 0):
            job_time_seconds_entry.delete(0,'end')
            job_temp_entry.delete(0,'end')
            queue.append(job(temp_time, temp_temp))
        else:
            print("No Arguments Passed")
            
        #print(f"Queue Size: {len(queue)}")
        #k = 1
        #for jobs in queue:
        #    print(f"Job {k}: Time: {jobs.time}, Temp: {jobs.temp}\n")
        #    k = k+1
    
                     
def goAddJob():
    global pageNum, window
    print("switched to add job")
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 2
    addJobPage()

def viewLogPage():
    global window, h, w, canvas, queue, pageNum, plot_main
    page = tk.Frame(window)

    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Viewing Log", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General.place(x =0.45*w, y = 0.12*h)	

    #Add job button
    goHome_Button = tk.Button(window, text = "Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)

    # Creates base figure for plotting
    fig = Figure(figsize = (5, 5), dpi = 90) 
    plot_main = fig.add_subplot(111) 

    #generates empty plot
    plot_main.plot(0)
    plot_main.set_title("Current Job Status")
    plot_main.axes.set_ylim(0, 200)
    plot_main.axes.set_xlabel("Time (s)")
    plot_main.axes.set_ylabel("Temperature")
    canvas = FigureCanvasTkAgg(fig, master = window)   
    canvas.draw() 
    canvas.get_tk_widget().place(x = 0.565*w, y = 0.26*h, anchor = "nw")

def goViewLog():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 3
    viewLogPage()
    
#Takes figure, updates figure with new data
def plot(myplot, dat1, dat2):
    global canvas, queue

    desired_temp = [float(queue[0].temp_desired)]*len(dat2)
    myplot.clear()
    myplot.set_title("Job Temperature")
    myplot.axes.set_ylabel("Temperature (C)")
    #myplot.axes.set_ylim(min(dat2), max(dat2))
    if(len(dat2) <= 60):
        myplot.plot(dat1,dat2)
    else:
        myplot.plot(dat1[-60:],dat2[-60:])
        #print(dat1[-60:])
        myplot.axes.set_xlim(dat1[-60], dat1[-1])
    myplot.plot(dat1, desired_temp)
    myplot.legend(["Current Temperature","Desired Temperature"], loc = "upper right")
    canvas.draw()


############################################
##########  FUNCTIONS FOR PROGRAM   ########
############################################    

#Gets time
def timenow():
    return time.perf_counter()

############################################
    
#Exits program upon clicking Exit button
def Exitf():
    #arduino.write(b'0')
    #arduino.close()
    os._exit(0)
    quit()
	
############################################

#Opens arduino and provides info to user
def openArduino():
    global arduino
    print(f"IDLE Awaiting input & Confirmation")
    print("Available ports: \n---------------")
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {}".format(port, desc))
    print('---------------\n')
    print("Please choose COM port for Arduino (i.e. \"COM4\")")
    port = input("Port = ")
    try :
        arduino = serial.Serial(port,9600)
        print(f"Opened port: {arduino.name:s}")
        time.sleep(2)
    except :
        print(f"Could not open \nrequested port ({port:s})")

############################################

#echo info function, for debugging
def echoInfo():
    global arduino
    while(arduino.in_waiting > 0):
        serialString = arduino.readline()
        serialString = serialString.decode('Ascii')
        #print(serialString)
        print(f"Echoed : {serialString:s}")

############################################
        
#Updates the monitor on the home page
def updateMonitor():
    global kilnInfo, gsInfo, queue, inc_time_monitor, pageNum, combox_General_home
    if(timenow() >= inc_time_monitor and pageNum == 1):
        kilnInfo.delete("1.0","end")
        kilnInfo_message = "Station | \tTime Remaining\tTemp. (Act./Des.)\tLast Tumbled\n"
        gsInfo.delete("1.0","end")
        gsInfo_message = "Station | \tTime\tD.Temp\tA.Temp\n"
        k = 1
        jobs = queue[0]
        kiln_temps = jobs.temp_general()
        gs_temps = jobs.temp_general()
        kilnInfo_message = kilnInfo_message+(f"Kiln: {jobs.getStep()}\t{jobs.rem_time}\t{kiln_temps[0]}/{kiln_temps[1]}\t{jobs.cur_cs_humidity}\t{jobs.rec_tumble}\n")
        for jobs in queue:
            gsInfo_message = gsInfo_message+(f"GS: {jobs.getStep()}\t{jobs.getStep()}\t{jobs.getGSTimes()}\t{gs_temps[0]}/{gs_temps[1]}\t{jobs.rec_tumble}\n")
            k = k+1
        kilnInfo.insert("end",kilnInfo_message)
        gsInfo.insert("end",gsInfo_message)
        print(kilnInfo_message)
        print(gsInfo_message)
        inc_time_monitor = timenow()+1
        if(len(queue) >= 1):
            combox_General_home["text"] = f"not empty"
        else:
            combox_General_home["text"] = f"empty"
    else:
        pass
    
############################################

#Checks if something is in the serial bus, if true, then parses it, the first two indices are reserved for the crucial
#Parts of the program, while extra fields are added in order to debug on the arduino and view internal states by following
#the standard formatting
    
def getMessage():
    global arduino, a_read, button_on_board
    while(arduino.in_waiting > 0):
        serialString = arduino.readline()
        serialString = serialString.decode('Ascii')
        parsed_string = serialString.split(" ")
        button_on_board = int(parsed_string[0])
        a_read = float(parsed_string[1])
        #for i in range(len(parsed_string)):
        #    print(parsed_string[i])

############################################

#Builds message, encodes it, and sends it to the arduino
def buildMessage():
    global queue
    if(len(queue) >= 1):
        tmperr = abs(float(queue[0].temp_desired) - float(queue[0].temp_actual))
        MESSAGE = f"{queue[0].time_job},{queue[0].time_remaining},{len(queue)},{tmperr},\n"
        arduino.write(MESSAGE.encode("utf-8"))
    else:
        MESSAGE = f"0,0,0,0,\n"
        arduino.write(MESSAGE.encode("utf-8"))
    #print(MESSAGE)

############################################################
##  STATE TRANSITION FUNCTION AND PROGRAM IMPLEMENTATION  ##
############################################################

############################################
    
##Main loop controlling all the states and tasks
def main():
    #global monitor, queue, inc_time_main, pageNum
    updateMonitor()
    #simulateTemp()
    #processmgr()
    #getMessage()
    pass
############################################
############################################
    
#Starts program
queue = [job(0,0)]
homePage() #Presents Home page
#openArduino() #Opens the arduino
#serialString = arduino.readline() #prevents crash from left over bits in bus
while True:
    main() #main loop
    window.update_idletasks()
    window.update()
