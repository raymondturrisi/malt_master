############################################
############   Description   ###############
############################################
#This is the code for the User Interface for the Malt Master Prototype for
#URI Mechanical Engineering Capstone Team 20H, written by Raymond Turrisi.


############################################
##############   INCLUDES   ################
############################################

import math as m
import serial
#from serial import Serial
import time as time
import tkinter as tk
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import os
import serial.tools.list_ports
import queue

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
#Job class
class job:
    name = "jobName"
    wash_time = 0
    wash_tumble_frq = 0
    wash_tumble_duration = 0
    wash_water = 0
    wash_cycles = 0
    steep_time = 0
    steep_tumble_frq = 0
    steep_water = 0
    steep_o2 = 0
    germ_time = 0
    germ_mist = 0
    germ_tumble_frq = 0
    germ_o2 = 0
    kiln_time = 0
    kiln_tumble_frq = 0
    kiln_temp = 0
    kiln_fan = 0
    job_rec_frq = float(0)

    c_time = 0
    time_remaining_c_step = 0
    time_remaining_dev = 0
    time_job = 0


    time_log = []
    temp_log = []
    def __init__(self):
        self.time = 0
        self.temp = 0
        
    def __init__(self, jobname, washtime, washtumble, washtumbleduration, washwater, washcycles, steeptime, steeptumble, steepwater, steepo2, germtime, germmist, germtumble, germo2, kilntime, kilntumble, kilntemp, kilnfan, recfrq):
        self.name = jobname
        self.wash_time = washtime
        self.wash_tumble_frq = washtumble
        self.wash_tumble_duration = washtumbleduration
        self.wash_water = washwater
        self.wash_cycles = washcycles
        self.steep_time = steeptime
        self.steep_tumble_frq = steeptumble
        self.steep_water = steepwater
        self.steep_o2 = steepo2
        self.germ_time = germtime
        self.germ_mist = germmist
        self.germ_tumble_frq = germtumble
        self.germ_o2 = germo2
        self.kiln_time = kilntime
        self.kiln_tumble_frq = kilntumble
        self.kiln_temp = kilntemp
        self.kiln_fan = kilnfan
        self.job_rec_frq = recfrq

        self.time_remaining_c_step = washtime
        self.time_remaining_dev = washtime*washcycles+steeptime+germtime
        self.time_job = washtime*washcycles+steeptime+germtime+kilntime

    def save_job():
        #export data as a csv to be opened in sheets software
        pass

queue = [] #max queue size is 1 for now, when the GS is done, the parameters are loaded and the object is destroyed

gs_busy, kiln_busy = 0,0

updateArduino = False
##Input variables

