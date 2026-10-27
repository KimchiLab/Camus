"""
Camus: Camera for Mus musculus
Hardware and software for camera video recordings within mouse lab home cages
This script will try to connect to the camera, change settings,
and record video to a sub folder Data in the current project
Make sure you are in the correct working directory
"""

import time
from datetime import datetime
import os.path  # To navigate paths within the OS
import cv2  # OpenCV
from camus_util import get_camera_index, camus_error, check_platform, camus_capture_settings  # Utility file for camus
import ctypes
import argparse
from multiprocessing import Process
from tkinter import *
# import re  # Regular Expressions
# import pandas as pd  # To load csv files using pandas
# from pygrabber.dshow_graph import FilterGraph  # To get Windows DevicePath info for each camera: 

 
### MAIN FUNCTION ###
if __name__ == '__main__':
    check_platform() # Make sure on windows

    # Options via command line interface
    DEFAULT_DURATION_MIN = 60  # Files need to be <2GB. 2hr=120min was approximately 1.5GB, but files a bit slow for processing, so switched to 1hr=60min 2024/01/01
    parser = argparse.ArgumentParser(description = "Camus command line interface")
    parser.add_argument("-d", "--duration_min", type=float, action="store", default=DEFAULT_DURATION_MIN, help = "Duration of each recording file in minutes")
    # parser.add_argument("-s", "--subject", help="Subject Name/ID", action="store", default="")
    # parser.add_argument("-c", "--camera", help="Camera Index", action="store", default=-1, type=int)
    args = parser.parse_args() # Read arguments from command line

    # create root window
    root = Tk()
     
    # root window title and dimension
    root.title("Camus")
    # Set geometry(widthxheight)
    root.geometry('360x240')
     
    # adding a label to the root window
    lbl = Label(root, text = "Subject & Camera ")
    lbl.grid()
     
    # adding Entry Field
    txt_subject = Entry(root, width = 10)
    txt_subject.grid(column = 1, row = 0)
    txt_camera = Entry(root, width = 10)
    txt_camera.grid(column = 2, row = 0)
     
    # function to display user text when 
    # button is clicked
    def clicked():
        str_subject = txt_subject.get()
        str_camera = txt_camera.get()
        res = "Subject " + str_subject + " Camera " + str_camera
        lbl.configure(text = res)
        
        # Screen settings: move window
        # window_name = f"{str_subject}_Cam{str_camera:02d}"
        window_name = f"{str_subject}_Cam{str_camera}"
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(78)  # For windows multi-monitor setups: width, height
        screen_height = user32.GetSystemMetrics(79)  # For windows multi-monitor setups: width, height
        cv2.namedWindow(window_name)  # Create named window
        # window_x = (VID_WIDTH * num_cam_target + 1) % screen_width
        # window_y = (VID_HEIGHT * (num_cam_target // (screen_width // VID_WIDTH)) % screen_height)
        # cv2.moveWindow(window_name, window_x, window_y)
        
     
    # button widget with red color text inside
    btn = Button(root, text = "Add Recording" ,
                 fg = "blue", command=clicked)
    # Set Button Grid
    btn.grid(column = 3, row = 0)
     
    # Execute Tkinter
    root.mainloop()