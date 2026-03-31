---
title: Point attachments
url: https://en.esotericsoftware.com/spine-points
source: Spine User Guide
---

# Point attachments

A point [attachment](https://en.esotericsoftware.com/spine-attachments) is a point in space with a rotation. It can be used to spawn particles or anything else that involves a position and/or rotation.

![Screenshot: Point](https://en.esotericsoftware.com/img/spine-user-guide/point-attachments/point.png)

Like any other attachment, a point attachment can go in a [skin](https://en.esotericsoftware.com/spine-skins). This allows each skin to have its own point attachments, so the position and rotation can change for different skins. For example, different guns may shoot from different positions.

Alternatively, a bone could be used instead of a point attachment, since a bone also has a position and rotation and bones can also go in a skin. However, bones have other features like scale or shear that require a little more processing at runtime.

The point attachment position and rotation cannot be keyed in animations. Instead, the point attachment's bone can be [keyed](https://en.esotericsoftware.com/spine-keys#Bone-transforms).

# Setup

To create a new point attachment, select a bone or slot in the tree, then choose `New...` `Point` in the tree properties.

![Screenshot: New](https://en.esotericsoftware.com/img/spine-user-guide/point-attachments/new.png)

Like any other attachment, multiple point attachments can be under the same slot. This can be used for animations or code at runtime to choose from multiple positions.

![Screenshot: Multiple](https://en.esotericsoftware.com/img/spine-user-guide/point-attachments/multiple.png)

# Properties

![Screenshot: Properties](https://en.esotericsoftware.com/img/spine-user-guide/point-attachments/properties.png)

See the [common attachment properties](https://en.esotericsoftware.com/spine-attachments#Common-properties) for the `Select`, `Export`, `Name`, `Color`, and `Set Parent` properties.
