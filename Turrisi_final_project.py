#Raymond Turrisi, 100607022
#Project: Final Project


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
window.title("Turrisi - Final Project")
window.geometry(f'{w}x{h}')

############################################
##############   Variables   ###############
############################################

#Global vars
queue = []
master_time = 0.00000
ogJobTime = 0.0000
reJobTime = 0.0000
ctemp = 0.0000
dtemp = 0.0000
queueSize = 0
heat_rate = 0
cool_rate = 0.5
pageNum = 1

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
monitor = tk.Text()

#Reading from arduino
button_on_board = 0
a_read = 0;

#Timers and global flags
inc_time_monitor = 0.00
ahead_simulator_time = 0
ahead_time_processmgr = 0;
buttonPressFlag = False


#Job class
class job:
    time_job = float(0)
    time_remaining = float(0)
    temp_desired = float(0)
    temp_actual = float(0)
    time_log = []
    temp_log = []
    def __init__(self):
        self.time = 0
        self.temp = 0
        
    def __init__(self, _time,_temp):
        self.time_job = _time
        self.time_remaining = _time
        self.temp_desired = _temp

        
############################################
###########   PAGES AND GO TO'S  ###########
############################################

combox_General_home = tk.Label()

def homePage():
    global h, w, pageNum, window, queue, monitor, combox_General_home
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

    #Monitor
    monitor = tk.Text(fg = "black", bg = "white", width = int(0.03*w), height = int(0.02*h), font = ('Helvetica',fontSize))
    monitor.place(x =0.45*w, y = 0.3*h)	


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
    arduino.close()
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
    global monitor, queue, inc_time_monitor, pageNum, combox_General_home
    if(timenow() >= inc_time_monitor and pageNum == 1):
        monitor.delete("1.0","end")
        monitor_message = "Job\tTime\tD.Temp\tA.Temp\n"
        k = 1
        for jobs in queue:
            monitor_message = monitor_message+(f"{k}\t{jobs.time_remaining}\t{jobs.temp_desired}\t{round(jobs.temp_actual,2)}\n")
            k = k+1
        monitor.insert("end",monitor_message)
        #print(monitor_message)
        inc_time_monitor = timenow()+1
        if(len(queue) >= 1):
            combox_General_home["text"] = f"Heating rate: {round(heat_rate,2)} C/s"
        else:
            combox_General_home["text"] = f"Heating rate: No job processing"
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

############################################
#If button is pressed, pops current job, but also prevents the user from holding down the button and deleting all jobs
def ifButtonIsPressed():
    global button_on_board, buttonPressFlag, queue
    #print(button_on_board)
    if(button_on_board == 0 and not(buttonPressFlag) and (len(queue) > 0)):
        queue.pop(0)
        buttonPressFlag = True
    if(buttonPressFlag and button_on_board == 1):
        buttonPressFlag = False
        
############################################################
##  STATE TRANSITION FUNCTION AND PROGRAM IMPLEMENTATION  ##
############################################################

############################################

#Simulates the temperature of the job and pushes it to the job's log for dynamic plotting
def simulateTemp():
    global queue, cool_rate, heat_rate, ahead_simulator_time, a_read
    if(timenow() >= ahead_simulator_time and (len(queue) >= 1)):
        heat_rate = (float(a_read)/1024)*7
        queue[0].time_log.append(float(queue[0].time_job) - float(queue[0].time_remaining))
        queue[0].temp_log.append(float(queue[0].temp_actual))
        queue[0].time_remaining = float(queue[0].time_remaining) - 1
        queue[0].temp_actual = float(queue[0].temp_actual)+heat_rate-cool_rate
        ahead_simulator_time = timenow()+1
    else:
        #left as safety
        pass

############################################
#Handles arbitrary tasks:
#If there is something in the queue and there is no time remaining, pops job
#If there is a job which can be plotted, plots it
#Every second builds a new message for the arduino
#Checks if button is pressed
    
def processmgr():
    global queue
    if((len(queue) >= 1 and float(queue[0].time_remaining) <= 0)):
        queue[0].temp_log.clear()
        queue[0].time_log.clear()
        queue.pop(0)
    if(len(queue) >= 1 and len(queue[0].time_log) >= 1):
        plot(plot_main, queue[0].time_log, queue[0].temp_log)
    if(timenow() >= ahead_time_processmgr):
        buildMessage()
    ifButtonIsPressed()

############################################
    
##Main loop controlling all the states and tasks
def main():
    global monitor, queue, inc_time_main, pageNum
    updateMonitor()
    simulateTemp()
    processmgr()
    getMessage()
############################################
############################################
    
#Starts program
homePage() #Presents Home page
openArduino() #Opens the arduino
serialString = arduino.readline() #prevents crash from left over bits in bus
while True:
    main() #main loop
    window.update_idletasks()
    window.update()













