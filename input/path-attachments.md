---
title: Path attachments
url: https://en.esotericsoftware.com/spine-paths
source: Spine User Guide
---

# Paths

A path [attachment](https://en.esotericsoftware.com/spine-attachments) is a composite Bézier spline. It is made up of "knots" which are vertices on the path, and "handles" which are vertices that control the curve of the path between knots.

![Screenshot: Path](https://en.esotericsoftware.com/img/spine-user-guide/paths/path.png)

Paths can be used with [path constraints](https://en.esotericsoftware.com/spine-path-constraints) to position bones along the path.

Paths can be deformed automatically when bones are transformed by using [weights](https://en.esotericsoftware.com/spine-weights). For best results, typically the knot and both handles are given the same weights.

Path vertex positions can be [keyed](https://en.esotericsoftware.com/spine-keys#Deform-keys) in animations.

# Setup

To create a new path, select a bone or slot in the tree, then choose `New...` `Path` in the tree properties.

![Screenshot: New](https://en.esotericsoftware.com/img/spine-user-guide/paths/new.png)

The new path appears in the tree and [edit mode](https://en.esotericsoftware.com#Edit-mode) opens automatically. The [new vertices mode](https://en.esotericsoftware.com#New-vertices-mode) inside of edit mode is also automatically selected.

# Properties

![Screenshot: Properties](https://en.esotericsoftware.com/img/spine-user-guide/paths/properties.png)

See the [common attachment properties](https://en.esotericsoftware.com/spine-attachments#Common-properties) for the `Select`, `Export`, `Name`, `Color`, and `Set Parent` properties.

## Length

The total length of the path is shown. To change the length, move the path vertices in the viewport.

## Closed

When checked, the first and last knots are connected.

![Screenshot: Closed](https://en.esotericsoftware.com/img/spine-user-guide/paths/closed.png)

When unchecked, the first and last knots are not connected.

When an open path is selected, dashed lines at both ends of the path show the direction the path is pointing. This can be useful when a path constraint position is less than `0%` or greater than `100%`.

![Screenshot: Path Open](https://en.esotericsoftware.com/img/spine-user-guide/paths/path-open.png)

## Constant speed

When checked, additional calculations are performed to make calculating positions along the path more accurate. When used with a [path constraint](https://en.esotericsoftware.com/spine-path-constraints), this results in bones moving along the path at a constant speed.

When unchecked, fewer calculations are performed but calculating positions along the path is less accurate. The accuracy is worsened when the handles affecting a portion of the path have dissimilar distances to their respective knot. Accuracy may also be worsened if vertices are moved from their setup pose positions using deform keys or weights.

Unless performance for calculating positions along paths has proven to be an issue, it is recommended to leave `Constant Speed` checked. It can be unchecked when the limitations are understood and the non-constant speed behavior is acceptable.

## Edit Path

Clicking the `Edit Path` button enters [edit mode](https://en.esotericsoftware.com#Edit-mode), which is for modifying the path's vertices.

## Freeze

The `Freeze` button sets rotation to 0 and scale to 1 for the current vertex positions.

This is possible because a path does not really have a rotation or scale. It has only a number of vertices, each of which has a position. Spine provides rotation and scale values for convenience, to allow manipulation similar to other attachments. The rotation and scale are adjusted when the `Rotate` or `Scale` tools are used on the entire attachment.

A path doesn't have translation, either. The translation values shown are the centroid of the vertices.

## Reverse

Clicking `Reverse` changes the direction of the path. A path constraint will go around the path in the opposite direction.

# Edit mode

Edit mode allows for creating, modifying, and deleting the path's vertices.

![Screenshot: Create](https://en.esotericsoftware.com/img/spine-user-guide/paths/create.png)

The [Edit Path](https://en.esotericsoftware.com#Edit-Path) button enters edit mode. It can be exited at any time by clicking the `Edit Path` button again, by closing the edit mode dialog, or by pressing `spacebar` or `escape`.

Right click switches between the `Create` and `Delete` tools.

## Create tool

The `Create` tool allows new knots to be created by clicking between existing knots. Drag to translate a vertex. Double click to delete a vertex.

## Delete tool

The `Delete` tool allows vertices to be deleted by clicking. Drag to translate a vertex. Multiple vertices can be selected by holding `ctrl` (`cmd` on Mac) or dragging to box select.

![Screenshot: Delete](https://en.esotericsoftware.com/img/spine-user-guide/paths/delete.png)

## New vertices mode

The `New` button deletes all vertices and enters the new vertices mode. This mode allows the path to be defined by clicking to create new knots. Drag to create a knot and adjust its handles. Vertices can also be translated by dragging or deleted by double clicking. To complete the path, exit the new vertices mode by clicking the first vertex to close the path or by clicking the `New` button again.

![Screenshot: New Vertices](https://en.esotericsoftware.com/img/spine-user-guide/paths/new-vertices.png)

# Transform tools

Path vertices can be moved outside of edit mode by using the transform tools. The entire path can be rotated, translated, and scaled like any other attachment.

![Screenshot: Rotate](https://en.esotericsoftware.com/img/spine-user-guide/paths/rotate.png)

Individual vertices can be translated with any transform tool by dragging. Multiple vertices can be selected by holding `ctrl` (`cmd` on Mac), then clicking or dragging to box select. The selected vertices can be deselected by pressing `spacebar` or `escape`, or by clicking in any empty space.

![Screenshot: Multiple Vertices](https://en.esotericsoftware.com/img/spine-user-guide/paths/multiple-vertices.png)

The origin used for rotation or scaling can be changed. Mouse over the small crosshair at the center of the `Rotate` or `Scale` tool until a circle appears, then drag the origin to the desired position. The origin will automatically snap to vertices.

![Screenshot: Origin](https://en.esotericsoftware.com/img/spine-user-guide/paths/origin.png)

Moving vertices in setup mode changes the path for the setup pose. Moving vertices in animate mode is done to set [deform keys](https://en.esotericsoftware.com/spine-keys#Deform-keys). Deform keys should generally be avoided and [weights](https://en.esotericsoftware.com/spine-weights) used instead.

Rotation and scale are only used to move the vertices. The amount of rotation and scale used is not stored in deform keys. Only the vertex positions are stored and interpolation between deform keys always moves the vertices in a straight line.

## Angle lock

When moving a handle, `shift` can be held to lock the angle of the handle, so it will only move toward or away from the knot. This can be useful to adjust the curve on only one side of the knot.

## Cusps

Normally when moving a handle, the handle on the opposite side of the knot also moves. By holding `alt` (`option` on Mac), a handle can be moved without affecting the other handle. This results in a cusp, where the transition from one curve to the next has a sharp turn.

# Video
