
# LS Rigging Tools Documentation
<center> LAST UPDATED
<br>
Author - Robin Koh Li Wen, May 6, 2025
<br>
Collaborators - Anis | Wen Hong | Sumesh</center>

# **🦴 LsRigTools**

- The LsRigTools shelf caters towards rigging for projects

> ![](../Images/LS_Rigging_Tools_doc/media/image19.gif)

## ![](../Images/LS_Rigging_Tools_doc/media/image12.png) **List Duplicate Names**

- It will basically list out duplicate names in the script editor

  - If there are no duplicate names, it will not be shown in the script editor

> ![](../Images/LS_Rigging_Tools_doc/media/image15.gif)

## ![](../Images/LS_Rigging_Tools_doc/media/image25.png) **Fast Renamer**

- Allows the selection to be renamed either based on hierarchy or by individual selection

  - Able to change prefix and suffix

> ![](../Images/LS_Rigging_Tools_doc/media/image17.gif)

- Able to find and replace a specific name

> ![](../Images/LS_Rigging_Tools_doc/media/image33.gif)

- Able to change the base name of the selection as well as the counter values & padding

> ![](../Images/LS_Rigging_Tools_doc/media/image32.gif)

- Able to change uppercase and lowercase of the name

> ![](../Images/LS_Rigging_Tools_doc/media/image6.gif)

- If all else fails for some reason, Maya has a default option for you to perform the same action in a more basic manner

> ![](../Images/LS_Rigging_Tools_doc/media/image24.png)

## ![](../Images/LS_Rigging_Tools_doc/media/image34.png) **IK Spline Setup (can remove according to Anis)**

> ![](../Images/LS_Rigging_Tools_doc/media/image8.png)

- Creating a IK Spline rig

## ![](../Images/LS_Rigging_Tools_doc/media/image20.png) **Pin Locator to Curve**

- Normally used for eyes and props

  - Eg. a locator will basically follow the curve

> ![](../Images/LS_Rigging_Tools_doc/media/image18.gif)

## ![](../Images/LS_Rigging_Tools_doc/media/image7.png) **Transfer UV/Shader**

> ![](../Images/LS_Rigging_Tools_doc/media/image2.png)

- More towards modeling tool

  - Takes the unfinished model to be rigged first (while waiting for the model to be completed)

  - Once the model is done, then the UV is transferred to the finished rigged model

## ![](../Images/LS_Rigging_Tools_doc/media/image30.png) **DJ Rivet \| Rivet**

- DJ Rivet - creates a follicle and constrains controller to mesh

- Rivet - creates a locator on the edge/face and attaches to the mesh

- Maya default Rivet - creates a UV pin

## ![](../Images/LS_Rigging_Tools_doc/media/image13.png) **SHIFT \| EDIT \| TRANS attribute**

- Shift Attribute (shifting the arrangement of the attribute)

- Edit Attribute (could be the same default edit attribute in maya)

- Transfer Attribute (refer pic below)

> ![](../Images/LS_Rigging_Tools_doc/media/image41.png)![](../Images/LS_Rigging_Tools_doc/media/image4.png)

- Transfer attribute from one ctrl to another

## ![](../Images/LS_Rigging_Tools_doc/media/image43.png) **CREATE \| PARENT \| SPLIT**

### **Create Joint**

### ![](../Images/LS_Rigging_Tools_doc/media/image3.png)

- Very straight forward in how to create a joint base on the 4 options given

### **Parent Joint**

- Very straight forward in setting up the parent and child in the joint order

> ![](../Images/LS_Rigging_Tools_doc/media/image35.gif)

### **Split Joint**

> ![](../Images/LS_Rigging_Tools_doc/media/image42.png)

- When the Start Joint is selected, it will auto detect the end joint

> ![](../Images/LS_Rigging_Tools_doc/media/image40.png)

- To add inbetween joints, change the joint quantity and hit Split Joints

> ![](../Images/LS_Rigging_Tools_doc/media/image14.gif)

- If it was set to independent, the inbetween joint created will not be part of the hierarchy

> ![](../Images/LS_Rigging_Tools_doc/media/image23.gif)

## 

## ![](../Images/LS_Rigging_Tools_doc/media/image10.png) **Override Colour**

- Changes the colour of the curves

> ![](../Images/LS_Rigging_Tools_doc/media/image28.png)
>
> ![](../Images/LS_Rigging_Tools_doc/media/image22.gif)

## ![](../Images/LS_Rigging_Tools_doc/media/image16.png) **Wire Controllers**

- A simple click and a controller is created

> ![](../Images/LS_Rigging_Tools_doc/media/image11.png)

## ![](../Images/LS_Rigging_Tools_doc/media/image44.png) **Lock 'n Hide**

> ![](../Images/LS_Rigging_Tools_doc/media/image36.png)
>
> ![](../Images/LS_Rigging_Tools_doc/media/image38.gif)

- Mainly for locking and hiding the attributes

## ![](../Images/LS_Rigging_Tools_doc/media/image9.png) **Controller Mirror UI**

> ![](../Images/LS_Rigging_Tools_doc/media/image21.png)

- Literally mirrors curve shapes to the other opposing side

## ![](../Images/LS_Rigging_Tools_doc/media/image27.png) **Joint Orient**

- Orient joints based on project requirements

## ![](../Images/LS_Rigging_Tools_doc/media/image29.png) **Z Up/Down**

- Changes the Z orientation upwards or downwards

  - Mainly for game engines

## ![](../Images/LS_Rigging_Tools_doc/media/image39.png) **Rename**

- Rename controllers/joints

- Very similar to Fast Rename

- Search and Replace (make sure to select the hierarchy and the name of what you want to change and the final output name)

## ![](../Images/LS_Rigging_Tools_doc/media/image1.png) **Save Weights (not applicable/working - can remove)**

## ![](../Images/LS_Rigging_Tools_doc/media/image26.png) **Skin Weights (not applicable/working - can remove)**

## ![](../Images/LS_Rigging_Tools_doc/media/image5.png) **Skin As**

- Transferring the skinning of a mesh to another mesh that has no joints

## ![](../Images/LS_Rigging_Tools_doc/media/image37.png) **Spline Weight Skin Tool**

- Refer to [https://arturocoso.gumroad.com/l/SplineWeights](https://arturocoso.gumroad.com/l/SplineWeights)

- Tutorials :

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1053249940?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="01 - Installation"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

<div style="padding:54.69% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1053252450?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="02 - Introduction"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1053257452?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="03 - leg_skin"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

<div style="padding:54.69% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1053289672?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="04 - arm_skin"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

<div style="padding:54.69% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1054022900?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="05 - neck_skin"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

<div style="padding:54.69% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1054031864?badge=0&autopause=0&player_id=0&app_id=58479/embed" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe></div>

<!-- -->

- Paid script (one time)

## **ngSkinTools**

- Refer to [https://www.ngskintools.com/](https://www.ngskintools.com/)

- Paid script

## 
