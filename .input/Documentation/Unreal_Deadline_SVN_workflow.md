# Workflow for Unreal to Deadline with SVN

## How to start using the workflow

Run INSTALL-artist.bat, a desktop shortcut will present itself after the installation.  
Run INSTALL-pipeline.bat for creating the project folder.  
In UE, setup the deadline workflow by reading the **Using Deadline in Unreal Engine 5** documentation.

## Project Folder

### Plugins

#### Unreal Engine 5.++

- Check-out project folder.   
- Working copy path should be pre-defined for each project.  
- Each user's first checkout should be a clean copy from the repository branch.  
- Shots build should be done with SVN’s switch function.  
- Start Unreal Engine with the .bat file that came along in the folder.  
- The workflow for enabling submission to deadline **in Using Deadline in Unreal Engine 5.**

#### Deadline Monitor

- Once a job is sent to deadline, there should be a post job in the task queue.  
- This post-job script is to switch the render node’s working path back to the previous url.  
- Ensure that the job is complete or else, re-queue the post task.

#### .json

1. ue5_deadline_pool  

- ./.json/ue5_deadline_pool.py  
- This file is created to define which are the user only, render only and hybrid pc in the render group. This data is important to run the pre_task_svn.py file.

2. url.json/txt  

- ./.json/url.json-.txt  
- These files store the url of the current working copy. The Json file is needed for Data Asset to define the Extra Key/Value pair, “URL”.

### DeadlineSVN

1. #### Pre_task_svn.py

- Write a **system_url** to \<USER\>/.deadline\_prerender folder. This callback file saves out the user url before the svn switch to render url  
- Read the `ue5_deadline_pool` to look for a machine-user node.  
- Parse an update in the `working copy` to align with the latest version.  
- Add for new files that are not in the url before a commit.   
- Commit to the repository.   
- Switch to the render url

2. #### Post_job_svn.py

- Read the **system_url** to retrieve the user url to perform a switch back.  
- Parse a clean-up of the `working copy`.  
- Revert to the last commit version.  
- Switch to switch back to user url  
- Clean-up after switch.

### Remote Executor folder

There is an integrated remote executor in the pre_task_svn.py script.This function acts as a remote save and close for render node side. 

1. **modify_default_engine_ini.py  **

- Python script to modify project engine’s ini file.   

2. **remote_execute_to_ue5.py ** 

- Python script to send files to Unreal Engine 5.  

3. **remote_execution.py**  

- Python script containing RemoteExecution classes to send files into Unreal Engine.  

4. **Save_and_quit_ue5.py**

- Python script to save all and close Unreal Engine. The UE5 app should adhere to the `plugin_configs` for the execution to work. 

### StartUp

1. **startup_ui.py**

- UI functions for project launcher  
- Setup project attribute in UE5 before app launch.
- Run SVN commands for branch add, switch, commit if user changed branch directory.

### UnrealDeadlineService

1. ##### Remote_executor

- ./MoviePipelineDeadline/Content/Python/remote\_executor.py  
- This python file has been modified to execute commands for svn before the project is submitted to the render queue.

2. ##### DeadlineJobDataAsset

- ./UnrealDeadlineService/Source/DeadlineService/Private/DeadlineJobDataAsset.cpp  
- This file has been modified to include the pre\_task and post\_job for Deadline.  
- This file has been modified to include “Working Copy” and “URL” key/value for Deadline.

### Plugin_config

- This file contains all the constant values that can be set for each project.

## Compile Data Asset

- Assign values to data asset default attribute.  
- The commandline to compile is:
  - ./RunUAT BuildPlugin -plugin=\<*/UnrealDeadlineService.uplugin\> \-package=\<folder\_to\_output\_build\>  
- This output should reside in the project Plugins folder.  
- To change the preset of Data Asset or any other Unreal Deadline Interface, the plugins folder will need to be re-compiled.

# Local Folder

## Deadline Folder

### Deadline_prerender folder 

1. system_url.data

- This callback data file is to store the `user URL` for deadline post_job to retrieve after the render is done.

# Legend

#### 1 .Working copy  {#1-.working-copy}

- Local path

#### 2. Clean copy 

- Copy of the project folder in the branch that is not modified and is in sync with the trunk

#### 3.Trunk copy 

- Trunk copy is the master copy of the project. 

#### 4. SVN commands

- **Switch**   
- Update the working copy to mirror a specified URL within the repository.  
- **Checkout**  
	- Check-out to a working copy from a repository.  
- **Update**  
	- Bring changes from the repository into the working copy.  
	- If no revision is given, bring working copy up-to-date with HEAD rev.  
 	 Else synchronize working copy to revision given by \-r.

- **Commit**  
	- Send changes from your working copy to the repository.  
	
- **Revert**  
	-  Restore pristine working copy state (undo local changes).  
	- **Merge**   
		- Merge changes into a working copy.  
	- **Add**  
		- Put new files and directories under version control.  
	