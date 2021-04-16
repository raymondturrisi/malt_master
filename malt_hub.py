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
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.009*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.3*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Home Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03918*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General_home.place(x =0.3*w, y = 0.12*h)	

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

    kiln_time_r = tk.Text(fg = "black", bg = "white", width = int(0.0078*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_time_r.place(x =0.3*w, y = 0.325*h)

    kiln_temp = tk.Text(fg = "black", bg = "white", width = int(0.0143*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_temp.place(x =0.395*w, y = 0.325*h)

    kiln_hum = tk.Text(fg = "black", bg = "white", width = int(0.009*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_hum.place(x =0.561*w, y = 0.325*h)

    kiln_tumbled = tk.Text(fg = "black", bg = "white", width = int(0.0148*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    kiln_tumbled.place(x =0.662*w, y = 0.325*h)

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

    germ_step = tk.Text(fg = "black", bg = "white", width = int(0.008*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_step.place(x =0.3*w, y = 0.525*h)

    germ_time_r = tk.Text(fg = "black", bg = "white", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_time_r.place(x =0.39*w, y = 0.525*h)

    germ_temp = tk.Text(fg = "black", bg = "white", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_temp.place(x =0.575*w, y = 0.525*h)

    germ_tumbled = tk.Text(fg = "black", bg = "white", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.75)))
    germ_tumbled.place(x =0.75*w, y = 0.525*h)

def goHome():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 1
    homePage()

def addJobPage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)

    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Add Job Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General_home.place(x =0.45*w, y = 0.12*h)	

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

    kn_time_tmp, kn_temp_tmp, kn_tumbles_tmp, kn_fan_speed_tmp = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()

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
    gs_steep_o2_entryLabel = tk.Label(fg = "black", bg = "white", text = "O2 for steeping (min/hr): ", width = int(0.017*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_steep_o2_entryLabel.place(x =0.35*w, y = 0.6*h)
    gs_steep_o2_entry = tk.Entry(window, textvariable = gs_steep_o2_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_steep_o2_entry.place(x =0.58*w, y = 0.6*h)

    ##Time for Germination
    gs_germ_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for germ. (hrs): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_time_entryLabel.place(x =0.35*w, y = 0.65*h)
    gs_germ_time_entry = tk.Entry(window, textvariable = gs_germ_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_time_entry.place(x =0.58*w, y = 0.65*h)

    ##Water for Germination
    gs_germ_water_entryLabel = tk.Label(fg = "black", bg = "white", text = "Water for germ. (gal): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_water_entryLabel.place(x =0.35*w, y = 0.7*h)
    gs_germ_water_entry = tk.Entry(window, textvariable = gs_germ_water_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_water_entry.place(x =0.58*w, y = 0.7*h)

    ##Tumbling for Germination
    gs_germ_tumble_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbles for germ. (cyc/hr): ", width = int(0.018*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_tumble_entryLabel.place(x =0.35*w, y = 0.75*h)
    gs_germ_tumble_entry = tk.Entry(window, textvariable = gs_germ_tumble_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_tumble_entry.place(x =0.58*w, y = 0.75*h)

    ##O2 for Germination
    gs_germ_o2_entryLabel = tk.Label(fg = "black", bg = "white", text = "O2 for germ. (min/hr): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    gs_germ_o2_entryLabel.place(x =0.35*w, y = 0.8*h)
    gs_germ_o2_entry = tk.Entry(window, textvariable = gs_germ_o2_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    gs_germ_o2_entry.place(x =0.58*w, y = 0.8*h)
    
    #Kiln

    ##Time for kiln
    kn_time_entryLabel = tk.Label(fg = "black", bg = "white", text = "Time for kiln (hrs): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_time_entryLabel.place(x =0.66*w, y = 0.2*h)
    kn_time_entry = tk.Entry(window, textvariable = kn_time_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_time_entry.place(x =0.84*w, y = 0.2*h)

    ##Tumbling for kiln
    kn_temp_entryLabel = tk.Label(fg = "black", bg = "white", text = "Tumbling for kiln (cyc/hr): ", width = int(0.016*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_temp_entryLabel.place(x =0.66*w, y = 0.25*h)
    kn_temp_entry = tk.Entry(window, textvariable = kn_temp_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_temp_entry.place(x =0.84*w, y = 0.25*h)

    ##Temperature for kiln
    kn_tumbles_entryLabel = tk.Label(fg = "black", bg = "white", text = "Temp. for kiln (F): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_tumbles_entryLabel.place(x =0.66*w, y = 0.3*h)
    kn_tumbles_entry = tk.Entry(window, textvariable = kn_tumbles_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_tumbles_entry.place(x =0.84*w, y = 0.3*h)

    ##Fan speed
    kn_fan_speed_entryLabel = tk.Label(fg = "black", bg = "white", text = "Fan speed (0-20): ", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',int(fontSize*0.7)), anchor = "nw")
    kn_fan_speed_entryLabel.place(x =0.66*w, y = 0.35*h)
    kn_fan_speed_entry = tk.Entry(window, textvariable = kn_fan_speed_tmp, width = int(0.007*w), font = ('Helvetica',int(fontSize*0.7)))
    kn_fan_speed_entry.place(x =0.84*w, y = 0.35*h)



    #Exit button binded too escape key (on some computers)
    buildJob_Button = tk.Button(window, text = "Build Job", command = Exitf, font = ('Helvetica',fontSize))
    buildJob_Button.place(x=0.05*w,y=0.85*h)
    buildJob_Button.bind('<Enter>', buildJob)



def goAddJob():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 2
    addJobPage()

def monitorPage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)

    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Monitor Page", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General_home.place(x =0.45*w, y = 0.12*h)	

    #Go Home Button
    goHome_Button = tk.Button(window, text = "Go Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    ExitButton.place(x=0.05*w,y=0.3*h)
    ExitButton.bind('<Escape>', Exitf)	


def goMonitorJob():
    global pageNum, window
    for widget in window.winfo_children():
        widget.destroy()
    pageNum = 3
    monitorPage()

def manControlPage():
    global h, w, pageNum, window, combox_General_home, kilnInfo, gsInfo
    page = tk.Frame(window)

    #communication box title
    combox_title = tk.Label(fg = "black", bg = "white", text = "Notice Box:", width = int(0.015*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_title.place(x =0.45*w, y = 0.05*h)

    #Header
    combox_header = tk.Label(fg = "black", bg = "white", text = "Manual Control", width = int(0.01*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_header.place(x =0.025*w, y = 0.025*h)
    
    #communication box general
    combox_General_home = tk.Label(fg = "black", bg = "white", text = "", width = int(0.03*w), height = int(0.002*h), font = ('Helvetica',fontSize), anchor = "nw")
    combox_General_home.place(x =0.45*w, y = 0.12*h)	

    #Go Home Button
    goHome_Button = tk.Button(window, text = "Go Home", width = int(0.015*w), height = int(0.002*h), command = goHome, font = ('Helvetica',fontSize))
    goHome_Button.place(x=0.075*w,y=0.1*h)
    
    #Exit button binded too escape key (on some computers)
    #ExitButton = tk.Button(window, text = "Exit", command = Exitf, font = ('Helvetica',fontSize))
    #ExitButton.place(x=0.05*w,y=0.3*h)
    #ExitButton.bind('<Escape>', Exitf)


    #Buttons and controls which directly control the states of the embedded devices

    
    ##Enter man mode
    def man_ctl():
        pass

    manMode_label = tk.Label(fg = "black", bg = "white", text = "Manual Mode: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    manMode_label.place(x =0.08*w, y = 0.21*h)

    manMode_button = tk.Button(window, text = "Manual Mode", command = man_ctl, font = ('Helvetica',int(fontSize*0.8)))
    manMode_button.place(x=0.24*w,y=0.20*h)

    ##Purge system
    def purge_ctl():
        pass


    purge_label = tk.Label(fg = "black", bg = "white", text = "Purge: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    purge_label.place(x =0.08*w, y = 0.28*h)

    purge_button = tk.Button(window, text = "fill", command = purge_ctl, font = ('Helvetica',int(fontSize*0.8)))
    purge_button.place(x=0.24*w,y=0.27*h)

    ##Kiln heater
    def kiln_heater_ctl():
        pass

    kiln_heater_label = tk.Label(fg = "black", bg = "white", text = "Kiln Heater: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_heater_label.place(x =0.08*w, y = 0.35*h)

    kiln_heater_button = tk.Button(window, text = "fill", command = kiln_heater_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_heater_button.place(x=0.24*w,y=0.34*h)

    ##Kiln fan

    kiln_fan_slider_label = tk.Label(fg = "black", bg = "white", text = "Kiln fan: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_fan_slider_label.place(x =0.08*w, y = 0.42*h)


    kiln_fan_slider_var = tk.DoubleVar()
    kiln_fan_slider = tk.Scale(window, from_=0, to=255, orient= tk.HORIZONTAL)
    kiln_fan_slider.place(x=0.24*w,y=0.42*h)

    ##Kiln motor
    def kiln_motor_ctl():
        pass

    kiln_motor_label = tk.Label(fg = "black", bg = "white", text = "Kiln motor: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_motor_label.place(x =0.08*w, y = 0.49*h)

    kiln_motor_button = tk.Button(window, text = "fill", command = kiln_motor_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_motor_button.place(x=0.24*w,y=0.48*h)

    ##GS motor
    def gs_motor_ctl():
        pass

    gs_motor_label = tk.Label(fg = "black", bg = "white", text = "GS Motor: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gs_motor_label.place(x =0.08*w, y = 0.56*h)

    gs_motor_button = tk.Button(window, text = "fill", command = gs_motor_ctl, font = ('Helvetica',int(fontSize*0.8)))
    gs_motor_button.place(x=0.24*w,y=0.55*h)

    ##Kiln flap
    def kiln_flap_ctl():
        pass

    kiln_flap_label = tk.Label(fg = "black", bg = "white", text = "Kiln flap: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    kiln_flap_label.place(x =0.08*w, y = 0.63*h)
    kiln_flap_button = tk.Button(window, text = "fill", command = kiln_flap_ctl, font = ('Helvetica',int(fontSize*0.8)))
    kiln_flap_button.place(x=0.24*w,y=0.62*h)


    ##Gate valve
    def gate_ctl():
        pass

    gate_label = tk.Label(fg = "black", bg = "white", text = "Gate valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gate_label.place(x =0.08*w, y = 0.70*h)

    gate_button = tk.Button(window, text = "fill", command = gate_ctl, font = ('Helvetica',int(fontSize*0.8)))
    gate_button.place(x=0.24*w,y=0.69*h)

    ##Germ Jogger
    gj_slider_label = tk.Label(fg = "black", bg = "white", text = "Germ Jogger: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    gj_slider_label.place(x =0.08*w, y = 0.77*h)

    gj_slider_var = tk.DoubleVar()
    gj_slider = tk.Scale(window, from_=0, to=255, orient=tk.HORIZONTAL)
    gj_slider.place(x=0.24*w,y=0.76*h)

    ##o2 valve
    def o2_ctl():
        pass

    o2_label = tk.Label(fg = "black", bg = "white", text = "O2 intake: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    o2_label.place(x =0.08*w, y = 0.85*h)

    o2_button = tk.Button(window, text = "fill", command = o2_ctl, font = ('Helvetica',int(fontSize*0.8)))
    o2_button.place(x=0.24*w,y=0.83*h)

    ##Flood valve
    def fill_ctl():
        pass

    fill_label = tk.Label(fg = "black", bg = "white", text = "Fill valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    fill_label.place(x =0.39*w, y = 0.21*h)

    fill_button = tk.Button(window, text = "fill", command = fill_ctl, font = ('Helvetica',int(fontSize*0.8)))
    fill_button.place(x=0.55*w,y=0.20*h)

    ##Mister
    def mister_ctl():
        pass

    mist_label = tk.Label(fg = "black", bg = "white", text = "Mist valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    mist_label.place(x =0.39*w, y = 0.28*h)

    mist_button = tk.Button(window, text = "fill", command = mister_ctl, font = ('Helvetica',int(fontSize*0.8)))
    mist_button.place(x=0.55*w,y=0.27*h)

    ##Drain
    def drain_ctl():
        pass

    drain_label = tk.Label(fg = "black", bg = "white", text = "Drain valve: ", width = int(0.01*w), font = ('Helvetica',int(fontSize*0.9)), anchor = "nw")
    drain_label.place(x =0.39*w, y = 0.35*h)

    drain_button = tk.Button(window, text = "fill", command = drain_ctl, font = ('Helvetica',int(fontSize*0.8)))
    drain_button.place(x=0.55*w,y=0.34*h)


def goManControl():
    global pageNum, window
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
    
#Exits program upon clicking Exit button
def Exitf():
    #arduino.write(b'0')
    #arduino.close()
    os._exit(0)
    quit()


homePage()
while True:
    #main() #main loop
    window.update_idletasks()
    window.update()