# Reference Chooser
This scripts helps to replace scene asset reference from  master/opt/abc folder.
Asset file inside MASTER/OPT/ABC folder needs to have same name.

```
-Sample Asset folder structure-
--------------------------WXC_ShrubAzaleaA--------------------------
OPT--------------> R://LEMONCORE/WXC_PROJ/scenes/Assets/Prop/S/ShrubAzaleaA/OPT/WXC_ShrubAzaleaA.ma
ABC--------------> R://LEMONCORE/WXC_PROJ/scenes/Assets/Prop/S/ShrubAzaleaA/ABC/WXC_ShrubAzaleaA.ma
MASTER-----------> R://LEMONCORE/WXC_PROJ/scenes/Assets/Prop/S/ShrubAzaleaA/master/WXC_ShrubAzaleaA.ma```

```

To Run the script:<br>

- Select the reference you want to replace, from the script editor and run the script.
- Choose the type (opt/abc/master) that u want to replace to.
- Script supports multiple selection as well.
- Any asset that has missing chosen type in the directory.. script will throw a warning and continue to other selection(if there are multiple selection) or stop(for single selection)

## Reference Chooser1

### Reference Chooser2