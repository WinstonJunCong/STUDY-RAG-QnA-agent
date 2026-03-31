---
title: Import
url: https://en.esotericsoftware.com/spine-import
source: Spine User Guide
---

# Import

Spine project files and JSON or binary data can also be imported using the [command line interface](https://en.esotericsoftware.com/spine-command-line-interface).

Spine can import data from other Spine projects, allowing projects to be combined. Spine can also import data in the same JSON and binary formats that Spine exports, allowing skeletons to be imported from other programs, such as image editor [scripts](https://en.esotericsoftware.com/spine-images#Scripts).

# Project

Spine can import a skeleton or animation from another Spine project. This can be used to move skeletons from other projects into a single project. Importing an animation can be used to have multiple people working on the same project, with some limitations.

To open the import project dialog, choose `Import Project` from the main menu.

![Screenshot: Menu Project](https://en.esotericsoftware.com/img/spine-user-guide/import/menu-project.png)

Enter the path to the project file to import and choose to import a skeleton or animation.

![Screenshot: Import Project](https://en.esotericsoftware.com/img/spine-user-guide/import/import-project.png)

## Skeleton

After the skeleton is imported, some items can be dragged in the tree from one skeleton to another.

When importing a skeleton, choose which skeleton to import and the name to use for the imported skeleton.

![Screenshot: Import Skeleton](https://en.esotericsoftware.com/img/spine-user-guide/import/import-skeleton.png) 

## Animation

An animation can be imported into a completely different skeleton, as long as it uses the same name for at least some bones and other items.

When importing an animation, choose which skeleton and animations to import, then the skeleton to which they will be imported.

![Screenshot: Import Animation](https://en.esotericsoftware.com/img/spine-user-guide/import/import-animation.png)

The skeleton that the animations are imported into must have bones, slots, attachments, events, and constraints with the same names as the skeleton that is being imported from, but only for those items that are actually keyed in the animations being imported. Additionally, for [deform keys](https://en.esotericsoftware.com/spine-keys#Deform-keys), the mesh must have the same number of vertices in both skeletons.

If the skeleton is missing items keyed by an animation, the animation is imported without those keys and warnings are shown for the missing items.

# Data

You can import data into Spine from an image editor [script](https://en.esotericsoftware.com/spine-images#Scripts), continue working in your image editor, and later import newer data into the same skeleton.

Spine can import data in the [JSON](https://en.esotericsoftware.com/spine-json-format) or [binary](https://en.esotericsoftware.com/spine-binary-format) formats that it [exports](https://en.esotericsoftware.com/spine-export). This provides a path to bring data from other programs into Spine, such as from image editor [scripts](https://en.esotericsoftware.com/spine-images#Scripts).

It can be useful to recreate a Spine project from JSON or binary data and a texture atlas. To do that, see the [Importing skeleton data](https://en.esotericsoftware.com/blog/Importing-skeleton-data) blog post.

To open the import data dialog, choose `Import Data` from the main menu.

![Screenshot: Menu Data](https://en.esotericsoftware.com/img/spine-user-guide/import/menu-data.png)

Enter the path to the JSON or binary file to import, or the folder where they are located, and a name for the imported skeleton.

![Screenshot: Import Data](https://en.esotericsoftware.com/img/spine-user-guide/import/import-data.png)

## Scale

For example, if a Spine project is created with images that are 4 times larger than necessary, it can be exported to JSON with `Nonessential` checked, then imported to a new project with a scale of 0.25. The images used for the new project should be 25% the size of the original images.

The import data `Scale` changes the size of the skeleton without changing the scale of any bones. All the data is scaled: the position and length of bones, attachment offsets, bounding boxes, meshes, animations, etc. 

If a Spine project was created with images that are the wrong size, the project can be [exported](https://en.esotericsoftware.com/spine-export#JSON) to JSON with `Nonessential` checked and then imported again using `Scale` to change the size of the skeleton. The new project would then use images with a different size.

## New project

When checked, the data will be imported into a new project.

When unchecked, the data will be imported into the current project and more options appear.

![Screenshot: Import Data Existing](https://en.esotericsoftware.com/img/spine-user-guide/import/import-data-existing.png)

### Create a new skeleton

When checked, the data is imported into the current project as a new skeleton.

### Import into an existing skeleton

When checked, the data is imported into the chosen skeleton in the current project. This imports bones, slots, skins, and attachments, but not animations. It is primarily for importing data from [scripts](https://en.esotericsoftware.com/spine-images#Scripts). To import animations into an existing skeleton, use [project import](https://en.esotericsoftware.com/spine-import#Animation).

### Existing attachments

If the skeleton already contains an item from the data:

- When `Ignore` is checked, it is left as is. This preserves any changes that may have been made to the item.
- When `Replace` is checked, it is replaced with the item from the data.


## Nonessential data

When JSON or binary data is exported and the [Nonessential data](https://en.esotericsoftware.com/spine-export#Nonessential-data) setting is checked, extra information is exported which is not normally used at runtime. If the data is later imported back into the Spine editor, that extra information is used to configure the imported skeleton.

If JSON or binary data is exported without `Nonessential data` being checked and is later imported back into the Spine editor, then the import will succeed but some information may be lost.

For example, the color of a bounding box is not normally needed at runtime, so it is only exported when `Nonessential data` is checked. If that exported data is imported back into the Spine editor, the bounding box will have a default color.

For mesh attachments, the manual (orange) [edges](https://en.esotericsoftware.com/spine-meshes#Edges) inside the mesh hull are nonessential data. If `Nonessential data` is not checked when the mesh is exported and that exported data is imported back into the Spine editor, the mesh will not have any manual edges. The triangulation of the mesh from when it had manual edges is preserved. If [edit mesh](https://en.esotericsoftware.com/spine-meshes#Edit-Mesh) is used to modify the mesh, a new triangulation will be computed.
