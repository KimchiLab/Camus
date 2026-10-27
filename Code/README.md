# Camus Installation
Tested on Windows 10 & 11, using Anaconda install:  
Run Anaconda Prompt **with Administrator priviledges** (right click on Anaconda Prompt and select Run as Administrator)  
Go to the downloaded GitHub\Camus\Code folder and type:  
conda env create -f camus_env.yaml  

Note: conda is notorious for having a slow environment solver. In our lab it has worked well enough for us, but some other labs have significant slowing creating an environment. Attempted fixes:  
  1. Use another environment creator? We have tried mamba, but OpenCV, which works with conda, doesn't seem to work well via this environment file with mamba  
  2. Reinstall Anaconda using the most limited settings possible   
  3. Update conda's environment solver: https://www.anaconda.com/blog/conda-is-fast-now  
      1. conda update -n base conda
      2. conda install -n base conda-libmamba-solver
      3. conda config --set solver libmamba

### Main Script
Code\camus.py

## To Run 
Run Anaconda Prompt or Powershell from Desktop  
conda activate Camus  
[Will change to Camus environment]  
Go to the python script directory  
cd C:\GitHub\Camus\Code
python camus.py  
This will prompt you to enter the filename (default = "Test") and camera index (default = 0)  
Files will be saved to the Data subfolder if it exists  

### Single command line run
Or to do this all in one line:  
%windir%\system32\cmd.exe "/c C:\ProgramData\Anaconda3\Scripts\activate.bat Camus && python camus.py"  

For ease of use this is already stored in Code\camus.cmd , though it might need to be changed if Anaconda did not install in the default directory.  

### Multiple independent cameras
You should be able to run multiple 


### Show all cameras  
You can run camus_show_all.py, or the associated .cmd file, to show the video from all available cameras as a spot check  

## Camera ID Tracking
OpenCV in python does not track the same camera consistently. When cameras are unplugged and replugged, the python OpenCV camera indexes can change, sometimes unpredictably. If you have more than one camera and would like to keep camera identification somewhat consistent or systematic, we use Windows DevicePath assignments for each camera. These assignments can be found using device manager and saved in the CamusInfo.csv file.  

### Interactively assign camera information. 
You can run camus_assign_info.py, or the associated .cmd file, to interactively assign camera numbers to each camera that is currently plugged into the computer. This script will try to connect to each camera. When it does, if you would like to change the camera number, press "c" on the camera window and type the new number in the python terminal window. When you are ready to go to the next camera, press "q". The windows specific information for each camera will be saved in CamusInfo.csv as described below.  

### CamusInfo.csv
To setup the CamusInfo.csv file manually, rename the Code/SampleCamusInfo.csv file to Code/CamusInfo.csv . Open it in a notepad or spreadsheet software for editing.  
The 3 columns are:  
CameraNum : User chosen number for each camera  
DevicePath : Windows defined DevicePath specific to a camera/USB port combination  
Notes : Optional notes for each camera that will be displayed when selecting a camera  

### Windows Device Paths
To find a DevicePath for a specific camera and a specific USB port:  
Plug in a specific camera to a specific USB port, ideally an independent port.  
Go to Device Mananger (either Run devmgmt.msc OR click Windows key -> start searching for Device Manager, and select it)  
Expand the Cameras section, Right click on the desired/new camera, select properties  
Click on the details tab, and under property, select Device instance path  
Right click and copy this value 
Paste the value to the CamusInfo.csv file   

Please note that windows will typically assign the same Device instance path to any camera of the same type connected to a specific USB port. To keep things stable, always connect the same intended camera to the same USB port. It can be helpful to label the port and any USB cable and camera with the intended number.  


### Adjusting Capture Settings
Capture settings are set by the following line in camus.py,  
cap_set, CAP_CODEC = camus_util.camus_capture_settings(device_name, led_type)  
which calls a utility function from camus_util.py  

This function will preselect camera settings based on the camera device_name and capture settings based on the led_type, for example:  
        if led_type == "Spinel":  
            # Spinel LEDs 120 degrees x 2  
            cap_set.update({"exposure": -8.0})  # Range -1.0 to -13.0; Default -6.0; EXP_TIME=2^(-EXP_VAL), so -6=15.6ms, -7=7.8ms, -8=3.9ms  
            cap_set.update({"brightness": 12.0})  # Range -64.0 to 64.0; Default 0.0  

Images can be made darker by making the exposure setting more negative (less time to capture an image) or by decreasing the brightness. We recommend trying a few settings to optimize contrast and avoiding over/under saturation of the camera.


### Trouble Shooting Startup
If Camus recordings fail to start and the window shuts down -> here are some helpful steps 
 
1. Open an elevated command prompt. Click Start, type cmd, then right-click "Command Prompt" and choose Run as administrator. Click Yes on the UAC prompt. The window title should say "Administrator: Command Prompt."
 
2. Activate the Camus environment. In that admin window, run: C:\ProgramData\Anaconda3\Scripts\activate.bat Camus
The prompt should now show (Camus) at the front.
 
3. Go to your code folder and run the script once.
cd \GitHub\Camus\Code

python camus_show_all.py
 
Once this is done you can press 'Q' on any open camera window. This should resolve the write-permission problem and would allow you to now just use the desktop icon to run cameras normally. Thanks!
 
 
