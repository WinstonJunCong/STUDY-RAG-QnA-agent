---
title: Settings
url: https://en.esotericsoftware.com/spine-settings
source: Spine User Guide
---

# Settings

Spine provides many settings to customize its behavior.

To open the `Settings` dialog, press `F12` or open the main menu by clicking the Spine logo in the upper left and choose `Settings`.

![Screenshot: Menu](https://en.esotericsoftware.com/img/spine-user-guide/settings/menu.png)

![Screenshot: Settings Dialog](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-dialog.png)

# Application

## Launcher

![Screenshot: Settings Launcher](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-launcher.png)

These settings affect the launcher, before a version of the Spine editor is started.

| Setting | Description |
| --- | --- |
| Version | Sets the Spine editor version to use the next time Spine starts. This is the same aschoosing a versionon the Spine launcher dialog.The select box shows all versions you have downloaded. You can clickOther...and type the version number forany versionwe've ever released.Seeversioningfor more information. |
| Start automatically | When checked, the Spine launcher will start the version of the Spine editor that was last used.When unchecked, the Spine launcher stops to allow a version to be chosen. Clicking anywhere in the Spine launcher window when it first appears will prevent it from starting automatically. |

## Files

![Screenshot: Settings Files](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-files.png)

These buttons open the corresponding folder when clicked.

| Setting | Description |
| --- | --- |
| Backups | This folder contains copies of project files made just before each save. Also, ifauto backupis enabled, copies of the project file are saved periodically.Windows: <user home folder>\Spine\backupsMac: <user home folder>/Library/Application Support/Spine/backupsLinux: <user home folder>/.spine/backups |
| Hotkeys | This text file contains all of Spine's hotkeys. The file can be edited to customize the hotkeys to your liking. Seekey namesfor a list of the key names that can be used.When new hotkeys are added to Spine, they are added to the hotkeys file.Windows: <user home folder>\Spine\hotkeys.txtMac: <user home folder>/Library/Application Support/Spine/hotkeys.txtLinux: <user home folder>/.spine/hotkeys.txt |
| Log | Thespine.logfile is written each time Spine starts. It may provide more details in case something goes wrong.Windows: <user home folder>\Spine\spine.logMac: <user home folder>/Library/Application Support/Spine/spine.logLinux: <user home folder>/.spine/spine.log |

## General

![Screenshot: Settings General](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-general.png)

These settings affect the entire application.

| Setting | Description |
| --- | --- |
| Color management | When unchecked, colors are rendered to the monitor using sRGB using gamma blending. Most monitors use sRGB.When checked, the monitor's color profile is used to render accurate colors. This is useful for monitors that use wide gamut colors or an ICC color profile other than sRGB. Enabling color management uses slightly more GPU resources.When enabled, blending can be done in either gamma or linear space. Images are generally saved in gamma space and most game toolkits perform blending in gamma space because it requires less effort, even though the results are less accurate. When using linear blending at runtime, choosing linear blending allows you to see blending in Spine exactly as it will render at runtime.Color management is not available for Linux. |
| Editor frame rate | Sets the maximum frames per second that Spine can render at. Generally it should be set to the refresh rate of your monitor. This setting does not affect thetimeline FPS.Spine only renders when necessary, which is usually much less often than the editor frame rate, except when playing animations.The editor frame rate may be overridden by GPU settings. |
| Reuse instance | When checked, if a file is opened via an OS file explorer, it is opened in an existing Spine instance, if one is running.When unchecked, a new Spine instance is started to open the file.This setting is not available for Mac, where double clicking a file always reuses an existing Spine instance if possible. To open multiple instances of Spine on Mac, this command can be used:open-n-a/Applications/Spine.app |
| Show FPS | When checked, the editor framerate is shown in the title bar as frames per second during animation playback. When not playing an animation, the FPS is not shown. |
| Welcome screen | When checked, Spine will show thewelcome screenon startup.When unchecked, Spine will open the last opened project on startup. The welcome screen can still be accessed by clicking the mail button in Spine's titlebar: |

# User interface

![Screenshot: Settings User Interface](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-user-interface.png)

These settings affect all of Spine's views and other parts of the [user interface](https://en.esotericsoftware.com/spine-ui).

| Setting | Description |
| --- | --- |
| Language | The language of the Spine user interface. It is set by default to the OS language, if possible. |
| Font | Sets the font used by Spine's user interface. Some language require their own font.Bitmaprenders very efficiently, but supports only Latin, Greek, and Cyrillic characters and is available only for the medium and large font sizes.Unicodetakes slightly more GPU resources but supports all sizes and has glyphs for most languages.When the language is set to Chinese, Japanese, or Korean, the corresponding font should be used. |
| Font size | Sets the font size used by Spine's user interface. Smaller font sizes allow more to be fit on screen at once, but may be harder to read. TheBitmapfont is limited to the medium or large sizes. |
| Default timeline FPS | Sets the defaulttimeline FPSfor new projects. |
| Interface scale | Scales Spine's entire user interface larger or smaller. This allows the user interface to be a comfortable size for the size of monitor you are using.When set higher than 100%, Spine uses 2x graphics so the user interface stays looking sharp. Scales other than 100% or 200% may appear less sharp. |
| Row height | Sets the height of each row in the dopesheet and graph. The default setting is the most visually appealing, but more rows can be shown at once with a smaller setting. |
| Toolbar position | Allows customizing the toolbar position to maximize the usable editor space for your window size by placing themain toolbaron the left, center, or right. |
| Toolbar text labels | The text labels on themain toolbarcan be hidden to take up less space.Automatichides them when the main toolbar no longer fits in the viewport. |
| Tree indentation | The amount in pixels to indent tree nodes in thetree viewhierarchy. Lower indentation allows more to be shown in the tree horizontally, but makes it less obvious which tree nodes are underneath others. |

# Viewport

![Screenshot: Settings Viewport](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-viewport.png)

These settings affect rendering of the skeletons and tools in the [viewport](https://en.esotericsoftware.com/spine-ui#Viewport).

| Setting | Description |
| --- | --- |
| Background | Sets the colors and patterns to use for the editor background. The alpha can be set to zero for some colors to hide that part of the background, such as the gradient.When doing screen capture to a lossy format, like GIF, it can be helpful to use a solid background color. |
| Backface culling | When unchecked, all triangles are drawn.When checked, triangles facing away from the screen are not drawn. This can be useful to hide portions of a mesh that are not facing the screen. The same effect can be enabled in some game toolkits. |
| Bone scale | Scales the size of the bones and zoom levels so they better match the size of the skeletons. This is helpful when working with very small or very large skeletons. |
| Color bleed | When greater than zero, when images are loaded color bleeding is performed to copy neighboring colors into transparent pixels. This prevents artifacts when downscaling, meaning when the images are zoomed out or otherwise displayed smaller than their actual size. Higher values increase image loading time but may be needed when downscaling a large amount. |
| Dim unselected skeletons | When checked and a project has multiple skeletons, skeletons that are not selected are drawn with more dimly. This can reduce clutter if many skeletons are visible at once. |
| Highlight attachments | When checked, edges of attachment images are highlighted when hovered or selected. When images have a lot of translucency, this may make the images difficult to see. |
| Highlight smoothing | When checked, the attachment highlight is smoothed when zoomed in.When unchecked, the attachment highlight is pixelated when zoomed in. This may be desirable when working with pixel art. |
| Missing images | When checked, a red "missing" image is displayed when an image cannot be found for region and mesh attachments.When unchecked, the image is shown as black. |
| Multisample anti-aliasing | When checked, Spine will use multisample anti-aliasing. This doesn't effect most of Spine's rendering but provides antialiasing when amesh edgeorclippingcuts through an image.GPU support for the chosen MSAA setting is required, else it will have no effect. |
| Pixel grid | When checked, the viewport rendering is rasterized to simulate pixel art. When enabled, the rendering for each skeleton is limited to 2048x2048. |
| Smoothing | Sets the smoothing to apply to images in the viewport. Smoothing is a way of blurring the image to hide the pixel structure when upscaling, meaning when images are zoomed in or otherwise displayed larger than their actual size.0 disables smoothing, nearest neighbor filtering is used. This can be useful for pixel art.1-10 uses linear filtering between 10% and 100%.11 uses bicubic filtering. This may be sharper and preserve details slightly better than linear filtering.WhenAnisotropic filteringis checked, the quality when downscaling images is improved. When enabled, 33% more GPU memory is required for each image that is loaded. This settingaffects exports.WhenKeep edgesis checked, smoothing is not used for translucent pixels. This allows the edges of an image to be seen clearly while still using smoothing for the rest of the image. |

# Behavior

![Screenshot: Settings Behavior](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-behavior.png)

These settings affect the behavior of Spine's user interface.

| Setting | Description |
| --- | --- |
| Automatic backup | When checked, the project is saved periodically in thebackup folder, if it has changes since the last save. This is normally very fast, but for extremely large projects this may introduce unwanted pauses and can be disabled. |
| Delete confirmation | When unchecked and you choose to delete an item, Spine will no longer ask if you are sure you want to delete it. If an item is deleted accidentally, you can always use undo by pressingctrl+Z(cmd+Zon Mac). |
| Double click shortcuts | Spine uses double click for a number of optional shortcuts, for example to rename an item in the tree or deselect in the viewport. When unchecked, those shortcuts are disabled. This can be useful when using a pen tablet, where it may be easy to accidentally double click. |
| Interface animations | When unchecked, Spine will not use animations in the user interface. This means menus will not open using an animation, dialogs will not fade in, etc. |
| Middle mouse pans | When unchecked, the middle mouse button is used to make a new selection, regardless of the current selection. This is the default.When checked, the middle mouse button is used for panning instead. This can be useful if coming from other software that uses the middle mouse button to pan. |
| Pan momentum | When checked, panning a large amount continues for a very short amount of time to make the movement smoother.When unchecked, panning always stops abruptly. |
| Smooth scrolling | When checked, scrollbars are animated smoothly when scrolled instead of jumping instantly into position. |
| Tooltips | When unchecked, tooltips will not be shown by hovering the mouse. Tooltips can still be shown on demand by pressingF1. |
| Zoom to mouse | When checked, the mouse wheel orZoomhotkey (Uby default) will zoom in/out using the mouse cursor location. This is usually a very natural way of zooming, but may not work well for a pen tablet or touchpad/trackpad.When unchecked, zooming in/out uses the center of the viewport. |

## Dopesheet

![Screenshot: Settings Dopesheet](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-dopesheet.png)

These settings affect the behavior of the [dopesheet view](https://en.esotericsoftware.com/spine-dopesheet).

| Setting | Description |
| --- | --- |
| Box select pause | When checked, a brief pause is required after selecting to prevent the selection box from disappearing. |
| Jump to frame | When checked, the timeline position is set when empty space is clicked in the dopesheet. |
| Jump to key | When checked, the timeline position is set to the key's frame when a key is clicked in the dopesheet. |

## Graph

![Screenshot: Settings Graph](https://en.esotericsoftware.com/img/spine-user-guide/settings/settings-graph.png)

These settings affect the behavior of the [graph view](https://en.esotericsoftware.com/spine-graph).

| Setting | Description |
| --- | --- |
| Drag to edit | When checked, dragging in empty space manipulates the graph selection. Like in the viewport, this reduces fatigue from using the mouse to animate for long hours.When unchecked, keys and curve handles in the graph must be dragged to manipulate them. |
| Jump to frame | When checked, the timeline position is set when empty space is clicked in the graph. |
| Jump to key | When checked, the timeline position is set to the key's frame when a key is clicked in the graph. |
