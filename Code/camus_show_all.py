"""
Camus: Camera for Mus musculus
Hardware and software for camera video recordings within mouse lab home cages
This script will connect to all cameras currently plugged in 
and display them simultaneously
"""

import os.path  # To navigate paths within the OS
import re  # Regular Expressions
import pandas as pd  # To load csv files using pandas
import cv2  # OpenCV
from multiprocessing import Process
from camus_util import camus_error, check_platform, camus_capture_settings, camus_window_pos, get_all_camera_status  # Utility file for camus
from pygrabber.dshow_graph import FilterGraph  # To get Windows DevicePath info for each camera: 

def process_camera(assigned_cam_num, idx_cam, device_name, num_first_valid_camera):
    # Camera/Capture settings:
    cap_set, CAP_CODEC = camus_capture_settings(device_name, 'Spinel')
    
    # Camera SetupX
    cap = cv2.VideoCapture(idx_cam, cv2.CAP_DSHOW)  # Need to use this for windows compatibility in order to change settings correctly (vs CAP_MSMF? )
    if not cap.isOpened():
        print(f'*** Could not open Assigned {assigned_cam_num}, temp/OpenCV camera index {idx_cam}, device {device_name} ***')  # Ensure capture index device has been opened
        return
    for prop in cap_set:
        temp_prop = 'CAP_PROP_' + prop.upper()
        ret = cap.set(getattr(cv2, temp_prop), cap_set[prop])
        # if not ret:
        #     print(f'Could not adjust camera/captXure setting for {prop}')
    ret = cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*CAP_CODEC))
    # if not ret:
    #     print("Could not adjust camera/capture setting for codec")
    SCALE = 3  # How much smaller to make the image, e.g. 3=1/3 of original size
    VID_WIDTH = int(cap.get(getattr(cv2, "CAP_PROP_FRAME_WIDTH"))/SCALE)
    VID_HEIGHT = int(cap.get(getattr(cv2, "CAP_PROP_FRAME_HEIGHT"))/SCALE)
    # print(assigned_cam_num, idx_cam, temp_name, device_name, VID_WIDTH, VID_HEIGHT, "that's it")

    # Text display settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (10, 40)
    fontScale = 0.8
    color = (0, 0, 255)  # Blue in BGR
    thickness = 1  # Line thickness in pixels
    
    # Screen settings: move window
    # window_name = f'Camus: Cam {assigned_cam_num+1}'
    window_name = f'Camus: Cam {assigned_cam_num}, Idx {idx_cam}: {device_name}'
    window_x, window_y = camus_window_pos(assigned_cam_num, VID_WIDTH, VID_HEIGHT, num_first_valid_camera)
    cv2.namedWindow(window_name)  # Create named window
    cv2.moveWindow(window_name, window_x, window_y)
    num_frame_in_file = 0
    num_frame_skip_show = 1 # Needs to be int
    
    while True:
        # reads frames from a camera, ret checks return at each frame
        ret, frame = cap.read()
        if ret:
            num_frame_in_file += 1
            
            # Lastly, show every nth frame in window, since this can be relatively slow and only used to make sure things are ok during real-time
            if (0 == (num_frame_in_file % num_frame_skip_show)):
                # Resize frame (if needed?)
                frame = cv2.resize(frame, (VID_WIDTH, VID_HEIGHT))
                
                # Put text on image
                frame = cv2.putText(frame, window_name, org, font, fontScale, color, thickness, cv2.LINE_AA)
                
                # Show frame in window
                cv2.imshow(window_name, frame)
    
        # Quick wait/check for input
        temp_char = cv2.waitKey(1) & 0xFF
        if temp_char == ord('q') or temp_char == ord('Q'):  # Quit script
            # When done with this camera, close windows/release webcam
            cap.release()  # Release webcam
            cv2.destroyAllWindows()  # De-allocate any associated memory usage
            print(f'Done with temp index {idx_cam}, device {device_name}')
            return


### MAIN FUNCTION ###
if __name__ == '__main__':
    check_platform()
    processes = []
    
    # first find what cameras are currently connected to/registered with Windows
    df, file_info = get_all_camera_status()
    df_row_default = df.where((df.Status == "Found") | (df.Status == "Plugged in, Not in file")).first_valid_index()
    num_first_valid_camera = int(df.loc[df_row_default, "CameraNum"])

    for idx_cam, temp_path in enumerate(df['DevicePath']):
        if df["Status"][idx_cam] == 'Not found':
            str_found = '-'
        else:
            str_found = '+'
            device_name = df['DeviceName'][idx_cam]
            # Start process for this camera: will not work for multiple cameras on same USB hub: at least on one computer (office desktop) tested so far
            p = Process(target=process_camera, args=(df['CameraNum'][idx_cam], df['IndexCV2'][idx_cam], df['DeviceName'][idx_cam],  num_first_valid_camera))
            
            p.start()
            processes.append(p)

            # Single process: one at a time: will work for multiple cameras on same USB hub
            # process_camera(assigned_cam_num, idx_cam, temp_name, device_name)

    # Check if any processes have been quit, and if so wait for all processes to end
    done = False
    while not done:
        for p_check in processes:
            if not p_check.is_alive():
                for p_end in processes:
                    p_end.terminate()
                done = True
                break
    for p in processes:
        p.join()
