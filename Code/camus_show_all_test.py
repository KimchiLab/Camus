"""
Camus: Camera for Mus musculus
TEST recording script.

Opens every camera currently plugged in to the computer (like camus_show_all.py)
and records video from each one using the CamusSplit LED settings (like camus_ledsplit).

Use this to test different settings (exposure, brightness, etc.) on a new camera/LED
setup. The actual exposure, brightness, and camera number are:
  - printed to the console at startup
  - overlaid on each live preview window
  - written to a *_settings.txt file alongside the .avi

Output: <script_folder>/Data/show_all test videos/TEST_<timestamp>_cam<N>_<device>.avi

Press 'q' or 'Q' in any preview window to stop all recordings cleanly.
"""

import os
import os.path
import time
import datetime
import cv2  # OpenCV
from multiprocessing import Process, Event
from camus_util import (
    check_platform,
    camus_capture_settings,
    camus_window_pos,
    get_all_camera_status,
)


# ---- TEST CONFIG: change these while testing ----------------------------
LED_TYPE = "CamusSplit"   # Pulls exposure=-8.0, brightness=32.0 from camus_util
FILE_PREFIX = "TEST"
DISPLAY_SCALE = 3         # Preview window = 1/DISPLAY_SCALE of full-res capture

# Anchor the output folder to the SCRIPT's location, not the cwd.
# This way it doesn't matter whether you launch from a .cmd, an IDE,
# or a shell -- files always land next to the script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "Data", "show_all test videos")

# How long to give each child to finalize its AVI on shutdown before we give up.
SHUTDOWN_GRACE_SEC = 5.0
# -------------------------------------------------------------------------


def process_camera(assigned_cam_num, idx_cam, device_name,
                   num_first_valid_camera, session_timestamp,
                   output_folder, shutdown_event):

    # Defensive: make sure the folder exists from the child's perspective too.
    os.makedirs(output_folder, exist_ok=True)

    # --- Capture settings (same call ledsplit makes) ---
    cap_set, CAP_CODEC = camus_capture_settings(device_name, LED_TYPE)

    # --- Open camera ---
    cap = cv2.VideoCapture(idx_cam, cv2.CAP_DSHOW)  # DSHOW needed on Windows to actually apply settings
    if not cap.isOpened():
        print(f'*** Could not open Cam {assigned_cam_num} '
              f'(OpenCV idx {idx_cam}, device {device_name}) ***')
        shutdown_event.set()  # don't leave the others running forever
        return

    # Apply all properties from cap_set
    for prop in cap_set:
        temp_prop = 'CAP_PROP_' + prop.upper()
        cap.set(getattr(cv2, temp_prop), cap_set[prop])
    # Codec must be set LAST per camus_util note
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*CAP_CODEC))

    # --- Read back the values the camera actually accepted ---
    actual_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps    = cap.get(cv2.CAP_PROP_FPS)
    actual_exp    = cap.get(cv2.CAP_PROP_EXPOSURE)
    actual_bright = cap.get(cv2.CAP_PROP_BRIGHTNESS)

    # Report to console
    print(f'--- Cam {assigned_cam_num}: {device_name} (OpenCV idx {idx_cam}) ---')
    print(f'    Resolution : {actual_width} x {actual_height} @ {actual_fps:.2f} fps')
    print(f'    Exposure   : {actual_exp:.1f}   (target {cap_set.get("exposure", "n/a")})')
    print(f'    Brightness : {actual_bright:.1f}   (target {cap_set.get("brightness", "n/a")})')

    # --- Set up output video file ---
    safe_device = device_name.replace(' ', '_').replace('/', '_')
    file_base = f'{FILE_PREFIX}_{session_timestamp}_cam{assigned_cam_num}_{safe_device}'
    file_vid_path = os.path.join(output_folder, f'{file_base}.avi')

    # Save with MJPG to match the capture codec (no transcoding)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    save_fps = float(cap_set.get('fps', actual_fps if actual_fps > 0 else 30.0))
    file_vid = cv2.VideoWriter(file_vid_path, fourcc, save_fps,
                               (actual_width, actual_height))
    if not file_vid.isOpened():
        print(f'*** Could not open video writer for {file_vid_path} ***')
        cap.release()
        shutdown_event.set()
        return
    print(f'    Writing to : {file_vid_path}')

    # --- Drop a sidecar settings file so we know what was used for this recording ---
    file_meta_path = os.path.join(output_folder, f'{file_base}_settings.txt')
    with open(file_meta_path, 'w') as f:
        f.write(f'Camera Number     : {assigned_cam_num}\n')
        f.write(f'OpenCV Index      : {idx_cam}\n')
        f.write(f'Device Name       : {device_name}\n')
        f.write(f'LED Type          : {LED_TYPE}\n')
        f.write(f'Resolution        : {actual_width} x {actual_height}\n')
        f.write(f'FPS (target/read) : {cap_set.get("fps", "n/a")} / {actual_fps:.2f}\n')
        f.write(f'Exposure (target/read)   : {cap_set.get("exposure", "n/a")} / {actual_exp:.1f}\n')
        f.write(f'Brightness (target/read) : {cap_set.get("brightness", "n/a")} / {actual_bright:.1f}\n')
        f.write(f'Session timestamp : {session_timestamp}\n')
        f.write('\n--- Full target cap_set ---\n')
        for prop, val in cap_set.items():
            f.write(f'  {prop}: {val}\n')

    # --- Preview window ---
    VID_WIDTH  = int(actual_width  / DISPLAY_SCALE)
    VID_HEIGHT = int(actual_height / DISPLAY_SCALE)

    font       = cv2.FONT_HERSHEY_SIMPLEX
    fontScale  = 0.6
    color      = (0, 0, 255)   # Red in BGR
    thickness  = 1

    window_name = f'Camus TEST: Cam {assigned_cam_num}, idx {idx_cam}: {device_name}'
    window_x, window_y = camus_window_pos(assigned_cam_num, VID_WIDTH, VID_HEIGHT,
                                          num_first_valid_camera)
    cv2.namedWindow(window_name)
    cv2.moveWindow(window_name, window_x, window_y)

    num_frame_in_file = 0
    num_frame_skip_show = 1  # Show every frame; raise this if preview is too heavy

    # --- Recording loop. Wrapped in try/finally so the AVI gets finalized
    #     no matter how we leave (Q, exception, sibling crash, etc.).
    try:
        while not shutdown_event.is_set():
            ret, frame = cap.read()
            if ret:
                num_frame_in_file += 1

                # Save the FULL-RES, CLEAN frame to disk (no overlay)
                file_vid.write(frame)

                # Show a downscaled copy with overlay info
                if (0 == (num_frame_in_file % num_frame_skip_show)):
                    disp = cv2.resize(frame, (VID_WIDTH, VID_HEIGHT))
                    overlay_lines = [
                        f'Cam {assigned_cam_num} (idx {idx_cam}): {device_name}',
                        f'Exp: {actual_exp:.1f}   Bright: {actual_bright:.1f}',
                        f'LED: {LED_TYPE}   Frames: {num_frame_in_file}',
                    ]
                    y = 25
                    for line in overlay_lines:
                        disp = cv2.putText(disp, line, (10, y), font, fontScale,
                                           color, thickness, cv2.LINE_AA)
                        y += 22
                    cv2.imshow(window_name, disp)

            temp_char = cv2.waitKey(1) & 0xFF
            if temp_char == ord('q') or temp_char == ord('Q'):
                # Tell every other camera to wind down too
                shutdown_event.set()
                break
    finally:
        # GUARANTEED cleanup -- this is what was missing before.
        try:
            cap.release()
        except Exception as e:
            print(f'    Cam {assigned_cam_num}: cap.release() raised: {e}')
        try:
            file_vid.release()
        except Exception as e:
            print(f'    Cam {assigned_cam_num}: file_vid.release() raised: {e}')
        try:
            cv2.destroyWindow(window_name)
        except Exception:
            pass
        print(f'Done Cam {assigned_cam_num} ({device_name}): '
              f'{num_frame_in_file} frames -> {file_vid_path}')