############################################
###########   PAGES AND GO TO'S  ###########
############################################
combox_General_home = tk.Label()
#page variables
pageNum = 0
def homePage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)
    window.configure(bg = "light goldenrod yellow")
    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Home Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.0899*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    combox_General_home.place(x =0.0055*w, y = 0.95*h)	

    #Add job button
    addJob_Button = tk.Button(window, text = "Add Job", width = int(0.015*w), height = int(0.002*h), command = goAddJob, font = ('Helvetica',fontSize))
    addJob_Button.place(x=0.03*w,y=0.1*h)
    
    #View log button
    monitor_Button = tk.Button(window, text = "View Monitor", width = int(0.015*w), height = int(0.002*h), command = goMonitorJob, font = ('Helvetica',fontSize))
    monitor_Button.place(x=0.03*w,y=0.2*h)
    
    #Manual Control button
    manControl_Button = tk.Button(window, text = "Manual Control", width = int(0.015*w), height = int(0.002*h), command = goManControl, font = ('Helvetica',fontSize))
    manControl_Button.place(x=0.03*w,y=0.3*h)

    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.03*w,y=0.4*h)
    ExitButton.bind('<Escape>', Exitf)

    #Monitors

    ##Headers for monitor boxes
    ###Kiln
    kiln_header = tk.Label(fg = "black", bg = "white", text = "Kiln", width = int(0.004*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    kiln_header.place(x =0.3*w, y = 0.2*h)

    kiln_time_r_h = tk.Label(fg = "black", bg = "white", text = "Time Rem.", width = int(0.008*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "n")
    kiln_time_r_h.place(x =0.3*w, y = 0.262*h)

    kiln_temp_h = tk.Label(fg = "black", bg = "white", text = "Temp. F (Act./Des.)", width = int(0.0146*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    kiln_temp_h.place(x =0.395*w, y = 0.262*h)

    kiln_hum_h = tk.Label(fg = "black", bg = "white", text = "Humidity (%)", width = int(0.009*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    kiln_hum_h.place(x =0.561*w, y = 0.262*h)

    kiln_tumbled_h = tk.Label(fg = "black", bg = "white", text = "Tumble (Prev. / Next)", width = int(0.0142*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    kiln_tumbled_h.place(x =0.662*w, y = 0.262*h)

    kiln_time_r_txt = tk.Text(fg = "black", bg = "white", width = int(0.0078*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_time_r_txt.place(x =0.3*w, y = 0.325*h)

    kiln_temp_txt = tk.Text(fg = "black", bg = "white", width = int(0.0143*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_temp_txt.place(x =0.395*w, y = 0.325*h)

    kiln_hum_txt = tk.Text(fg = "black", bg = "white", width = int(0.009*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_hum_txt.place(x =0.561*w, y = 0.325*h)

    kiln_tumbled_txt = tk.Text(fg = "black", bg = "white", width = int(0.0148*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_tumbled_txt.place(x =0.662*w, y = 0.325*h)

    ###GS
    germ_header = tk.Label(fg = "black", bg = "white", text = "Germination Station", width = int(0.0155*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    germ_header.place(x =0.3*w, y = 0.4*h)

    germ_step_h = tk.Label(fg = "black", bg = "white", text = "Step", width = int(0.0075*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    germ_step_h.place(x =0.3*w, y = 0.462*h)

    germ_time_r_h = tk.Label(fg = "black", bg = "white", text = "Time Rem. (Step/NET)", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    germ_time_r_h.place(x =0.39*w, y = 0.462*h)

    germ_temp_h = tk.Label(fg = "black", bg = "white", text = "Temp. F (Act./Des.)", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    germ_temp_h.place(x =0.575*w, y = 0.462*h)

    germ_tumbled_h = tk.Label(fg = "black", bg = "white", text = "Tumble (Prev. / Next)", width = int(0.0158*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    germ_tumbled_h.place(x =0.75*w, y = 0.462*h)

    germ_step_txt = tk.Text(fg = "black", bg = "white", width = int(0.008*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_step_txt.place(x =0.3*w, y = 0.525*h)

    germ_time_r_txt = tk.Text(fg = "black", bg = "white", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_time_r_txt.place(x =0.39*w, y = 0.525*h)

    germ_temp_txt = tk.Text(fg = "black", bg = "white", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_temp_txt.place(x =0.575*w, y = 0.525*h)

    germ_tumbled_txt = tk.Text(fg = "black", bg = "white", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_tumbled_txt.place(x =0.75*w, y = 0.525*h)

def goHome():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 1
    homePage()


def addJobPage():
    global h, w, pageNum, window, combox_General_home, queue
    page = tk.Frame(window)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Add Job Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.0899*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    combox_General_home.place(x =0.0055*w, y = 0.95*h)

    #Go Home Button
    goHome_Button = tk.Button(window, text = "Go Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.05*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)

    #Parameters for building a job, and the awful requirements to do anything in tkinter
    gs_wash_time_tmp, gs_wash_tumble_tmp, gs_wash_tumble_dur_tmp, gs_wash_water_tmp, gs_wash_cycles_tmp = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()
    gs_steep_time_tmp, gs_steep_tumbles_tmp, gs_steep_water_tmp, gs_steep_o2_tmp = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()
    gs_germ_time_tmp, gs_germ_water_tmp, gs_germ_tumble_tmp, gs_germ_o2_tmp = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()

    kn_time_tmp, kn_temp_tmp, kn_tumbles_tmp, kn_fan_speed_tmp, rc_frq_tmp = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()

    name_tmp = tk.StringVar()
    #//In order for process

    #Germination Station

    ##Time for wash
    gs_wash_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for wash (min.): ", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_wash_time_entryLabel.place(x =0.35*w, y = 0.2*h)
    gs_wash_time_entry = tk.Entry(window, textvariable = gs_wash_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_wash_time_entry.place(x =0.58*w, y = 0.2*h)

    ##Tumbling for wash
    gs_wash_tumble_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbles for wash (cyc/hr): ", width = int(0.017*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_wash_tumble_entryLabel.place(x =0.35*w, y = 0.25*h)
    gs_wash_tumble_entry = tk.Entry(window, textvariable = gs_wash_tumble_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_wash_tumble_entry.place(x =0.58*w, y = 0.25*h)
    
    ##Tumble duration for wash
    gs_wash_tumble_dur_entryLabel = tk.Label(fg = "black", bg = "white", text = "Duration of tumble (sec): ", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_wash_tumble_dur_entryLabel.place(x =0.35*w, y = 0.3*h)
    gs_wash_tumble_dur_entry = tk.Entry(window, textvariable = gs_wash_tumble_dur_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_wash_tumble_dur_entry.place(x =0.58*w, y = 0.3*h)

    ##Water for wash
    gs_wash_water_entryLabel = tk.Label(fg = "black", bg = "white", text = "Water for wash (gal): ", width = int(0.014*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_wash_water_entryLabel.place(x =0.35*w, y = 0.35*h)
    gs_wash_water_entry = tk.Entry(window, textvariable = gs_wash_water_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_wash_water_entry.place(x =0.58*w, y = 0.35*h)

    ##Cycles for washing
    gs_wash_cycles_entryLabel = tk.Label(fg = "black", bg = "white", text = "Washing cycles: ", width = int(0.012*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_wash_cycles_entryLabel.place(x =0.35*w, y = 0.4*h)
    gs_wash_cycles_entry = tk.Entry(window, textvariable = gs_wash_cycles_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_wash_cycles_entry.place(x =0.58*w, y = 0.4*h)

    ##Time for steeping
    gs_steep_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for steeping (hrs): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_steep_time_entryLabel.place(x =0.35*w, y = 0.45*h)
    gs_steep_time_entry = tk.Entry(window, textvariable = gs_steep_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_steep_time_entry.place(x =0.58*w, y = 0.45*h)

    ##Tumbling for steeping
    gs_steep_tumbles_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbles for steeping (cyc/hr): ", width = int(0.02*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_steep_tumbles_entryLabel.place(x =0.35*w, y = 0.5*h)
    gs_steep_tumbles_entry = tk.Entry(window, textvariable = gs_steep_tumbles_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_steep_tumbles_entry.place(x =0.58*w, y = 0.5*h)

    ##Water for steeping
    gs_steep_water_entryLabel = tk.Label(fg = "black", bg = "white", text = "Water for steeping (gal): ", width = int(0.017*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_steep_water_entryLabel.place(x =0.35*w, y = 0.55*h)
    gs_steep_water_entry = tk.Entry(window, textvariable = gs_steep_water_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_steep_water_entry.place(x =0.58*w, y = 0.55*h)

    ##O2 for steeping
    gs_steep_o2_entryLabel = tk.Label(fg = "black", bg = "white", text = "O2 for steeping (%): ", width = int(0.017*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_steep_o2_entryLabel.place(x =0.35*w, y = 0.6*h)
    gs_steep_o2_entry = tk.Entry(window, textvariable = gs_steep_o2_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_steep_o2_entry.place(x =0.58*w, y = 0.6*h)

    ##Time for Germination
    gs_germ_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for germ. (hrs): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_time_entryLabel.place(x =0.35*w, y = 0.65*h)
    gs_germ_time_entry = tk.Entry(window, textvariable = gs_germ_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_time_entry.place(x =0.58*w, y = 0.65*h)

    ##Water for Germination
    gs_germ_mist_frq_entryLabel = tk.Label(fg = "black", bg = "white", text = "Misting time (%): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_mist_frq_entryLabel.place(x =0.35*w, y = 0.7*h)
    gs_germ_mist_frq_entry = tk.Entry(window, textvariable = gs_germ_water_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_mist_frq_entry.place(x =0.58*w, y = 0.7*h)

    ##Tumbling for Germination
    gs_germ_tumble_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbles for germ. (cyc/hr): ", width = int(0.018*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_tumble_entryLabel.place(x =0.35*w, y = 0.75*h)
    gs_germ_tumble_entry = tk.Entry(window, textvariable = gs_germ_tumble_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_tumble_entry.place(x =0.58*w, y = 0.75*h)

    ##O2 for Germination
    gs_germ_o2_entryLabel = tk.Label(fg = "black", bg = "white", text = "O2 for germ. (%): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_o2_entryLabel.place(x =0.35*w, y = 0.8*h)
    gs_germ_o2_entry = tk.Entry(window, textvariable = gs_germ_o2_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_o2_entry.place(x =0.58*w, y = 0.8*h)
    
    #Kiln

    ##Time for kiln
    kn_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for kiln (hrs): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_time_entryLabel.place(x =0.66*w, y = 0.2*h)
    kn_time_entry = tk.Entry(window, textvariable = kn_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_time_entry.place(x =0.86*w, y = 0.2*h)

    ##Tumbling for kiln
    kn_temp_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbling for kiln (cyc/hr): ", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_temp_entryLabel.place(x =0.66*w, y = 0.25*h)
    kn_temp_entry = tk.Entry(window, textvariable = kn_temp_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_temp_entry.place(x =0.86*w, y = 0.25*h)

    ##Temperature for kiln
    kn_tumbles_entryLabel = tk.Label(fg = "black", bg = "white", text = "Temp. for kiln (F): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_tumbles_entryLabel.place(x =0.66*w, y = 0.3*h)
    kn_tumbles_entry = tk.Entry(window, textvariable = kn_tumbles_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_tumbles_entry.place(x =0.86*w, y = 0.3*h)

    ##Fan speed
    kn_fan_speed_entryLabel = tk.Label(fg = "black", bg = "white", text = "Fan speed (0-255): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_fan_speed_entryLabel.place(x =0.66*w, y = 0.35*h)
    kn_fan_speed_entry = tk.Entry(window, textvariable = kn_fan_speed_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_fan_speed_entry.place(x =0.86*w, y = 0.35*h)

    ##Recording frequency
    rc_frq_entryLabel = tk.Label(fg = "black", bg = "white", text = "Recording Frequency (min): ", width = int(0.018*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    rc_frq_entryLabel.place(x =0.66*w, y = 0.4*h)
    rc_frq_entry = tk.Entry(window, textvariable = rc_frq_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    rc_frq_entry.place(x =0.86*w, y = 0.4*h)

    ##Recording frequency
    name_entryLabel = tk.Label(fg = "black", bg = "white", text = "Job Name: ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    name_entryLabel.place(x =0.66*w, y = 0.45*h)
    name_entry = tk.Entry(window, textvariable = name_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    name_entry.place(x =0.86*w, y = 0.45*h)

    name_entry.delete(0,'end')
    gs_wash_time_entry.delete(0,'end')
    gs_wash_tumble_entry.delete(0,'end')
    gs_wash_tumble_dur_entry.delete(0,'end')
    gs_wash_water_entry.delete(0,'end')
    gs_wash_cycles_entry.delete(0,'end')
    gs_steep_time_entry.delete(0,'end')
    gs_steep_tumbles_entry.delete(0,'end')
    gs_steep_water_entry.delete(0,'end')
    gs_steep_o2_entry.delete(0,'end')
    gs_germ_time_entry.delete(0,'end')
    gs_germ_mist_frq_entry.delete(0,'end')
    gs_germ_tumble_entry.delete(0,'end')
    gs_germ_o2_entry.delete(0,'end')
    kn_time_entry.delete(0,'end')
    kn_tumbles_entry.delete(0,'end')
    kn_temp_entry.delete(0,'end')
    kn_fan_speed_entry.delete(0,'end')
    rc_frq_entry.delete(0,'end')


    def buildJob():
        global queue, combox_General_home, gs_busy
        try:
            if(not(gs_busy)):
                queue.append(job(name_tmp.get(),gs_wash_time_tmp.get(), gs_wash_tumble_tmp.get(), 
                    gs_wash_tumble_dur_tmp.get(),gs_wash_water_tmp.get(),gs_wash_cycles_tmp.get(),
                    gs_steep_time_tmp.get(), gs_steep_tumbles_tmp.get(), gs_steep_water_tmp.get(), gs_steep_o2_tmp.get(), 
                    gs_germ_time_tmp.get(), gs_germ_water_tmp.get(), gs_germ_tumble_tmp.get(), gs_germ_o2_tmp.get(), 
                    kn_time_tmp.get(), kn_tumbles_tmp.get(),kn_temp_tmp.get(), kn_fan_speed_tmp.get(), rc_frq_tmp.get()))
            else:
                 print("GS is busy and new job cannot be loaded right now")

        except ValueError:
            print("There is a problem with one of your inputs, everything must be whole integers")
            pass
        else:
            #print("There is an unaccounted for problem, goodluck..")
            pass

        name_entry.delete(0,'end')
        gs_wash_time_entry.delete(0,'end')
        gs_wash_tumble_entry.delete(0,'end')
        gs_wash_tumble_dur_entry.delete(0,'end')
        gs_wash_water_entry.delete(0,'end')
        gs_wash_cycles_entry.delete(0,'end')
        gs_steep_time_entry.delete(0,'end')
        gs_steep_tumbles_entry.delete(0,'end')
        gs_steep_water_entry.delete(0,'end')
        gs_steep_o2_entry.delete(0,'end')
        gs_germ_time_entry.delete(0,'end')
        gs_germ_mist_frq_entry.delete(0,'end')
        gs_germ_tumble_entry.delete(0,'end')
        gs_germ_o2_entry.delete(0,'end')
        kn_time_entry.delete(0,'end')
        kn_tumbles_entry.delete(0,'end')
        kn_temp_entry.delete(0,'end')
        kn_fan_speed_entry.delete(0,'end')
        rc_frq_entry.delete(0,'end')
        print(queue[0].name)

    #Exit button binded too escape key (on some computers)
    buildJob_Button = tk.Button(window, text = "Start Job", command = buildJob, font = ('Helvetica',fontSize))
    buildJob_Button.place(x=0.05*w,y=0.85*h)

def goAddJob():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 2
    addJobPage()

def monitorPage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Monitor Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.0899*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    combox_General_home.place(x =0.0055*w, y = 0.95*h)	

    #Go Home Button
    goHome_Button = tk.Button(window, text = "Go Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)

    # Creates base figure for plotting
    fig = Figure(figsize = (6, 6), dpi = 100, tight_layout=True) 
    plot_gs_temp = fig.add_subplot(221)
    plot_gs_wl = fig.add_subplot(222) 
    plot_k_temp = fig.add_subplot(223)
    plot_k_hum = fig.add_subplot(224)  

    #generates empty plot
    plot_gs_temp.plot(0)
    plot_gs_wl.plot(0)
    plot_k_temp.plot(0)
    plot_k_hum.plot(0)

    plot_gs_temp.set_title("GS Temperature")
    plot_gs_wl.set_title("GS Water Level")
    plot_k_temp.set_title("Kiln Temperature")
    plot_k_hum.set_title("Kiln Humidity")

    plot_gs_temp.axes.set_ylim(0, 150)
    plot_gs_wl.axes.set_ylim(0, 40)
    plot_k_temp.axes.set_ylim(0, 150)
    plot_k_hum.axes.set_ylim(0, 110)

    plot_gs_temp.axes.set_xlabel("Time (s)")
    plot_gs_wl.axes.set_xlabel("Time (s)")
    plot_k_temp.axes.set_xlabel("Time (s)")
    plot_k_hum.axes.set_xlabel("Time (s)")

    plot_gs_temp.axes.set_ylabel("Temperature (F)")
    plot_gs_wl.axes.set_ylabel("Gallons")
    plot_k_temp.axes.set_ylabel("Temperature (F)")
    plot_k_hum.axes.set_ylabel("Humidity (%)")

    canvas = FigureCanvasTkAgg(fig, master = window)   
    canvas.draw() 
    canvas.get_tk_widget().place(x = 0.4*w, y = 0.05*h, anchor = "nw")

def plot(myplot, gs_temp_series, gs_wl_series, k_temp_series, k_hum_series):
    global canvas

    myplot.clear()
    myplot.set_title("Job Temperature")
    myplot.axes.set_ylabel("Temperature (C)")
    #myplot.axes.set_ylim(min(dat2), max(dat2))
    if(len(dat2) <= 60):
        myplot.plot(dat1,dat2)
    else:
        myplot.plot(dat1[-60:],dat2[-60:])
        myplot.axes.set_xlim(dat1[-60], dat1[-1])
    myplot.plot(dat1, desired_temp)
    myplot.legend(["Current Temperature","Desired Temperature"], loc = "upper right")
    canvas.draw()


def goMonitorJob():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 3
    monitorPage()

#mode of system
mode = 0 # 0 = normal operation, 1 = manual control, 2 = purging

#variables
k_heating, k_fan, k_motor = 0, 0, 0 # 0 or 1, 0 - 255, 0 or 1 respectively
gs_motor, k_flap, gate_valve, g_jogger = 0, 0, 0, 0 # 0 or 1, 0 or 1, 0 or 1, 0-255
o2_valve, filling, misting, draining, filtering = 0, 0, 0, 0, 0 # 0 or 1, 0 or 1, 0 or 1, 0 or 1

def manControlPage():
    global h, w, pageNum, window, combox_General_home, updateArduino
    global mode, manMode_button, purge_button, kiln_heater_button, kiln_motor_button, filter_button

    global gs_motor_button, kiln_flap_button, o2_button
    global fill_button, gate_button, mist_button, drain_button
    global k_heating, k_fan, k_motor
    global gs_motor, k_flap, gate_valve, g_jogger
    global o2_valve, filling, misting, draining, filtering


    page = tk.Frame(window)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Manual Control", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.0899*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)), anchor = "nw")
    combox_General_home.place(x =0.0055*w, y = 0.95*h)	

    #Go Home Button
    goHome_Button = tk.Button(window, text = "Go Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    #ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    #ExitButton.place(x=0.05*w,y=0.3*h)
    #ExitButton.bind('<Escape>', Exitf)


    #Buttons and controls which directly control the states of the embedded devices

    manMode_button = tk.Button()

    ###Manual mode sequence
    def man_ctl():
        global mode, manMode_button
        updateArduino = True
        if(mode == 0):
            mode = 1
            manMode_button.configure(text="True")
        elif(mode == 1):
            mode = 0
            manMode_button.configure(text="False")
        print(f"Mode: {mode}")

    manMode_label = tk.Label(fg = "black", bg = "white", text = "Manual Mode: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    manMode_label.place(x =0.08*w, y = 0.21*h)

    manMode_button = tk.Button(window, text = "False",command = man_ctl, font = ('Helvetica',int(fontSize*0.8)))
    manMode_button.place(x=0.24*w,y=0.20*h)

    

    ##Purge system objects
    purge_button = tk.Button()
    def purge_ctl():
        global mode, purge_button
        if(True):
            mode = 2
            manMode_button.configure(text="NA")
            purge_button.configure(text="Purging..")
        print(f"Mode: {mode}")
        ##change mode to 3, block interaction with all objects, insantiate sequence to purge system, update combox with steps (must be done in state transition structure)
        pass

    purge_label = tk.Label(fg = "black", bg = "white", text = "Purge: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    purge_label.place(x =0.08*w, y = 0.28*h)

    purge_button = tk.Button(window, text = ("Purging.." if mode == 2 else "--"), command = purge_ctl, font = ('Helvetica',int(fontSize*0.8)))
    purge_button.place(x=0.24*w,y=0.27*h)

    ##Kiln heater objects
    kiln_heater_button = tk.Button()

    def kiln_heater_ctl():
        #changes kiln heater variable, only when in manual mode
        global mode, k_heating, kiln_heater_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(k_heating == 0):
                k_heating = 1
                kiln_heater_button.configure(text="On")
            elif(k_heating == 1):
                k_heating = 0
                kiln_heater_button.configure(text="Off")
            print(f"Kiln heating: {k_heating}")
        else:
            print(f"Kiln heating: {k_heating}")

    kiln_heater_label = tk.Label(fg = "black", bg = "white", text = "Kiln Heater: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_heater_label.place(x =0.08*w, y = 0.35*h)

    kiln_heater_button = tk.Button(window, text = ("On" if k_heating else "Off"), command = kiln_heater_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_heater_button.place(x=0.24*w,y=0.34*h)

    ##Kiln fan
    def kf_ctl():
        #changes gate valve variable, only when in manual mode
        global mode, k_fan, kiln_fan_button, updateArduino
        updateArduino = True
        if(mode == 1):
            k_fan = kiln_fan_slider.get()
            print(f"Kiln Fan: {k_fan}")
        else:
            print(f"Kiln Fan: {k_fan}")

    kiln_fan_slider_label = tk.Label(fg = "black", bg = "white", text = "Kiln fan: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_fan_slider_label.place(x =0.08*w, y = 0.42*h)

    kiln_fan_slider_var = tk.DoubleVar()
    kiln_fan_slider = tk.Scale(window, from_=0, to=255, orient= tk.HORIZONTAL)
    kiln_fan_slider.place(x=0.3*w,y=0.41*h)

    kiln_fan_button = tk.Button(window, text = "Push", command = kf_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_fan_button.place(x=0.24*w,y=0.41*h)

    ##Kiln motor
    kiln_motor_button = tk.Button()

    def kiln_motor_ctl():
        #changes kiln motor variable, only when in manual mode
        global mode, k_motor, kiln_motor_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(k_motor == 0):
                k_motor = 1
                kiln_motor_button.configure(text="On")
            elif(k_motor == 1):
                k_motor = 0
                kiln_motor_button.configure(text="Off")
            print(f"Kiln motor: {k_motor}")
        else:
            print(f"Kiln motor: {k_motor}")

    kiln_motor_label = tk.Label(fg = "black", bg = "white", text = "Kiln motor: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_motor_label.place(x =0.08*w, y = 0.49*h)

    kiln_motor_button = tk.Button(window, text = ("On" if k_motor else "Off"), command = kiln_motor_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_motor_button.place(x=0.24*w,y=0.48*h)

    ##GS motor
    def gs_motor_ctl():
        #changes gs motor variable, only when in manual mode
        global mode, gs_motor, gs_motor_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(gs_motor == 0):
                gs_motor = 1
                gs_motor_button.configure(text="On")
            elif(gs_motor == 1):
                gs_motor = 0
                gs_motor_button.configure(text="Off")
            print(f"GS motor: {gs_motor}")
        else:
            print(f"GS motor: {gs_motor}")

    gs_motor_label = tk.Label(fg = "black", bg = "white", text = "GS Motor: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gs_motor_label.place(x =0.08*w, y = 0.56*h)

    gs_motor_button = tk.Button(window, text = ("On" if gs_motor else "Off"), command = gs_motor_ctl, font = ('Helvetica',int(fontSize*0.8)))
    gs_motor_button.place(x=0.24*w,y=0.55*h)

    ##Kiln flap
    kiln_flap_button = tk.Button()
    def kiln_flap_ctl():
        #changes kiln flap variable, only when in manual mode
        global mode, k_flap, kiln_flap_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(k_flap == 0):
                k_flap = 1
                kiln_flap_button.configure(text="Open")
            elif(k_flap == 1):
                k_flap = 0
                kiln_flap_button.configure(text="Closed")
            print(f"Kiln flap: {k_flap}")
        else:
            print(f"Kiln flap: {k_flap}")

    kiln_flap_label = tk.Label(fg = "black", bg = "white", text = "Kiln flap: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_flap_label.place(x =0.08*w, y = 0.63*h)
    kiln_flap_button = tk.Button(window, text = ("Open" if k_flap else "Closed"), command = kiln_flap_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_flap_button.place(x=0.24*w,y=0.62*h)


    ##Gate valve
    def gate_ctl():
        #changes gate valve variable, only when in manual mode
        global mode, gate_valve, gate_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(gate_valve == 0):
                gate_valve = 1
                gate_button.configure(text="Open")
            elif(gate_valve == 1):
                gate_valve = 0
                gate_button.configure(text="Closed")
            print(f"Gate valve: {gate_valve}")
        else:
            print(f"Gate valve: {gate_valve}")

    gate_label = tk.Label(fg = "black", bg = "white", text = "Gate valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gate_label.place(x =0.08*w, y = 0.70*h)

    gate_button = tk.Button(window, text = ("Open" if gate_valve else "Closed"), command = gate_ctl, font = ('Helvetica',int(fontSize*0.8)))
    gate_button.place(x=0.24*w,y=0.69*h)

    ##Germ Jogger

    def gj_ctl():
        #changes gate valve variable, only when in manual mode
        global mode, g_jogger, gj_button, updateArduino
        updateArduino = True
        if(mode == 1):
            g_jogger = gj_slider.get()
            print(f"GJ: {g_jogger}")
        else:
            print(f"GJ: {g_jogger}")

    gj_slider_label = tk.Label(fg = "black", bg = "white", text = "Germ Jogger: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gj_slider_label.place(x =0.08*w, y = 0.77*h)

    gj_slider_var = tk.DoubleVar()
    gj_slider = tk.Scale(window, from_=0, to=255, orient=tk.HORIZONTAL)
    gj_slider.place(x=0.3*w,y=0.76*h)

    gj_button = tk.Button(window, text = "Push", command = gj_ctl, font = ('Helvetica',int(fontSize*0.8)))
    gj_button.place(x=0.24*w,y=0.76*h)


    ##o2 valve
    def o2_ctl():
        global mode, o2_valve, o2_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(o2_valve == 0):
                o2_valve = 1
                o2_button.configure(text="Open")
            elif(o2_valve == 1):
                o2_valve = 0
                o2_button.configure(text="Closed")
            print(f"O2 valve: {o2_valve}")
        else:
            print(f"O2 valve: {o2_valve}")

    o2_label = tk.Label(fg = "black", bg = "white", text = "O2 intake: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    o2_label.place(x =0.08*w, y = 0.85*h)

    o2_button = tk.Button(window, text = ("Open" if o2_valve else "Closed"), command = o2_ctl, font = ('Helvetica',int(fontSize*0.8)))
    o2_button.place(x=0.24*w,y=0.83*h)

    ##Flood valve
    def fill_ctl():
        #changes fill valve variable, only when in manual mode
        global mode, filling, fill_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(filling == 0):
                filling = 1
                fill_button.configure(text="Open")
            elif(filling == 1):
                filling = 0
                fill_button.configure(text="Closed")
            print(f"Filling: {filling}")
        else:
            print(f"Filling: {filling}")

    fill_label = tk.Label(fg = "black", bg = "white", text = "Fill valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    fill_label.place(x =0.39*w, y = 0.21*h)

    fill_button = tk.Button(window, text = ("Open" if filling else "Closed"), command = fill_ctl, font = ('Helvetica',int(fontSize*0.8)))
    fill_button.place(x=0.55*w,y=0.20*h)

    ##Mister
    def mister_ctl():
        global mode, misting, mist_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(misting == 0):
                misting = 1
                mist_button.configure(text="Open")
            elif(misting == 1):
                misting = 0
                mist_button.configure(text="Closed")
            print(f"Misting: {misting}")
        else:
            print(f"Misting: {misting}")

    mist_label = tk.Label(fg = "black", bg = "white", text = "Mist valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    mist_label.place(x =0.39*w, y = 0.28*h)

    mist_button = tk.Button(window, text = ("Open" if misting else "Closed"), command = mister_ctl, font = ('Helvetica',int(fontSize*0.8)))
    mist_button.place(x=0.55*w,y=0.27*h)

    ##Drain
    def drain_ctl():
        #changes drain valve variable, only when in manual mode
        global mode, draining, drain_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(draining == 0):
                draining = 1
                drain_button.configure(text="Open")
            elif(draining == 1):
                draining = 0
                drain_button.configure(text="Closed")
            print(f"Draining: {draining}")
        else:
            print(f"Draining: {draining}")

    drain_label = tk.Label(fg = "black", bg = "white", text = "Drain valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    drain_label.place(x =0.39*w, y = 0.35*h)

    drain_button = tk.Button(window, text = ("Open" if draining else "Closed"), command = drain_ctl, font = ('Helvetica',int(fontSize*0.8)))
    drain_button.place(x=0.55*w,y=0.34*h)

    ##Filter
    def filter_ctl():
        #changes filter variable, only when in manual mode
        global mode, filtering, filter_button, updateArduino
        updateArduino = True
        if(mode == 1):
            if(filtering == 0):
                filtering = 1
                filter_button.configure(text="On")
            elif(filtering == 1):
                filtering = 0
                filter_button.configure(text="Off")
            print(f"Filtering: {filtering}")
        else:
            print(f"Filtering: {filtering}")

    filter_label = tk.Label(fg = "black", bg = "white", text = "Filter: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    filter_label.place(x =0.39*w, y = 0.42*h)

    filter_button = tk.Button(window, text = ("On" if filtering else "Off"), command = filter_ctl, font = ('Helvetica',int(fontSize*0.8)))
    filter_button.place(x=0.55*w,y=0.41*h)

def goManControl():
    global pageNum, window
    updateArduino = True
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 4
    manControlPage()


############################################
##########  FUNCTIONS FOR PROGRAM   ########
############################################ 

#Gets time
def timenow():
    return time.perf_counter()

############################################
arduino = serial.Serial()


#Exits program upon clicking Exit button
def Exitf():
    #arduino.write(b'0')
    #arduino.close()
    os._exit(0)
    quit()

#Opens arduino and provides info to user
def openArduino():
    global arduino
    print(f"IDLE Awaiting input & Confirmation")
    print("Available ports: \n---------------")
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {}".format(port, desc))
    print('---------------\n')
    #print("Please choose COM port for Arduino (i.e. \"COM4\")")
    #port = input("Port = ")
    try :
        arduino = serial.Serial("/dev/ttyACM0",115200)
        print(f"Opened port: {arduino.name:s}")
        time.sleep(2)
    except :
        pass
        #print(f"Could not open \nrequested port ({port:s})")

def updatePlots():
    pass

def updateMonitor():
    global wash_sequence, steep_sequence, germ_sequence, kiln_sequence, combox_General_home
    if(wash_sequence):
        combox_General_home.configure(text="Washing Grain")
    elif(steep_sequence):
        combox_General_home.configure(text="Steeping Grain")
    elif(germ_sequence):
        combox_General_home.configure(text="Germinating Grain")
    elif(kiln_sequence):
        combox_General_home.configure(text="Drying Grain")
    else:
        combox_General_home.configure(text="System Ready")
    pass

def buildMessage():
    global updateArduino
    if(updateArduino):
        message = f"{k_heating},{k_fan},{k_motor},{gs_motor},{k_flap},{gate_valve},{g_jogger},{o2_valve},{filling},{misting},{draining},{filtering}\n"
        #arduino.write(message.encode("utf-8"))
        print(message.encode("utf-8"))
        updateArduino = False

m_type, k_temp_now, k_hum_now, gs_temp_now, gs_wh_now, gs_wl_now = 0,0,0,0,0,0

def wh2wl(dist2top):
    #piece wise function for curvature of silo
    #linear at the top half
    #sloped at the bottom half, gauged from physical measurements
    height = 50
    corner = 35 #cm, need to update constant
    if(dist2top <= corner):
        return ((corner-dist2top)*(0.5)+15) #gallons, need to update constant (volume per cm)
    else:
        return (1/3)*(3.145)*(0.57735)*(height-(dist2top-corner))^3 #gallons, need to update constants, volume of cone


def getMessage():
    #type, ktemp, khum, gstemp, gswl
    global arduino, m_type, k_temp_now, k_hum_now, gs_temp_now, gs_wl_now
    while(arduino.in_waiting > 0):
        serialString = arduino.readline()
        serialString = serialString.decode('Ascii')
        #print(serialString)
        #parsed_string = serialString.split(",")
        #m_type = int(parsed_string[0])
        #k_temp_now = float(parsed_string[1])
        #k_hum_now = float(parsed_string[2])
        #gs_temp_now = float(parsed_string[3])
        #gs_wh_now = float(parsed_string[4])
        #gs_wl_now = wh2wl(gs_hl_now)

        #for i in range(len(parsed_string)):
            #print(parsed_string[i])


current_job = job("arb", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
c_step_time_r = 0
gs_busy, wash_sequence, steep_sequence, germ_sequence = False, False, False, False
steeping, steep_1, steep_2, steep_3 = False, False, False, False
germ_1, germ_2, germ_3 = False, False, False
kiln_1, kiln_2, kiln_3 = False, False, False
gj_1, gj_2 = False, False
gj_sequence, kiln_sequence, entry_flagged, first_mix, gs_mixing = False,False,False,False, False
gs_start_time, fill_start_time, first_mix_time, gj_start_time, kiln_start_time, last_mix, drain_start, next_o2_release = 0,0,0,0,0,0,0,0
o2_interval, o2_duration, next_o2_release, o2_opened_at = 0.00, 0.00, 0.00, 0.00
steep_start_time = 0

def stateManagement():
    global current_job, queue
    global steeping, steep_1, steep_2, steep_3, steep_start_time
    global germ_1, germ_2, germ_3
    global kiln_1, kiln_2, kiln_3
    global gj_1, gj_2, gj_start_time
    global gs_busy, wash_sequence, steep_sequence, germ_sequence
    global gs_start_time, fill_start_time, first_mix_time, kiln_start_time, last_mix, drain_start, next_o2_release
    global updateArduino, gs_wl_now
    global gj_sequence, kiln_sequence, entry_flagged, first_mix, gs_mixing
    global o2_interval, o2_duration, next_o2_release, o2_opened_at

    global k_heating, k_fan, k_motor
    global gs_motor, k_flap, gate_valve, g_jogger
    global o2_valve, filling, misting, draining, filtering
    #if not purging, system is doing nothing, or processing job (mode == 1)
        #if a job is received, start process, gs is busy
    if(mode == 0):
        #update buttons, combox, etc
        #start wash sequence if there is a job and there are no problems
        if(len(queue) == 1 and not(gs_busy)):
            current_job = queue.pop(0)
            gs_busy = True
            wash_sequence = True
            gs_start_time = timenow()
            print("started")
        if(wash_sequence):
            if(current_job.wash_cycles > 0):
                #fill with water until water level is reached, or a time has allotted (safety)
                if(not(filling) and not(entry_flagged)):
                    fill_start_time = timenow()
                    filling = 1
                    updateArduino = True 
                    entry_flagged = True
                    print(f"filling {timenow()}")
                    print(current_job.wash_cycles)
                if(filling):
                    gs_wl_now = 25 #delete
                    if(timenow() >= (fill_start_time + 5)):
                        filling = 0 
                        gs_mixing = True
                        updateArduino = True 
                        first_mix = True
                        print(f"not filling {timenow()}")
                #when water is filled, stir for n time in one minute intervals (save the motor), filter is on
                if(gs_mixing):
                    if(first_mix):
                        last_mix = timenow()
                        first_mix = False 
                        first_mix_time = timenow()
                        gs_motor = 1
                        filtering = 1
                        updateArduino = True
                        print(f"first mix {timenow()}")
                    if(not(first_mix)):
                        if(last_mix + 5 <= timenow()):
                            if(gs_motor):
                                gs_motor = 0
                            else:
                                gs_motor = 1
                            last_mix = timenow()
                            updateArduino = True
                            print(f"mixing {timenow()}")
                    if(current_job.wash_time*1 <= (timenow()-first_mix_time)):
                        #oh the pain of non-blocking code
                        draining = 1
                        gs_motor = 1
                        last_mix = 0
                        filtering = 0
                        first_mix = True
                        gs_mixing = False 
                        updateArduino = True
                        drain_start = timenow()
                        print(f"wash done {timenow()}")
                #when n time is reached, filter is off, system is draining and mixing
                
                if(draining and (drain_start + 5) <= timenow()):
                    draining = 0
                    gs_motor = 0
                    current_job.wash_cycles = current_job.wash_cycles - 1
                    updateArduino = True
                    entry_flagged = False
                    print(f"drained {timenow()}")
                    print(current_job.wash_cycles)
                    #when system is drained (initial height pm 5 cm), repeats the above step for c cycles
            else:
                print(f"washing done {timenow()}")
                wash_sequence = False
                steep_sequence = True
                steep_1 = True
                entry_flagged = False

        #start steep sequence
            #steeps for n time, agitating periodically, adding o2 periodically
        if(steep_sequence):
            ##starting the steep sequence
            if(steep_1):
                if(not(filling) and not(entry_flagged) and not(steeping)):
                        fill_start_time = timenow()
                        filling = 1
                        updateArduino = True 
                        entry_flagged = True
                        print(f"filling {timenow()}")
                ##filling 
                if(filling):
                    if(timenow() >= (fill_start_time + 5)):
                        filling = 0 
                        steeping = True
                        updateArduino = True 
                        print(f"not filling {timenow()}")
                ##steeping
                if(steeping and entry_flagged):
                    steep_start_time = timenow()
                    next_o2_release = timenow()
                    o2_interval = current_job.steep_time*(current_job.steep_o2/100)
                    o2_duration = o2_interval*current_job.steep_o2/100
                    entry_flagged = False
                    steep_1 = False
                    steep_2 = True
                    print(f"start steeping {timenow()}")
                    print(f"{o2_interval}")
                    print(f"{o2_duration}")

            if(steep_2):
                ##periodically releasing o2

                if(next_o2_release <= timenow()):
                    o2_opened_at = timenow()
                    o2_valve = 1
                    next_o2_release = next_o2_release+o2_interval
                    updateArduino = True
                    print(f"opened {timenow()}")
                if(o2_opened_at + o2_duration <= timenow() and o2_valve == 1):
                    print(f"closed {timenow()}")
                    o2_valve = 0
                    updateArduino = True

                ##periodically mixing
                if(last_mix + 5 <= timenow()):
                    if(gs_motor):
                        gs_motor = 0
                    else:
                        gs_motor = 1
                    last_mix = timenow()
                    updateArduino = True
                    print(f"mixing {timenow()}")

                ##ending statement
                if(current_job.steep_time*1*1 <= timenow() - steep_start_time):
                    steeping = False
                    entry_flagged = True
                    o2_valve = 0
                    draining = 1
                    gs_motor = 1
                    drain_start = timenow() 
                    print(f"draining {timenow()}")
                    updateArduino = True
                    steep_2 = False
                    steep_3 = True

            if(steep_3):
                #done steeping
                if(draining and (drain_start + 5) <= timenow()):
                    draining = 0
                    gs_motor = 0
                    updateArduino = True
                    steep_3 = False
                    entry_flagged = False
                    germ_1 = True
                    steep_sequence = False
                    germ_sequence = True
                    print(f"drained {timenow()}")
                    

        #start germinating sequence
            #germing for n time
                #mist periodically
                #tumble periodically
        if(germ_sequence):
            ##starting the steep sequence
            if(germ_1):
                germ_start_time = timenow()

                next_o2_release = timenow()
                o2_interval = current_job.germ_time*(current_job.germ_o2/100)
                o2_duration = o2_interval*current_job.germ_o2/100
                next_mist_release = timenow()
                mist_interval = current_job.germ_time*(current_job.germ_mist/100)
                mist_duration = mist_interval*current_job.germ_mist/100

                entry_flagged = False
                germ_1 = False
                germ_2 = True
                print(f"start germinating {timenow()}")
                #print(f"{o2_interval}")
                #print(f"{o2_duration}")
                #print(f"{mist_interval}")
                #print(f"{mist_duration}")

            if(germ_2):
                ##periodically releasing o2

                if(next_o2_release <= timenow()):
                    o2_opened_at = timenow()
                    o2_valve = 1
                    next_o2_release = next_o2_release+o2_interval
                    updateArduino = True
                    print(f"o2 opened {timenow()}")
                if(o2_opened_at + o2_duration <= timenow() and o2_valve == 1):
                    print(f"o2 closed {timenow()}")
                    o2_valve = 0
                    updateArduino = True

                ##periodically misting
                if(next_o2_release <= timenow()):
                    o2_opened_at = timenow()
                    o2_valve = 1
                    next_o2_release = next_o2_release+o2_interval
                    updateArduino = True
                    print(f"mister opened {timenow()}")
                if(o2_opened_at + o2_duration <= timenow() and o2_valve == 1):
                    print(f"mister closed {timenow()}")
                    o2_valve = 0
                    updateArduino = True


                ##periodically mixing
                if(last_mix + 5 <= timenow()):
                    if(gs_motor):
                        gs_motor = 0
                    else:
                        gs_motor = 1
                    last_mix = timenow()
                    updateArduino = True
                    print(f"mixing {timenow()}")

                ##ending statement
                if(current_job.germ_time*1*1 <= timenow() - steep_start_time):
                    o2_valve = 0
                    gs_motor = 1
                    drain_start = timenow() 
                    print(f"last tumbling {timenow()}")
                    updateArduino = True
                    germ_2 = False
                    germ_3 = True
                    last_mix = timenow()

            if(germ_3):
                #done germing
                if(timenow() >= last_mix + 5):
                    gs_motor = 0
                    updateArduino = True
                    gj_1 = True
                    germ_3 = False
                    germ_sequence = False
                    gj_sequence = True
                    print(f"done germing {timenow()}")
                    
        #transport grain for (2 minutes?)
            #gs is not busy
        if(gj_sequence):
            if(gj_1):
                #setup this mode
                gj_start_time = timenow()
                g_jogger = 255
                gate_valve = 1
                gs_motor = 1
                k_motor = 1
                updateArduino = True
                gj_1 = False
                gj_2 = True
                print(f"beginning grain transport {timenow()}")
            if(gj_2):
                #transport the grain while spinning the kiln motor
                if(timenow() >= gj_start_time + 5):
                    g_jogger = 0
                    gate_valve = 0
                    gs_motor = 0
                    k_motor = 0
                    updateArduino = True
                    gj_2 = False
                    kiln_1 = True
                    gj_sequence = False
                    kiln_sequence = True
                    print(f"done transporting {timenow()}")
        #start kiln process
            #kilns for n time, with heating element on when temperature is not at desired temperature, with fan at set fan speed
                #heater turns off if temperature is not met within 30 minutes, defaulting to 100 degrees and 40 pwm fan speed
            #finish kilning
        if(kiln_sequence):
            #throw heaters
            if(kiln_1):
                kiln_start_time = timenow()
                last_mix = timenow()
                gs_busy = False
                k_fan = current_job.kiln_fan
                k_heating = 1
                kiln_1 = False 
                kiln_2 = True
                updateArduino = True 
                print(f"starting kiln process {timenow()}")
            #mix periodically
            if(kiln_2):
                if(k_motor == 0 and timenow() >= last_mix + 4):
                    last_mix = timenow()
                    k_motor = 1
                    updateArduino = True
                    print(f"mixing on {timenow()}")

                if(k_motor == 1 and timenow() >= last_mix + 4):
                    last_mix = timenow()
                    k_motor = 0
                    updateArduino = True
                    print(f"mixing off {timenow()}")

                #exit code: push grain out
                if(current_job.kiln_time*1 <= timenow()-kiln_start_time):
                    last_mix = timenow()
                    k_fan = 0
                    k_heating = 0
                    k_motor = 1
                    k_flap = 1
                    updateArduino = True
                    kiln_2 = False 
                    kiln_3 = True
                    print(f"finished kilning {timenow()}")
            #once grain is assumed to have been gone, clode kiln and reset
            if(kiln_3):
                if(timenow() >= last_mix + 5):
                    k_motor = 0
                    k_flap = 0
                    updateArduino = True
                    kiln_3 = False
                    kiln_sequence = False
                    print(f"kiln reset {timenow()}")

    #if purging, purge
        pass
    if(mode == 2):
        #purge sequence
        pass
    pass

def main():
    global queue, kiln_1, kiln_2, kiln_3, kiln_sequence, last_mix
    #print(f"kiln states {kiln_1} {kiln_2} {kiln_3} {kiln_sequence} {timenow()} {last_mix}")
    #updating plots
    updatePlots()
    updateMonitor()

    #building messages if arduino needs to be updated
    buildMessage()

    #reading messages from arduino if they're in line, updating variables
    #getMessage()

    #state_management
    stateManagement()

homePage()
#openArduino() #Opens the arduino
#serialString = arduino.readline() #prevents crash from left over bits in bus
while True:
    main() #main loop
    #print(updateArduino)
    window.update_idletasks()
    window.update()