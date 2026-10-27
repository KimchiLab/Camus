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
from os import system
import cv2
import ctypes
from ctypes import wintypes
import argparse
from math import floor
import numpy as np
import camus_util
 
camus_util.check_platform()

# Options via command line interface
DEFAULT_DURATION_MIN = 60  # Files need to be <2GB. 2hr=120min was approximately 1.5GB, but files a bit slow for processing, so switched to 1hr=60min 2024/01/01
parser = argparse.ArgumentParser(description = "Camus command line interface")
parser.add_argument("-s", "--subject", help="Subject Name/ID", action="store", default="")
parser.add_argument("-c", "--camera", help="Camera Index", action="store", default=-1, type=int)
parser.add_argument("-d", "--duration_min", type=float, action="store", default=DEFAULT_DURATION_MIN, help = "Duration of each recording file in minutes")
parser.add_argument("-n", "--number_first_camera", type=int, action="store", default=0, help = "Number of camera corresponding to first position, in case indexing is spread across computers")
parser.add_argument("-f", "--frame_skip_show", type=int, action="store", default=1, help = "nth Frame number to show, 1=all frames, 30=every 30th frame, etc") # 10 vs 1 saves 1-2% CPU on personal desktop
parser.add_argument("-i", "--frame_initial_show", type=int, action="store", default=1800, help = "number of frame to show Initially, duration will depend on frame rate, e.g. 1800=60sec*30fps") # 10 vs 1 saves 1-2% CPU on personal desktop
parser.add_argument("-l", "--led_type", action="store", default="Spinel", help = "Type of LED Panel, to adjust prestored brightness settings")
args = parser.parse_args() # Read arguments from command line

# Set Filename/Participant name
if args.subject:
    filename_prefix = args.subject
    filename_prefix = filename_prefix.replace('\"', '')
else:
    FILENAME_DEFAULT = "Test"
    filename_prefix = input(f'Enter the filename prefix, typically the participant ID (default={FILENAME_DEFAULT})\nif recording more than one, put dashes between each, e.g. 01-02-04: ') or FILENAME_DEFAULT
filename_prefix = filename_prefix.upper()  # Make all uppercase to minimize duplicates participant subjects later on
print(f'Using filename prefix = {filename_prefix}\n')

# Define parent & participant specific save path: make sure paths exist
save_path_parent = r'..\Data'  # Define parent save path
if not os.path.exists(save_path_parent):  # Make sure path exists
    os.mkdir(save_path_parent)
save_path = os.path.join(save_path_parent, filename_prefix)  # Define participant save path
if not os.path.exists(save_path):  # Make sure path exists
    os.mkdir(save_path)

# Choose appropriately indexed camera: not straightforward using cv2 and Windows
idx_cam, num_cam_target, device_name, num_first_valid_camera, target_device_path = camus_util.get_camera_index(args.camera)
if idx_cam < 0:
    camus_util.camus_error('No valid camera chosen, check active valid camera and info file')

# Camera/Capture settings:
# for ELP-USBFHD05MT : 1/2.7" OV2710: valid resolutions (need wide) = 320x240=1.33, 640x480=1.33, 800x600=1.33, 1024x768=1.33, 1280x720=1.78, 1280x1024=1.25, 1920x1080=1.78
if args.led_type:
    led_type = args.led_type
    led_type = led_type.replace('\"', '')
cap_set, CAP_CODEC = camus_util.camus_capture_settings(device_name, led_type)

# Initialize webcam & check settings
print("Opening camera...")
cap = camus_util.camus_initialize_camera(idx_cam, cap_set, CAP_CODEC, num_cam_target)

# Setup dummy vars
file_vid = ''
file_csv = ''

# Video settings for saving, not set by camera settings
VID_COLOR = False  # True=Color, False=black&white/monochrome/graySCALE, filesize only about 5-10% smaller?
SCALE = 3  # How much smaller to make the image, e.g. 3=1/3 of original size
VID_WIDTH = int(cap_set["frame_width"]/SCALE)
VID_HEIGHT = int(cap_set["frame_height"]/SCALE)
# Video Settings: Define the outpt codec and then create VideoWriter object
# fourcc = -1 # to display all available codecs: only for windows and doesn't always work?
# codec=XVID/DIVX/FMP4 -> container=avi. This is about 1/2 the size of open H264/AVC1, at least with default settings.
# Also used by https://github.com/AdaptiveMotorControlLab/Camera_Control/blob/master/camera_control_GUI.py
VID_CODEC = 'XVID'
VID_EXT = 'avi'
# For H264, need to place get the correct openh264-1.8.0-win64.dll version from
# https://github.com/cisco/openh264/releases
# And place in the same dir as the .py python script
# fourcc = cv2.VideoWriter_fourcc(*'H264')  # Same output as x264 & avc1
# VID_EXT = 'mp4'
fourcc = cv2.VideoWriter_fourcc(*VID_CODEC)  # Same output as x264 & avc1