### MAIN ###
if __name__ == '__main__':
    check_platform()

    # Make sure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # One timestamp for the whole session so all cameras' files group together
    session_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    print('===== Camus SHOW_ALL TEST recording =====')
    print(f'LED type        : {LED_TYPE}')
    print(f'Output folder   : {OUTPUT_FOLDER}')
    print(f'Session stamp   : {session_timestamp}')
    print(f'File prefix     : {FILE_PREFIX}')
    print('Press "q" in any preview window to stop all cameras.\n')

    # Find all currently connected cameras
    df, file_info = get_all_camera_status()
    df_row_default = df.where(
        (df.Status == "Found") | (df.Status == "Plugged in, Not in file")
    ).first_valid_index()
    if df_row_default is None:
        print("No cameras currently plugged in. Quitting.")
        raise SystemExit
    num_first_valid_camera = int(df.loc[df_row_default, "CameraNum"])

    # Shared shutdown signal across all camera processes
    shutdown_event = Event()

    processes = []
    for idx_cam, temp_path in enumerate(df['DevicePath']):
        if df["Status"][idx_cam] == 'Not found':
            continue
        p = Process(
            target=process_camera,
            args=(
                df['CameraNum'][idx_cam],
                df['IndexCV2'][idx_cam],
                df['DeviceName'][idx_cam],
                num_first_valid_camera,
                session_timestamp,
                OUTPUT_FOLDER,
                shutdown_event,
            ),
        )
        p.start()
        processes.append(p)

    if not processes:
        print("No active cameras to record from. Quitting.")
        raise SystemExit

    print(f'Started {len(processes)} camera process(es).\n')

    # Wait until either:
    #   - someone presses Q in a preview window (-> shutdown_event gets set), or
    #   - a child process dies on its own (camera unplugged, crash, etc.)
    try:
        while True:
            if shutdown_event.is_set():
                break
            if any(not p.is_alive() for p in processes):
                # A child died without setting the event. Propagate the shutdown.
                shutdown_event.set()
                break
            time.sleep(0.2)   # don't pin a CPU
    except KeyboardInterrupt:
        print('Ctrl-C received, shutting down...')
        shutdown_event.set()

    # Give every child a chance to release its VideoWriter (this is the whole point).
    print(f'Shutting down -- waiting up to {SHUTDOWN_GRACE_SEC:.0f}s for cameras to finalize files...')
    for p in processes:
        p.join(timeout=SHUTDOWN_GRACE_SEC)

    # Force-kill anything still hanging on (e.g. a frozen cap.read()).
    for p in processes:
        if p.is_alive():
            print(f'  PID {p.pid} did not exit in time, terminating.')
            p.terminate()
            p.join()

    print(f'All cameras stopped. Files in: {OUTPUT_FOLDER}')
