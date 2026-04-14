# **LsToolsNuke Documentation**

- Make sure you are opening Nuke from PROJECT nuke provide by Tech team (ZunAo)

    ![](../Images/LsToolsNuke_Doc//media/B9J2QCQSLP5VD0U5B500PKET40.png)

- Always check on your viewport color lookup, its needs to be sRGB (ACES)

    ![](../Images/LsToolsNuke_Doc//media/J7NDOP9UPP2KH75U4M3M3TP92K.png)

- All png and mattepaint / cyc footage require changing colorspace to ( Output - sRGB )

    ![](../Images/LsToolsNuke_Doc//media/R19NIFEST13IJ33K9M7VTCNCBO.png)

    ![](../Images/LsToolsNuke_Doc//media/QM9BHDQKTH1IF53P95JR0OEQJC.png)

- EXR footage from maya render require changing colorspace to ( scene_Linear )

    ![](../Images/LsToolsNuke_Doc//media/A08JLEU3TH7DJ4V93C4S9G65SC.png)

- Remember to always localized your shot to reduce lag

- Base comp can be found inside PROJECT\>tool\>example

    ![](../Images/LsToolsNuke_Doc//media/JEKGOEMMBD38JDEP251TLOLHES.png)

- We have custom make tool for comp, try use these tools only

    ![](../Images/LsToolsNuke_Doc//media/3CLLCNFDAL6OP4LQM2E2AUUO24.png)

- AovAdjustment is for light adjust, select the aov light to adjust

- Atmosphere is fog

- DepthCC is creating a mask using zdepth data

- P3DMatte is same with matte3D

- SpecularGlow need to change input specular setting to ( specular_key )

- Tools for comp, found on top of each PROJECT nuke file, each option will open up the folder location<br>
<br>

## **Project Related Tabs**

![](../Images/LsToolsNuke_Doc//media/B7O5Q0TE9D47976493UBDHEVAO.png)

- **Open Local Comp** Shot - key in the shot number and it will auto open up the comp file that you check out from Lemoncore

- **This Comp Folder** - this will open up this shot comp folder in your local drive

- **RenderOutput Folder** - this will open up the maya rendered imagine inside server folder

    ![](../Images/LsToolsNuke_Doc//media/APAB7U0KED45DCTS9ONJH1IK94.png)

- Use this to send nuke file to farm for output ( not all project works )

- Not all the tools here is use, only use it when needed

    ![](../Images/LsToolsNuke_Doc//media/L6C1DTQH1D7CT9MBFIEB6NF9MO.png)

- Print Footages - use this to clean nuke file path for clean up files, usually do this after the shot is approve by client

- Cleanup This Nuke File - this usually can fix all your dirty nuke file path, path no relative, not linked to server etc etc

- Localize using Robocopy - a fast localize plug in to use rather then the default nuke way

- Update ToolSets - this will help you get the new ToolSets created by key artist thats in server
