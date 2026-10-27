# Computer
Single Camus setups can be run on most Windows computers. But once you go above 2 USB cameras on a laptop, or 4 USB cameras on a desktop, things get trickier. You can not simply add more USB ports using external USB hubs, since multiple cameras will be sharing the same bandwith. Each camera ultimately needs an ***internally independent*** USB port. For most people, when trying the system out, a laptop will be enough. For larger numbers of caemras, we have built desktop computers that can be mounted on the back of the cage racks and can record from up to 20 cameras at a time. We have worked hard to find components that allow us to run as many cameras as possible on one computer. The key components are PCIe expansion cards that allow for additional independent USB3 ports, and a CPU capable of coordinating so many USB devices at once. If you are interested in running larger numbers of cameras, we recommend looking at the most current computer [parts list](CamusPartsList.xlsx).

# Camera/LED Parts
We have found that the standard LED panels on the ELP cameras do not spread enough light across the cage and can be fairly variable from panel to panel. While you can compensate for panel variability by adjusting the exposure times and brightness values in the python scripts, we instead are using two wide-angle IR LED panels from Spinel that we can mount at angles. The panel to panel consistency seems to be better. When you first try either of these panels, however, you may not see much if you plug the camera into any computer/software. This is likely because the camera is primarily IR sensitive and the IR LEDs will not turn on if there is ambient light, due to a photoresistor. This sensor has to be inactive to turn on the IR LEDs. You can either print a black PLA cap (shown below), or snap off the photoresistor (what we tend to do now--carefully), or desolder it. It is sometimes hard to cover the photoresistor with your finger or tape, a better way to check if it is affecting your ability to record is to turn off the room lights. If the LEDs are on there should be a red light from the LEDs, and you can also usually see that they are on more clearly using a phone camera, which is usually IR sensitive.  

# 3D Printed Parts
We have printed our 3D printed parts using either a Prusa MK3S+ and a Bambu A1. In general we print our parts in gray PLA. The one exception is the cap to cover the camera photoresistor/ambient light sensor. Most parts can be printed in an intuititve orientation. However, the water bottle holder should be printed at an angle, in order to minimize breakage at stress points. We print these holders on the Prusa with some tweaks to support settings, but they also print well on the Bambu printer with tree supports. Sample 3mf files for both printers are included in the repo. We recommend cleaning all parts included in a cage at least weekly or between mice.  Water bottles and food hoppers can be washed with detergent and then sprayed with 70% ethanol or isopropyl alcohol. Camera housing should be sprayed with a sterilant such as C-Dox/Clidox (typically provided by the animal care facility).  

# Building and Installing Camus Cameras for in home cage recordings
Details shown here are for Allentown NexGen Mouse 500 Standard cage with a Micro Barrier Top. The Sutton lab has also worked on modifying parts as needed for the SuperMouse 750 cages.  

Before starting make sure you use all parts that are already printed before reprinting new parts and save any extra parts for future builds. 

## 3D Printed Parts
1. CameraHolder & Cap: ![Image 
 of camera holder and cap](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/cap%20and%20camera%20holder%20-%20Copy.jpeg)
1. 2 Photosensor round covers for LED panels (1 for each panel): **Must be printed in black PLA for light shielding** 
1. 4 LED rectangular covers for LED panels (2 for  each panel):  **Must be printed in black PLA for light shielding** ![Image of 2 round ps cover](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/the%20blockers.jpeg)
1. Cage Top mouse escape prevention grid ![Image of Top mouse escape prevention grid](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/top%20of%20cage.jpeg)
1. Pair of USB cable connection covers (top & bottom) ![Image of USB cable connection cover](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/Usb.jpeg)

### Other parts/materials
1. Camera: 120 degree ELP Webcam (remove LED board & LED board cables) ![camera picture](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/camera%20for%20github.jpeg)
1. 2 Flat Spinel LED Panels: Wider and brighter than the panels that come with the camera ![Image of LED Panels](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/led%20connected%20(1).jpeg)
1. Heat shrink tubing: 1/16" & 1/8": cut two 1cm pieces of each diameter ![Image of tubing](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/heat%20shrink%20tubing.jpeg)

### Cables
1. USB to JST cable (thin/3.5mm): connects camera to USB extension, comes with camera  
1. USB 2.0 A-to-A extension cable: connect camera USB cable to computer. We are using 5m active extension cables. USB2.0 is only rated to 5m.  
1. Custom soldered Y-JST to 2 JST cables (2mm JST connectors): connects camera to two LED panels ![Image of the JST cables](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/03f840b8-3990-48e7-8221-6aa2ec639096.jpg)
	1. Take the JST-JST wire from the camera to the initial led plate remove it and cut in half.
        1. Strip each side of the wire (24g cutter) so that ~6mm wire is exposed on the ends
        1. Twist the strands in each wire to bring them together
        1. Twist the two free ends of the same color around each other.  ![Image of the JST cables getting twisted](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/f755bf52-2e28-4ce1-938b-354be2f42d94.jpg)
    	1. Cut another JST-JST cable to obtain a third half and once again strip and twist each side
        1. Add Heat shrink tubing (1cm of 1/16 and 1cm of 1/8) onto the third half JST cable wire and then hook the third free ends into the hooks of the two wrapped ends, so that they are mechanically stable (ensure colors are corresponding). ![Image of the JST cables with exposed wire and heat shrink tubing](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/1a9770b9-fabb-4ea6-830e-52f40053998d.jpg)
	1. **Critical point: The same color wire must be on the same side of the connector.** When the notch of the cable is facing you: Red should be on the Right, and when the two tabs and silver components are facing you Black is on the Right. Some cables are sent in reverse orientation so each end is different. These will need to be switched if they are soldered that way. This can be done carefully by inserting a thin surface under the white plastic tab and gently pulling out each wire, then gently reinserting them with the silver hook pushing past the white plastic tab.
        1. Solder the third free wire to the two-hooked wires of the same color. Repeat with the other color. ![Image of the JST cables getting soldered](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/48944506-51d3-4b56-a320-17c392af5e32.jpg)
        2. Use the heat gun to snug the heat shrink tubing on the exposed wire.  ![Image of the heat shrink tubing setup](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/49a8f4bd-1e7f-44f6-a31b-e323e47ad8e0.jpg)
        3. You are all set!               
           ![Image of the Y-shaped JST cable](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/9ab2f7f3-0737-4ef5-b62c-3e361b730f79.jpg)

