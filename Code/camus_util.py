# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 23:21:32 2023

@author: ekimc
"""

import os.path # To navigate paths within the OS
import re # Regular Expressions
import platform  # To check the platform given windwos specific settings
import sys
import time
import pandas as pd # To load csv files using pandas
from pygrabber.dshow_graph import FilterGraph # To get Windows DevicePath info for each camera
from cv2 import waitKey
import ctypes
from math import floor
import cv2  # OpenCV


def camus_capture_settings(device_name: str, led_type: str) -> tuple:
    """ Set camera capture settings for different cameras """
    # Folloiwng settings need to be formatted differently
    CAP_CODEC: str = "MJPG" # Codec for camera capture, not saving. Need MJPEG for faster frame rates than YUY2. Needs to be set last in parent function after all other settings. Does not support 1280x720 full field of view?! Really should but likely crops funny https://www.webcamerausb.com/elp-infrared-usb-camera-support-ir-cut-free-driver-30fps-1080p-cctv-camera-board-with-24pcs-ir-led-p-317.html https://www.elpcctv.com/2mp-cmos-ov2710-sensor-free-driver-night-vision-ir-usb-camera-module-full-hd-1080p-p-383.html
    if device_name == "HD USB Camera":  # ELP Webcam names
        # for ELP-USBFHD05MT : 1/2.7" OV2710: valid resolutions (need wide) = 320x240=1.33, 640x480=1.33, 800x600=1.33, 1024x768=1.33, 1280x720=1.78, 1280x1024=1.25, 1920x1080=1.78
        cap_set: dict = {
            "frame_width": 1920,
            "frame_height": 1080,
            "fps": 30.0,  # Frames per second: Should be a float. Setting to 30.0 requires MJPG rather than YUY2, and yield ~19.97 fps
            "sharpness": 2.0,  # Min 0.0, Max 6.0, default 2.0
            "gamma": 100.0,  # Range 72.0 to 500.0, Default 100.0
            "backlight": 1.0,  # Range 0.0 to 2.0; Default 1.0
            "contrast": 32.0,  # Min 0.0, Max 64.0, default 32.0
            "gain": 0.0,  # Range 0.0 to 100.0; Default 0.0
            # Not needed or supported:
            # "saturation": 32.0,  # Min 0.0, Max 64.0, default 60.0 # Doesn't do much for monochrome images
            # "hue": 0.0, # ??? Min -64.0, Max 64.0, default 0.0 # Doesn't do much for monochrome images
            # cap_white_balance =  # Default CAP_PROP_WHITE_BALANCE_BLUE_U 4600.0, but not same
        }
        # Settings to change for brightness adjustments
        if led_type == "Spinel":
            # print(f"LED settings set for {led_type}")
            # Spinel LEDs 120 degrees x 2
            cap_set.update({"exposure": -8.0})  # Range -1.0 to -13.0; Default -6.0; EXP_TIME=2^(-EXP_VAL), so -6=15.6ms, -7=7.8ms, -8=3.9ms
            cap_set.update({"brightness": 12.0})  # Range -64.0 to 64.0; Default 0.0
        elif led_type == "CamusSplit":
            # print(f"LED settings set for {led_type}")
            # Custom Camus Split LEDs: 120 degrees x 2 at 34-45 degrees
            cap_set.update({"exposure": -8.0})  # Range -1.0 to -13.0; Default -6.0; EXP_TIME=2^(-EXP_VAL), so -6=15.6ms, -7=7.8ms, -8=3.9ms
            cap_set.update({"brightness": 32.0})  # Range -64.0 to 64.0; Default 0.0
        elif led_type == "ELP":
            # print(f"LED settings set for {led_type}")
            # ELP LEDs 120 degrees x 2
            cap_set.update({"exposure": -7.0})  # Range -1.0 to -13.0; Default -6.0; EXP_TIME=2^(-EXP_VAL), so -6=15.6ms, -7=7.8ms, -8=3.9ms
            cap_set.update({"brightness": 16.0})  # Range -64.0 to 64.0; Default 0.0
        else: 
            print(f"LED type {led_type} not recognized, using default settings")
            cap_set.update({"exposure": -6.0})  # Range -1.0 to -13.0; Default -6.0; EXP_TIME=2^(-EXP_VAL), so -6=15.6ms, -7=7.8ms, -8=3.9ms
            cap_set.update({"brightness": 0.0})  # Range -64.0 to 64.0; Default 0.0
    elif device_name == "HD Pro Webcam C920":  # Desktop Webcam
        cap_set = {
            "frame_width": 1920,
            "frame_height": 1080,
            "fps": 30.0,  # Frames per second: Should be a float. Setting to 30.0 requires MJPG rather than YUY2, and yield ~19.97 fps
        }
    elif device_name == "DELL S2340T Webcam":  # Desktop Webcam
        cap_set = {
            "frame_width": 1920,
            "frame_height": 1080,
            "fps": 30.0,  # Frames per second: Should be a float. Setting to 30.0 requires MJPG rather than YUY2, and yield ~19.97 fps
        }
    else:
        cap_set = {
            "frame_width": 1920,
            "frame_height": 1080,
            "fps": 30.0,  # Frames per second: Should be a float. Setting to 30.0 requires MJPG rather than YUY2, and yield ~19.97 fps
        }
    return cap_set, CAP_CODEC


def camus_error(msg: str) -> None:
    """ Utility function to print error message and exit """
    # CONSTANTS
    TIME_DELAY_EXIT_SEC = 5
    print('!!! Error: ' + msg)
    print(f'Quitting in {TIME_DELAY_EXIT_SEC} seconds...')
    # Colors not working well across various intepreters and Windows shells
    # print(f'*** Error: {msg} ***')
    # print(f'*** Quitting in {TIME_DELAY_EXIT_SEC} seconds... ***')
    time.sleep(TIME_DELAY_EXIT_SEC)
    sys.exit()


def camus_message_quit(msg: str) -> None:
    """ Utility function to print message and exit """
    # CONSTANTS
    TIME_DELAY_EXIT_SEC = 5
    print('!!! ' + msg)
    print(f'Quitting in {TIME_DELAY_EXIT_SEC} seconds...')
    time.sleep(TIME_DELAY_EXIT_SEC)
    sys.exit()


# Check platform/OS
def check_platform() -> bool:
    """ Check if the current platform is Windows, since many camus functions currently depend on this """
    current_platform = platform.system()
    TARGET_PLATFORM = "Windows"
    flag_platform = current_platform == TARGET_PLATFORM
    if not flag_platform:
        camus_error(f'Only {TARGET_PLATFORM} platform currently supported, not {current_platform}')
    return flag_platform


def get_camera_index(num_cam_target: int = -1, target_device_path = None) -> tuple:
    """ Try to identify a specific windows camera to get OpencCV index, which may not be stable """
    idx_return = -1  # Default error return value
    device_name = "No camera"  # Default error return value
    num_first_valid_camera = 0  # Default error return value
    device_path = ""   # Default error return value
    
    # first find what cameras are currently connected to/registered with Windows
    df, file_info = get_all_camera_status();

    # If a target device path was passed in, try to use it to select the camera
    if target_device_path is not None:
        temp_match = df['DevicePath'] == target_device_path.lower()
        if sum(temp_match) > 0:
            idx_return = df.loc[temp_match, "IndexCV2"].item()
            num_cam_target = df.loc[temp_match, "CameraNum"]
            device_name = df.loc[temp_match, "DeviceName"]
            device_path = target_device_path
            num_first_valid_camera = 0 # ### Edit to actually include correct information? Currently only used when information already had been determined
        return idx_return, num_cam_target, device_name, num_first_valid_camera, device_path
        
    print('Choose from possible cameras: +Available, -Not available')
    for (count, temp_device_path) in enumerate(df['DevicePath']):
        if df["Status"][count] == 'Not found':
            str_found = '-'
        else:
            str_found = '+'
        print(str_found + 
              f' Camera # {df["CameraNum"][count]:2d} = '
              f'{df["Status"][count]}: '
              f'{df["DeviceName"][count]} '
              f'(Path= {temp_device_path}) ')

    # Choose camera from list
    df_row_default = df.where((df.Status == "Found") | (df.Status == "Plugged in, Not in file")).first_valid_index()
    assigned_num_default = int(df.loc[df_row_default, "CameraNum"])
    num_first_valid_camera = assigned_num_default
    # Keep track of intended user numbers vs cv2 indexes
    if num_cam_target < 0:
        num_cam_target = input(f"Enter the desired assigned camera number (default={assigned_num_default}): ") or assigned_num_default
    if isinstance(num_cam_target, str):
        try:
            num_cam_target = int(num_cam_target)
        except ValueError:
            print(f'ERROR: "{num_cam_target}" could not be converted to integer camera index')
            return idx_return, num_cam_target, device_name, num_first_valid_camera, device_path
    # Make sure camera selected from info file is currently registered
    if isinstance(num_cam_target, int) and (sum(df['CameraNum'] == num_cam_target) > 0):
        df_row_target = df.where(df.CameraNum == num_cam_target).first_valid_index()
        print(f'Trying camera number = {num_cam_target}, {df.loc[df_row_target, "Notes"]}: {df.loc[df_row_target, "DevicePath"]}')
        idx_return = df.IndexCV2[df_row_target].item()
        device_name = df.DeviceName[df_row_target]
        device_path = df.loc[df_row_target, "DevicePath"]
    else:
        print(f'Camera index {num_cam_target} not valid')
        return idx_return, num_cam_target, device_name, num_first_valid_camera, device_path

    if idx_return >= 0:
        print(f'Target camera {num_cam_target} found at current python index {idx_return} ({df.loc[df_row_target,"Notes"]}: {df.loc[df_row_target, "DevicePath"]})')
    else:
        print(f'Target camera {num_cam_target} not found ({df.loc[df_row_target, "Notes"]}: {df.loc[df_row_target, "DevicePath"]})')

    return idx_return, num_cam_target, device_name, num_first_valid_camera, device_path


def get_all_camera_status():  # No super simple way to provide return DataFrame type info?
    """ Try to get statuses for all cameras """
    file_info = r'CamusInfo.csv' # csv file with info for cameras

    # Create a blank dataframe
    df = pd.DataFrame(columns=['CameraNum', 'DevicePath', 'Notes', 'DeviceName', 'IndexCV2', 'Status'])
        
    # first find what cameras are currently connected to/registered with Windows
    # Get camera info using Windows DSHOW API from pygrabber
    graph = FilterGraph()
    try:
        device_names = graph.get_input_devices() # Get device default friendly names, may have more than 1 with same name
        device_paths = graph.get_input_device_paths() # Get DevicePath for each device, unique even if same Friendly names
    except ValueError:
        print('ERROR: No available cameras at the moment on this computer!\n')
        return df, file_info
    format_device_paths = format_windows_device_paths(device_paths)

    # Check if there is a saved CamusInfo.csv which details Camera and Device Path Info
    flag_file_info_found = os.path.isfile(file_info)
    if flag_file_info_found:
        # print(f'Camera Selection: Camus info file {file_info} found')
        df = pd.read_csv(file_info)
        # ### !!!
        # ### Make sure there are no duplicate camera numbers?
        # ### !!!
    else:
        # Otherwise create a blank dataframe
        print(f'Camera Selection: Camus info file {file_info} was not found in {os.getcwd()}')
        
    # Fill in dataframe with dummy active camera data
    str_temp = "IndexCV2"
    if str_temp in df.columns:
        df = df.drop(columns=[str_temp])
    df.insert(df.shape[1], str_temp, -1)
    str_temp = "Status"
    if str_temp in df.columns:
        df = df.drop(columns=[str_temp])
    df.insert(df.shape[1], str_temp, "Not found")
    
    # Find CamusInfo device paths among the currently connected camera device paths
    for i, temp_path in enumerate(format_device_paths):
        temp_match = df['DevicePath'] == temp_path.upper()
        if sum(temp_match):
            df.loc[temp_match,'IndexCV2'] = i
            df.loc[temp_match,'Status'] = "Found"
        # If camera are not listed in Camus file, display them too at the end
        else:
            if df.shape[0] == 0:
                temp_num = 0
            else:
                temp_num = df["CameraNum"].max()+1
            df.loc[len(df)] = {'CameraNum': temp_num
                              , 'DevicePath': temp_path
                              , 'DeviceName': device_names[i]
                              , 'Notes': device_names[i]
                              , 'IndexCV2': i
                              , 'Status': 'Plugged in, Not in file'}
    return df, file_info


def format_windows_device_paths(device_paths: list) -> list:
    """ Format Windows Device Paths to unique part for matching with device details """
    format_device_paths = []
    for temp_path in device_paths:
        temp_format = re.findall("\\\\\\\\\\?\\\(.*)#{", temp_path)
        temp_format = temp_format[0]
        temp_format = temp_format.replace("#", "\\")
        temp_format = temp_format.upper()
        format_device_paths.append(temp_format) # Diff is lowercase vs uppercase, and # -> \
    return format_device_paths


def input_number() -> int: 
    """ Get number: Indefinite blocking call until New line """
    txt = ""
    while True:
        temp_key = waitKey(0) & 0xFF
        if temp_key == ord("\n") or temp_key == ord("\r"): # Enter Key
            break
        else:
            txt = txt + chr(temp_key)
    num = int(txt)
    return num

def camus_window_pos(assigned_cam_num: int, VID_WIDTH: int, VID_HEIGHT: int, num_camera_first_position = 0) -> tuple:
    """ Set window position for each camus/camera """
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    # [screen_width, screen_height] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]  # Single monitor setups
    [screen_width, screen_height] = [user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)]  # For windows multi-monitor setups: width, height
    screen_width = floor(screen_width / 10) * 10 # Round screen_width down to nearest 10, due to windows adding a line to screens at times
    # Readjust camera position if needed
    temp_cam_pos = assigned_cam_num - num_camera_first_position
    if temp_cam_pos < 0:
        print(f'Negative camera position for camera {assigned_cam_num}, first camera should be {num_camera_first_position}, setting at 0')
        temp_cam_pos = 0
    # print(assigned_cam_num, VID_WIDTH, VID_HEIGHT, screen_width, screen_height)
    window_x = (VID_WIDTH * temp_cam_pos + 1) % screen_width
    window_y = (VID_HEIGHT * (temp_cam_pos // (screen_width // VID_WIDTH)) % screen_height) + 1
    return window_x, window_y

def camus_close_file(file_vid, file_csv, num_frame_in_file, idx_file) -> tuple:
    # Close/release prior output/files
    file_vid.release()  # Video output
    file_csv.close()  # Close csv file
    num_frame_in_file.append(0)  # reset file/frame counter
    idx_file += 1
    return file_vid, file_csv, num_frame_in_file, idx_file

def camus_initialize_camera(idx_cam, cap_set, CAP_CODEC, num_cam_target) -> tuple:
    cap = cv2.VideoCapture(idx_cam, cv2.CAP_DSHOW)  # Need to use this for windows compatibility in order to change settings correctly (vs CAP_MSMF? )
    if not cap.isOpened():
        camus_error(f'Could not open camera number {num_cam_target}, index {idx_cam}, intended camera number {num_cam_target}')  # Ensure capture index device has been opened
    for prop in cap_set:
        temp_prop = 'CAP_PROP_' + prop.upper()
        ret = cap.set(getattr(cv2, temp_prop), cap_set[prop])
        if not ret:
            print(f'Could not adjust camera/capture setting for {prop}')
    ret = cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*CAP_CODEC))
    if not ret:
        print("Could not adjust camera/capture setting for codec")

    # Check camera settings applied as expected
    for prop in cap_set:
        temp_prop = 'CAP_PROP_' + prop.upper()
        if cap_set[prop] != cap.get(getattr(cv2, temp_prop)):
            print(f'FYI: {prop}: Target= {cap_set[prop]:.1f}, Set= {cap.get(getattr(cv2, temp_prop)):.1f}')
    if cv2.VideoWriter_fourcc(*CAP_CODEC) != cap.get(cv2.CAP_PROP_FOURCC):
        print(f'FYI: codec: Target= {cv2.VideoWriter_fourcc(*CAP_CODEC):.1f}, Set= {cap.get(cv2.CAP_PROP_FOURCC)}')

    return cap
    