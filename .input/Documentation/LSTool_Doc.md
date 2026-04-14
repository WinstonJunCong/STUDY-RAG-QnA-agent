# **LS Tool Documentation**


## **Introduction** 

- LSTool is Lemonsky's homegrown one stop shot setup script which we will be using for almost all production projects to help artist shorten the setup time for each shot.

- **Remarks: Note that tools on other tabs may change based on the project you are working in. This doc will go through the general tools in the tool set.**

- The toolbar will be set up for each individual project and will generally look like this at it's very base.

![](../Images/LSTool_Doc//media/ITU20Q7J1L3T3COBT1V26EL9HK.png)



## **Where to Find LS Tool**

- Go to <LSA Pipeline 2025\> - <Tool Shelves\> - <LsAssyTools\> .

![](../Images/LSTool_Doc//media/U6QSDE4KOL5NJCF2KIC3QGMC40.png)


- You should see the Toolbar appear on your MAYA toolbar

![](../Images/LSTool_Doc//media/J57IFAKI8P1VT65L6CQJ4LRTIK.png).<br>
<br>

## **Main Functions Explained** 

![](../Images/LSTool_Doc//media/55C2CNFRVP1H5BIQT6EBA8J3M4.png)

### **1. Fix Color Management**

- Adjusts your color management to the required settings based on the project you are on.<br>
<br>

### **2. Set Vray as Renderer**

- Automatically help u set the correct renderer based on project. In this case here it is VRay but it may vary based on your project.<br>
<br>

### **3. Remove all Unknown Required Plugins**

- Deletes all un-required plugins that may be still embedded into any files.

![](../Images/LSTool_Doc//media/MH9GQK9E8D1GN0KONOGUSVAVPC.png)<br>

### **4. Extend Far Clip Plane**

- Increases the cameras far clip so there is no cutting in the viewport<br>
<br>

### **5. Hide All Image Planes**

- Hides all image planes inside the camera.<br>
<br>

### **6. Load Light Rig References**

- Loads all related light rigs into the shot .e.g. CH, Set, Props light rigs.<br>
<br>

### **7. Load Set FX References**

- Loads any built in Set FX such as water fx etc. If the FX is not needed in the shot you will need to go to the reference editor and turn them off.<br>
<br>

### **8. Load Set Grass References**

- Loads all Grass References of the set.<br>
<br>

### **9. Load Set 2DCYC or 3DCYC Reference**

- Loads any 2D/3D CYC referenced in the set.<br>
<br>

### **10. Disable Display Layer Override**

- Disables any overrides which may have been set in the display layer. Most of the time there won't be any overrides here.<br>
<br>

### **11. Setup Render Elements**

- Sets up the preset render render elements for your Vray project. For Arnold projects this most likely will be altered to setup the needed AOVs instead.<br>
<br>

### **12. Setup Render Settings**

- Sets up the basic render settings for your project.<br>
<br>

### **13. Set Playback Frame Range as Render Frame Range**

- Takes the frame range on the anim slider and sets it as your current shots frame range.<br>
<br>

### **14. Switch GeoRes and EyeRes to HiRes**

- Switches GeoRes of your assets from Proxy to HiRes versions.

![](../Images/LSTool_Doc//media/DRG19BJQ6L2HBAPT9TNKMDG51O.png)

### **15. Break Connections of Eye_Spec_CTRL**

- We can ignore this function as we do not have any Eye_Spec_Ctrl nodes in our assets.<br>
<br>

### **16. Set Render Camera**

- Helps to set the render camera in your render settings to the shot camera.<br>
<br>

### **17. Post Initial Setup**

- This tool is mostly not needed at the current time<br>
<br>

### **18. Enable SET Subdivision**

- This tool is mostly not needed at the current time<br>
<br>

### **19. One Click Setup**

- Runs all the above processes in one click, this will mostly be what you will be using for all your shots.
