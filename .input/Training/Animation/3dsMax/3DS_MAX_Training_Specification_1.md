# 3DS MAX Training Specification

# **🥅 Goal**

* To further improve on the necessary fundamentals for 3ds Max  
* To give the artist a general idea of what is to be expected of 3ds Max  
* To expose artists to basic technical skills that are fundamental to 3ds Max  
* To make it a habit for the artist to use self reference or video reference to better understand body mechanics


# **🎬 Style**

* Realistic exaggeration (Realistic body weight and physics but with exaggerated poses and timing)

# **💻 Pipeline Requirement**

* 3ds Max 2025  
* Keyframe Pro 1.15.1 (or higher)  
* QuickTime 7.7.9 (for Maya playblasting codec)  
* SkyChat  
* Google Chrome  
* Access to L Drive

# **📁 Folder Structure**

Generally, the folders can be divided into 2 directories, they are;

* LSATRG\_GENERAL\_PROJ  
* WIP

### **⭐ LSATRG\_GENERAL\_PROJ** 

* This directory is considered the **Master Directory**  
* Once the motion is considered approved, both maya and playblast files will be safely stored under their respective type of training for each individual artist for future references or as material for Lemon Sky’s Animation Reel


  **L:\\LEMONSKY\\LSATRG\_GENERAL\\WORKFILES\\LSATRG\_GENERAL\_PROJ\\05\_Anims\\GameAnim\_Training\\3dsMax\\\[ArtistName\]\\\[MotionName\]**


  ![][image1]


### **👷🏻‍♀️ WIP** 

* This directory is where all Work-In-Progress (WIP) files will go to under their respective artist name  
* Each respective motion folder should always have a Previews and WIP folder to store your working maya and playblast files  
* You may put the finalized and cleaned up files outside the folders so that it may be copied to the Master Directory


  


  #### **Playblast files**

  **L:\\LEMONSKY\\LSATRG\_GENERAL\\WORKFILES\\WIP\\05\_Anims\\GameAnim\_Training\\\[Software\]\\\[ArtistName\]\\\[MotionName\]\\\[Previews\]**


  #### **WIP Maya files**

  **L:\\LEMONSKY\\LSATRG\_GENERAL\\WORKFILES\\WIP\\05\_Anims\\GameAnim\_Training\\3dsMax\\\[ArtistName\]\\\[MotionName\]\\\[WIP\]**


**![][image2]**

# **💬 File Naming Conventions**

### **📔 Terminology Description for Level 1\~3**

**\[Character\]** 				➡ Name of character  
**\[WeaponType\]** 			➡ Fist | Dagger | Rapier | etc   
               *(Wp01 / Wp02 / Wp03 / etc)*  
**\[MotionType\]** 			➡ Idle | Locomotion | Attack | etc  
**\[MotionSubType\_Direction\]**	➡ Further description of the   
    MotionType with the intended      
    direction (Locomotion and   
    Attack will be shortened to Loc   
    and Atk)  
➡ **❕❕❕ Creatures do not need**   
     **to state the direction for**   
     **attacks ❕❕❕**  
➡ **Non-creature locomotion,**   
    **attacks and death will have**   
    **direction *(other motions will***   
    ***generally be facing***   
    ***to the front)***  
Attack has 9 directions 		➡ CL | CR | L | R | UL | UR | U |   
    DL | DR   
Locomotion has 8 directions 	➡ F | B | L | R | FL | FR | BL |   
    BR   
Death has 4 directions 		➡ F | B | L | R  
**\[Variation\]** 				➡ Variation of the motion  
**\[ClientVersion\]** 			➡ Versioning for the client side   
    *(VXXX eg. V001 )*  
**\[AnimationStage\]** 			➡ Blocking | Spline | Final *(BLK |*   
    *SPL | FNL)*  
**\[InternalRevision\]** 			➡ Versioning for internal   
     revisions *(RXXX eg. R001)*

The naming convention of both working maya file and working playblast should be as the following;

**\[Character\]**\_**\[WeaponType\]**\_**\[MotionType\]**\_**\[Motio**  
**nSubType\_Direction\]**\_**\[Variation\]**\_**\[ClientVersion\]**\_**\[AnimationStage\]**\_**\[InternalRevision\]**

Examples:  
**Lemon**\_**Wp00**\_**Idle**\_**Neutral**\_**00**\_**V001**\_**BLK**\_**R001**  
**Lemon**\_**Wp01**\_**Loc**\_**Walk\_F**\_**01**\_**V002**\_**BLK**\_**R010**  
**Lemon**\_**Wp02**\_**Atk**\_**Melee\_CR**\_**00**\_**V010**\_**BLK**\_**R004**  
**Sky**\_**Wp03**\_**Atk**\_**Slash\_DL**\_**00**\_**V003**\_**SPL**\_**R100**  
**Sky**\_**Wp04**\_**Skill**\_**Blizzard**\_**00**\_**V100**\_**SPL**\_**R200**  
**Sky**\_**Wp05**\_**State**\_**Death**\_**00**\_**V999**\_**FNL**\_**R999**  
**Sky**\_**Wp05**\_**Emote**\_**Happy**\_**00**\_**V100**\_**FNL**\_**R100**  
**Gamma**\_**Wp00**\_**Idle**\_**Neutral**\_**00**\_**V001**\_**BLK**\_**R001**  
**Gamma**\_**Wp00**\_**Loc**\_**Walk\_F**\_**01**\_**V002**\_**SPL**\_**R010**  
**Gamma**\_**Wp00**\_**Atk**\_**Slash\_00**\_**V010**\_**FNL**\_**R004**

**❕❕ For Master Files, please remove… ❕❕**  
**\[ClientVersion\]**\_**\[AnimationStage\]**\_**\[InternalRevision\]**

### **📗 Terminology Description for In-game Cutscene &**            **Character Intro/Outro**

**\[Character\]**\_**\[Title\]**\_**\[ClientVersion\]**\_**\[AnimationStage\]\_\[Internal**  
**Revision\]**

Examples:  
**Sky**\_**HeroIntro**\_**V001**\_**BLK\_R001**  
**Sky**\_**Ultimate**\_**V092**\_**SPL\_R400**  
**Lemon**\_**HeroOutro**\_**V999**\_**FNL\_R999**

**❕❕ For Master Files, please remove… ❕❕**  
**\[ClientVersion\]**\_**\[AnimationStage\]**\_**\[InternalRevision\]**

# **💿 Format**

3ds Max files 

* .max  
* 30 FPS  
* **❗❗❗ Start your motion at frame 0 ❗❗❗**

  Playblast files

* .mp4 (will need to stitch with Keyframe Pro)  
* 1920 x 1080 (HD 1080p)  
* 4 angles (perspective, front, side (left or right) and top)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>