# Screen settings: move windows
window_name = f"{filename_prefix}_Cam{num_cam_target:02d}"
console_name = window_name + " Console"
# Rename and minimize the command console window
system("title " + console_name) # Rename command prompt window name
time.sleep(0.1) # Give rename time to work
# Find console window by title, otherwise the active/foreground window may change before selection
user32 = ctypes.WinDLL('user32')
handle_console = user32.FindWindowW(None, console_name)
SW_SHOWNORMAL = 1
SW_MINIMIZE = 6
SW_RESTORE = 9
user32.ShowWindow(handle_console, SW_MINIMIZE)

# Create and reposition the video window
cv2.namedWindow(window_name)  # Create named window
time.sleep(0.1) # Give window creation time to work
if args.number_first_camera:
    num_camera_first_position = args.number_first_camera
else:
    num_camera_first_position = num_first_valid_camera
window_x, window_y = camus_util.camus_window_pos(num_cam_target, VID_WIDTH, VID_HEIGHT, num_camera_first_position)
cv2.moveWindow(window_name, window_x, window_y)

# Setup window and Start counters (frames & time)
print("Starting recording...")
flag_show_img = True
# flag_write_file = True
idx_file = 0
num_error = 0
num_frame_in_file = [0]  # keep as list
MAX_FRAME_IN_FILE = args.duration_min * 60 * cap_set['fps']  # min * sec * fps
num_frame_skip_show = args.frame_skip_show
num_frame_initial_show = args.frame_initial_show
ts_start = time.perf_counter()
# OpenCV Text parameters
font = cv2.FONT_HERSHEY_SIMPLEX
org = (20, 20)
fontScale = 0.5
max_error = 100
max_retry = 100

