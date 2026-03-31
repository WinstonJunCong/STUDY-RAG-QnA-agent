---
title: Slots
url: https://en.esotericsoftware.com/spine-slots
source: Spine User Guide
---

# Slots

The attachment that is visible for a slot can be [keyed](https://en.esotericsoftware.com/spine-keys#Slot-attachment) in animations.

A slot is parented to a [bone](https://en.esotericsoftware.com/spine-bones) is a container for [attachments](https://en.esotericsoftware.com/spine-attachments), where only one attachment (or none) can be visible at any given time. Slots are very important for many reasons, even if at first they may be difficult to appreciate. A slot is only conceptual, it does not have a position and it is not drawn.

# Draw order

The draw order for a skeleton is a list of slots, where attachments for slots higher in the list are drawn on top of those below. The draw order can be seen under the skeleton in the tree.

![Screenshot: Draworder](https://en.esotericsoftware.com/img/spine-user-guide/slots/draworder.png)

Slots group attachments of the same type. For example, a `weapon` slot may have a `knife`, `sword`, `axe`, etc. Since only the `weapon` slot appears in the draw order, the draw order list stays concise even if the skeleton has hundreds or thousands of weapons.

Slots also decouple bones from the draw order, allowing attachments on the same bone to be drawn above and below an attachment on a different bone. For example, the torso bone has slots `belly` and `shirt`, the hip bone has slot `pants`. Slots allow `belly` to be drawn under `pants` and `shirt` to be drawn above `pants`, even though both `belly` and `shirt` are on the same bone.

## Changing the draw order

When using an image editor [script](https://en.esotericsoftware.com/spine-images#Scripts) the images will be imported into Spine under slots that already have the correct draw order.

Slots in the draw order can dragged up or down and the draw order can be [keyed](https://en.esotericsoftware.com/spine-keys#Draw-order).

Alternatively, the plus (`+`) or minus (`-`) keys on your keyboard will change the draw order of the slot for the current selection. Rather than finding a slot in the tree, it can be convenient to select an attachment in the viewport, then use these hotkeys to adjust the draw order for the attachment's slot. Hold `shift` to jump by 5.

![Screenshot: Draworder1](https://en.esotericsoftware.com/img/spine-user-guide/slots/draworder1.png) ![Screenshot: Draworder2](https://en.esotericsoftware.com/img/spine-user-guide/slots/draworder2.png)

Here the `eye` slot was moved from above the `googles` slot to below it in the draw order.

### Tree filter

Adjusting the draw order can be made easier by using the [filter buttons](https://en.esotericsoftware.com/spine-tree#Filter-buttons) in the upper left of the tree view to hide bones and attachments, leaving only slots visible in the tree under the `Slots` node. These slots represent the draw order and can be dragged up or down.

![Screenshot: Filter](https://en.esotericsoftware.com/img/spine-user-guide/slots/filter.png)

Normally when an attachment is selected in the viewport, it is also selected in the tree. When the tree is filtered so it doesn't contain attachments, the slot is selected in the tree instead, which instantly shows you where the slot is within the draw order.

# Properties

![Screenshot: Properties](https://en.esotericsoftware.com/img/spine-user-guide/slots/properties.png)

## Color

The [slot color view](https://en.esotericsoftware.com/spine-slot-color) makes setting the slot color faster and more convenient than clicking the color button.

The slot color tints the slot's attachment, controls the attachment's alpha (opacity), and can be [keyed](https://en.esotericsoftware.com/spine-keys#Slot-color). Attachments have their own, separate [color](https://en.esotericsoftware.com/spine-attachments#Color) but it cannot be keyed.

The left half of the color button shows the color with alpha. The right half of the button shows the opaque color. Click the button to change the color and alpha.

Setting the alpha to zero to make an attachment invisible is not an efficient way to hide the attachment. Most game toolkits spend the same effort drawing an image with zero alpha as they do drawing an image that can be seen.

It is better to hide an attachment by setting a [slot attachment key](https://en.esotericsoftware.com/spine-keys#Slot-attachment). To avoid an abrupt disappearance, the slot color can be used to fade to transparent before hiding.

![Screenshot: Color Alpha](https://en.esotericsoftware.com/img/spine-user-guide/key-frames/color-alpha.png)

When the color and alpha have been [separated](https://en.esotericsoftware.com/spine-keys#Separate-color-and-alpha) for an animation, two color buttons appear. Clicking either button opens the same slot color dialog which can change either the alpha, color, or both.

![Screenshot: Separate Buttons](https://en.esotericsoftware.com/img/spine-user-guide/slots/separate-buttons.png)

## Tint black

Tint black enables tinting an image's dark colors separately from its light colors. When used with grayscale images, this can achieve a wide variety of colored images. It also allows for effects such as a solid color silhouette, inverted colors, Super Mario invincibility star flashing, and more. Additional effects can be achieved when using the additive, screen, or multiply blend modes.

Tint black is enabled by checking `Tint Black` for a slot and causes a second color button to appear.

![Screenshot: Tintblack](https://en.esotericsoftware.com/img/spine-user-guide/slots/tintblack.png)

The first color button sets the "light" color, which tints the lighter portions of the image and controls opacity. The second color button sets the "dark" color, which tints the darker portions of the image. The light and dark colors can be [keyed](https://en.esotericsoftware.com/spine-keys#Slot-color).

| Light | Dark | Image | Description |
| --- | --- | --- | --- |
|  |  |  | The original black and white image. |
|  |  |  | Without tint black, the light color set to red. The black and white image is tinted uniformly with red, resulting in shades of the same red. |
|  |  |  | With tint black, the light color set to salmon pink and the dark color to red. The image is not simply shades of the same color, so it has much more visual interest. |
|  |  |  | With tint black, the light color set to blue and the dark color to light blue. Inverse colors, a solid color silhouette, flashing, and other effects can be achieved. |

See the tint blank [example projects](https://en.esotericsoftware.com/spine-examples#Tint-blank) for usage examples.

## Blending

The Photoshop [script](https://en.esotericsoftware.com/spine-images#Scripts) will set the blending mode for slots it creates using the Photoshop layer's blending mode.

Blending controls how the slot attachment's pixels are combined with the pixels below:

- `Normal` is the default setting, normal blending is applied.
- `Additive` corresponds to Linear Dodge in Photoshop.
- `Multiply` corresponds to Multiply in Photoshop.
- `Screen` corresponds to Screen in Photoshop.


Blending modes other than `Normal` may affect performance for some game toolkits by increasing [draw calls](https://en.esotericsoftware.com/spine-metrics#Draw-calls). Some game toolkits can avoid increased draw calls when using `Additive` and rendering with premultiplied alpha.

## Separate color and alpha

In animate mode, an additional row appears in the slot properties.

![Screenshot: Separate](https://en.esotericsoftware.com/img/spine-user-guide/slots/separate.png)

The `Alpha` checkbox allows color (RGB) and alpha (A) to be keyed separately for the current animation. See [separate color and alpha](https://en.esotericsoftware.com/spine-keys#Separate-color-and-alpha) for more information.

# Hiding slots

![Screenshot: Slot Visibility](https://en.esotericsoftware.com/img/spine-user-guide/slots/slot-visibility.png)

Like bones, slots have a visibility dot in the tree. When hidden, attachments for the slot will not be drawn in the viewport and won't appear in image or video exports. However, this can't be keyed and the slot's attachments will still appear in data exports.

If you've hidden many slots or bones, `ctrl+H` will show them all again.

Hiding a slot's attachments is intended only for temporarily reducing clutter in the viewport and cannot be keyed. You may want to [hide](https://en.esotericsoftware.com/spine-attachments#Hiding-attachments) the slot's attachment and [key it](https://en.esotericsoftware.com/spine-keys#Slot-attachment) instead.

Right clicking a bone's visibility dot will toggle hiding the bone and all child bones and slots.

All attachments can be hidden in the viewport using the [viewport options](https://en.esotericsoftware.com/spine-tools#Viewport-options).

# Folders

Slots can be organized into folders. To create a folder, select a slot and click `New...` `Folder`. Slots can be moved between folders by dragging them.

In exported skeleton data, folder names are prepended to the slot name to create the final name used in the Spine Runtimes. For example, if the folder `hair` has a subfolder `long` which has a slot `hair-strand-1`, then the slot name at runtime is `hair/long/hair-strand-1`.