### Adhesives
1. Cyanoacrylate Glue (Super/Krazy glue)
1. Black Electrical tape
1. Duct Tape (2" wide)

## Building
1. 3D print all necessary parts
1. Make a Y shaped JST to JST x 2 cable (described above). 
1. Take the camera and connect it to the two spinel LED plates. This wiring should have one initial JST connection to the camera that is connected to another JST on the led plate. **Make sure the red wires are connecting to the positive terminal on all plates, otherwise the LED boards will smoke and be ruined** ![Image of camera connected to LED plates](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/connected%20everything%20-%20Copy.jpeg)
1. Make sure the camera USB to JST cable is a 3.5mm diameter cable. If larger, replace it with a 3.5mm cable.
1. Place the camera into the holder. Tuck the wiring underneath it, and make sure the USB connecter  through the opening in the center out the back. ![Image of camera being set up](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/pt%202.jpeg)
1. Place the photosensor cap over each Led panel photosensor. Use the cyanoacrylate to glue the cap to the board, otherwise the mice will eventually remove them (even if fit was originally tight). ![Image of photosensor caps on led plates](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/blockers%20placed%20onto%20led%20plates%20with%20superglue%20-%20Copy.png)
1. Use 8 “2-56 3/16" screws” to screw in the two LED Panels, making sure the photosensor is pointed outwards (laterally), away from the center.
1. Put the square holder with the lens hole on top of the camera ![Image of camera almost finished](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/pt%204.jpeg)
1. Use 4 “2-56 1in+1/8" screws” to screw in the camera square holder cap to the housing ![Image of screwed in camera](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/pt%205.jpeg)

## Securing the Camera to the Cage top/Ceiling
1. Tape the Side of the cable to the side wing of the camera holder from below **This prevents any rough movement from disconnecting the camera,and stabilizes the connection**
![Image of tape stablization](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/WhatsApp%20Image%202024-05-07%20at%2012.53.19%20PM.jpeg)
![Image of tape stabilizer](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/small%20tape%20thingy%20to%20stabalize.jpeg)
1. Put the camera holder in the center of the cage.
![Image of camera in cage](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num%201.png)
1. Thread the USB cord through the cage top
![Image of top of cage](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num2.png)
![Image of top of cage](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num2.2.png)
![Image of top of cage](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num%203%20(2).png)

1. Thread the USB cord through the mouse escape prevention system grid
![img of cable through grid](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num4.png)
1. Take a 2" wide x 4" long strip of duct tape and split it down the middle so you have two 1" pieces.

### Camera Placement in Cage
In order for deeplabcut to function properly, it must be able to track the mouse through most of the cage.
For our cages (Allentown NexGen Mouse 500 Standard Cage with Micro Barrier Top), the camera should be placed where the flat wings just line up with the edge of the micro-barrier lid (the purple grate).
1. Use the pieces to tape the lateral edge tabs of the wings of the camera holder to the sides of the cage top.
![img of 1st taping](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num%205.png)
The wings should then be taped to the sides using the strongest available tape--we use duct tape. 
In total, there should be 4 pieces of tape: 1 on each wing tip (1" width = 1/2 of 2" width), and a separate piece on each wing itself (2" width).
Finally, the cord should be taped such that it lays flat on the top of the cage and then runs along the side of the cage top. 

1. Take two 2" wide x 2" long pieces of duct tape.
1. Use the pieces to tape the flat/longer wings of the camera holder to the ceiling of the cage top.
![img of 2nd taping](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num6.png)
1. Tape the USB wiring to the outside of the top of the lid so that it lays as flat as possible and the cage can slide in the rack.
1. Tape the USB wiring to the side of the Cage
![img of usb thing](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num7.png)
1. Connect the USB cable to the extension cable
![img of usb thing](https://github.com/KimchiLab/Camus/blob/main/Hardware/Figures/num%208.png)
1. Cover the USB connection with the cover, use 4 2-56 1/2 flathead screws to connect the sides of the connection cover, and make sure to secure firmly against the side of the cage using 2-3 strips of tape. **If this can wiggle, the camera will become disconnected and need to be unplugged and plugged back in. Please also make sure the USB cable goes over the USB cover rather than between the IVC rack and cage, as the pressure can cause it to disconnect**
1. If needed, loop second USB cable around the cage

## Installing the Camus System in the cage rack
1. Plug the extension cable into the computer. Make sure there is enough slack. 
1. More details/pictures forthcoming.