# LOOP runs if capturing has been initialized.
while True:
    # reads frames from a camera, ret checks return at each frame
    ret, frame = cap.read()
    if ret: # Surprisingly this is still evaluating as True when the camera has been disconnected? but only coming in ~1/sec
        if 0 == np.sum(frame):
            num_error += 1
            print(f'No frame data received: Error # {num_error}, closing file...')
            file_vid, file_csv, num_frame_in_file, idx_file = camus_util.camus_close_file(file_vid, file_csv, num_frame_in_file, idx_file)
            # Reconnect to camera
            if num_error <= max_error:
                print('Trying to reconnect to camera...')
                cap.release()  # Release webcam
                i_try = 0
                while True:
                    # Need to reidentify idx_cam to see if back/present: translate from num_cam_target -> idx_cam
                    print(f'Reconnection attempt {i_try} of {max_retry}...')
                    idx_cam, temp_num_cam_target, temp_device_name, temp_num_first_valid_camera, temp_target_device_path = camus_util.get_camera_index(num_cam_target, target_device_path)
                    if idx_cam >= 0:
                        # Initialize camera
                        cap = camus_util.camus_initialize_camera(idx_cam, cap_set, CAP_CODEC, num_cam_target)
                        break
                    elif i_try > max_retry:
                        camus_util.camus_error(f'Could not reconnect to camera after {i_try} attempts, quitting...')
                    else:
                        time.sleep(1)
                    i_try += 1
            else:
                print(f'Too many invalid frame errors ({num_error}), quitting...')
                break
    
        # Get/note time of new frame
        str_datetime = datetime.now().strftime("%Y%m%d-%H%M%S.%f")

        # Before saving: check if need to close last file
        if num_frame_in_file[idx_file] >= MAX_FRAME_IN_FILE:
            file_vid, file_csv, num_frame_in_file, idx_file = camus_util.camus_close_file(file_vid, file_csv, num_frame_in_file, idx_file)

        # If empty file: setup new files: has the "odometer" rolled over and/or (re-)started at 0?
        if num_frame_in_file[idx_file] == 0:
            # Format filenames and open output files for saving: video out + csv
            filename = f'{filename_prefix}_{datetime.now().strftime("%Y%m%d-%H%M%S")}_Cam{num_cam_target:02d}'
            path_filename = os.path.join(save_path, filename)
            file_vid = cv2.VideoWriter(path_filename + "." + VID_EXT, fourcc, cap_set["fps"], (VID_WIDTH, VID_HEIGHT), VID_COLOR)
            # Frame time text file output: this is based on the computer clock, not necessarily the camera clock (which is likely not precise for a webcam regardless)
            file_csv = open(path_filename + ".csv", "w", encoding="utf8")
            # To convert to a datetime number, can use the following formula in excel for cell C1:
            # =VALUE(CONCAT(LEFT(B1,4),"/",MID(B1,5,2),"/",MID(B1,7,2)," ", MID(B1,10,2),":", MID(B1,12,2),":", MID(B1,14,9)))
            # This number is in the units of days, to convert to seconds in cell D1: =24*60*60*C1
            print(f'  Video file {idx_file:3d}: {path_filename}')

        # Now preprocess frame
        # Resize frame (if needed?): 115ns/it total when first
        frame = cv2.resize(frame, (VID_WIDTH, VID_HEIGHT))
        # Convert the frame to graySCALE: need to add False flag at end of VideoWriter call above: 200ns/it total when first
        if not VID_COLOR:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Save data to disk
        # if flag_write_file:
        num_frame_in_file[idx_file] += 1
        file_csv.write(f'{num_frame_in_file[idx_file]},{str_datetime}\n') # output current frame count/timestamp info (nearest to when obtained), using file counter
        file_vid.write(frame) # output the frame after converting

        # Lastly, show every nth frame in window, since this can be relatively slow, primarily used to make sure things are ok during real-time at startup
        if flag_show_img and ((0 == idx_file and num_frame_in_file[idx_file] < num_frame_initial_show) or (0 == (num_frame_in_file[idx_file] % num_frame_skip_show))):
            if num_frame_skip_show > 1 and (num_frame_in_file[idx_file] >= num_frame_initial_show):
                str_record_nodisplay = f'Displaying every {num_frame_skip_show} frame(s)'
                color = (0)  # Monochrome
                thickness = 3  # Line thickness in pixels
                frame = cv2.putText(frame, str_record_nodisplay, org, font, fontScale, color, thickness, cv2.LINE_AA)
                color = (255)  # Monochrome
                thickness = 1  # Line thickness in pixels
                frame = cv2.putText(frame, str_record_nodisplay, org, font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.imshow(window_name, frame)

    # Quick wait/check for 'q' key to stop the program
    temp_key = cv2.waitKey(1) & 0xFF
    if temp_key == ord('q') or temp_key == ord('Q'):  # Quit script
        break
    elif temp_key == ord('o') or temp_key == ord('O') or temp_key == ord('s') or temp_key == ord('S'):
        flag_show_img = not flag_show_img
        str_record_nodisplay = f'Recording/saving, but not displaying...'
        color = (0)  # Monochrome
        thickness = 3  # Line thickness in pixels
        frame = cv2.putText(frame, str_record_nodisplay, org, font, fontScale, color, thickness, cv2.LINE_AA)
        color = (255)  # Monochrome
        thickness = 1  # Line thickness in pixels
        frame = cv2.putText(frame, str_record_nodisplay, org, font, fontScale, color, thickness, cv2.LINE_AA)
        cv2.imshow(window_name, frame)

# At end: Display number of frames collected & fps
ts_end = time.perf_counter()
user32.ShowWindow(handle_console, SW_RESTORE)
dur = ts_end - ts_start
print(f'num total frames: {sum(num_frame_in_file)}')
print(f'duration (sec): {dur}')
print(f'fps actual: {sum(num_frame_in_file) / dur}')

# When completely done, close files/windows/release webcam/files
file_vid, file_csv, num_frame_in_file, idx_file = camus_util.camus_close_file(file_vid, file_csv, num_frame_in_file, idx_file)
cap.release()  # Release webcam
cv2.destroyWindow(window_name)
cv2.destroyAllWindows()  # De-allocate any associated memory usage
print("Done!")

