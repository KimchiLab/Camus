"""
Camus: Camera for Mus musculus
Hardware and software for camera video recordings within mouse lab home cages
This script will connect to all cameras currently plugged in 
and ask what index they should have assigned, to save into the CamusInfo.csv file
Make sure you are in the correct working directory
"""

from datetime import datetime
import os.path  # To navigate paths within the OS
import re  # Regular Expressions
import pandas as pd  # To load csv files using pandas
import cv2  # OpenCV
from pygrabber.dshow_graph import FilterGraph  # To get Windows DevicePath info for each camera
from camus_util import camus_error, camus_message_quit, check_platform, input_number, camus_capture_settings, get_all_camera_status # Utility file for camus

check_platform()
df, file_info = get_all_camera_status()
# print(df.to_string())

# Initialize webcam & check settings
print(f'\nInstructions to assign numbers to cameras:')
print(f'Make the camera image is the active window')
print(f'Press C to change assigned #, Q to quit')
print(f'Press N or + to go to next camera, P or - to go to previous camera\n')
idx_cam = 0
while idx_cam < len(df['DevicePath']):
    temp_path = df['DevicePath'][idx_cam]
    temp_name = df['DeviceName'][idx_cam]
    assigned_cam_num = df['CameraNum'][idx_cam]
    
    # Check that camera is valid/found by OpenCV
    if df['IndexCV2'][idx_cam] < 0:
        print(f'*** Could not open Assigned {assigned_cam_num}, temp/OpenCV camera index {idx_cam}, device path {temp_path} ***')
        idx_cam += 1
        continue
    
    # Camera/Capture settings:
    # for ELP-USBFHD05MT : 1/2.7" OV2710: valid resolutions (need wide) = 320x240=1.33, 640x480=1.33, 800x600=1.33, 1024x768=1.33, 1280x720=1.78, 1280x1024=1.25, 1920x1080=1.78
    cap_set, CAP_CODEC = camus_capture_settings(temp_name, 'Spinel')

    # Camera Setup
    format_device_paths = df['DevicePath']
    print(f'\n(Temp {idx_cam+1}/{len(format_device_paths)}) Opening Assigned# = {assigned_cam_num}, name= {temp_name}, path= {temp_path}')
    cap = cv2.VideoCapture(df['IndexCV2'][idx_cam], cv2.CAP_DSHOW)  # Need to use this for windows compatibility in order to change settings correctly (vs CAP_MSMF? )
    if not cap.isOpened():
        print(f'*** Could not open Assigned {assigned_cam_num}, temp/OpenCV camera index {idx_cam}, device path {temp_path} ***')  # Ensure capture index device has been opened
        idx_cam += 1
        if idx_cam > len(format_device_paths):
            print('Already past last camera, will quit')
        continue
    for prop in cap_set:
        temp_prop = 'CAP_PROP_' + prop.upper()
        ret = cap.set(getattr(cv2, temp_prop), cap_set[prop])
        # if not ret:
        #     print(f'Could not adjust camera/capture setting for {prop}')
    ret = cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*CAP_CODEC))
    # if not ret:
    #     print("Could not adjust camera/capture setting for codec")
    SCALE = 3  # How much smaller to make the image, e.g. 3=1/3 of original size
    VID_WIDTH = int(cap.get(getattr(cv2, "CAP_PROP_FRAME_WIDTH"))/SCALE)
    VID_HEIGHT = int(cap.get(getattr(cv2, "CAP_PROP_FRAME_HEIGHT"))/SCALE)

    # Text display settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (20, 60)
    fontScale = 2
    color = (0, 0, 255)  # Blue in BGR
    thickness = 4  # Line thickness in pixels
    window_name = f'Camus Assign Camera Info: camera ({idx_cam+1}/{len(format_device_paths)}) {assigned_cam_num} : {temp_name} : {temp_path}'
    
    while True:
        # reads frames from a camera, ret checks return at each frame
        ret, frame = cap.read()
    
        # Resize frame (if needed?)
        frame = cv2.resize(frame, (VID_WIDTH, VID_HEIGHT))
        
        # Put text on image
        frame = cv2.putText(frame, f"Assigned#= {assigned_cam_num}", org, font, fontScale, color, thickness, cv2.LINE_AA)
        
        # Show frame in window
        cv2.imshow(window_name, frame)
    
        # Quick wait/check for input
        temp_char = cv2.waitKey(1) & 0xFF
        if (temp_char) == ord('q') or (temp_char) == ord('Q'):  # Quit script
            print()
            camus_message_quit('Quitting per user request...')
        if (temp_char) == ord('p') or (temp_char) == ord('P') or (temp_char) == ord('-'):  # Previous camera
            idx_cam -= 1
            if idx_cam < 0:
                print('Already at first camera')
                idx_cam = 0
            else:
                break
        if (temp_char) == ord('n') or (temp_char) == ord('N') or (temp_char) == ord('+'):  # Next camera
            idx_cam += 1
            if idx_cam > len(format_device_paths):
                print('Already past last camera')
                idx_cam = len(format_device_paths)
            else:
                break
        elif temp_char == ord('c') or temp_char == ord('C'):  # Change assigned num
            print('Change assigned camera number: Enter digits followed by <Enter> key')
            # str_idx = input(f"What number should camera {temp_name}, {device_names[idx_cam]} = {temp_path} be? (enter number): ")
            # assigned_cam_num = int(str_idx)
            assigned_cam_num = input_number()
            print(f'Changed to assigned camera number {assigned_cam_num}')

            # Check that this number is not already in use for cameras with other device paths
            for idx_match, flag_match in enumerate(df['CameraNum'] == assigned_cam_num):
                if flag_match and not df['DevicePath'][idx_match] == temp_path.upper():
                    change_number = df['CameraNum'].max() + 1
                    print(f'Also changed another camera that already had that same assigned number to {change_number}')
                    df.loc[idx_match, 'CameraNum'] = change_number

            # Save new assigned info back to InfoCamus.csv file
            temp_match = df['DevicePath'] == temp_path.upper()
            if sum(temp_match):
                df.loc[temp_match, 'CameraNum'] = assigned_cam_num
            else:
                df.loc[len(df)] = {'CameraNum': assigned_cam_num
                                  , 'DevicePath': temp_path.upper()
                                  , 'DeviceName': temp_name}

            # Write back to file
            try:
                temp_df = df
                # Sort by camera numbers for writing back only
                temp_df = temp_df.sort_values(by = ['CameraNum'])
                temp_df = temp_df.drop(columns=['IndexCV2', 'Status'])
                temp_df.to_csv(file_info, index=False)
            except:
                print(f'Could not write to file {file_info}. Perhaps it is open somewhere?')

    # When done with this camera, close windows/release webcam
    cap.release()  # Release webcam
    cv2.destroyAllWindows()  # De-allocate any associated memory usage
    print(f'Done with temp index {idx_cam}, path {temp_path}')

