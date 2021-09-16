# Visual Tracker Simulator
A Blender add-on that generates and runs scenes using parameters from the text file. Allows to render such scene and its mask.

## How to install
Download the project, unzip it, create a folder called _visual\_tracker\_simulator_, place the _\_\_init\_\__ file in it. Copy this folder inside the add-on folder in the Blender installation location.

## How to use
In Object Mode, press **N** on your keyboard to get the sidebar. Click the Visual Tracker Simulator button.
\
Choose a desired file, then click *Load* to generate it. You can choose to only set certain parameters. Make sure to inialize all the parameters first, to avoid An example is provided in the _example_ folder.
\
The scene properties that are currently parametrised are:
* camera x, y and z location
* light intensity
* fog density
* density of generated objects


## Creating your own scenes
The scene must have the following collections:
* _MainObjects_ - objects you want to follow. Each of the objects you want to follow should be put in its own collection with the same name as the following object (for example an object named Boat should be in the collection named _Boat_, inside a collection named _MainObjects_)
* _GeneratingObjects_ - objects that you want to generate. Objects in this folder will be duplicated, then randomly put on paths in the collection _FollowingPaths_
The name of the path should contain the name of the layer/object you're following. Make sure that only that object has such a name (layer and object names should be the same, and only them). The following path should be cyclic, to prevent the path jumping from one point to another. Generating objects should only consist of one mesh
* _CameraParents_ - paths which the camera will follow. The path the camera follows has the same prefix as the object we are following, and the path will be chosen at random out of those paths
* _GeneratedObjects_ - a collection in which the objects generated with the add-on are stored
* _FollowingPaths_ - in here, put the paths you want the generated objects to follow. The path will be chosen at random
Other collections can be used to make the scene view more organised, but they are not needed.
<!-- end of the list -->
\
For each of the objects we want to follow, a layer must be created. Create a layer for each of the collections in _MainObject_, give it the same name as the collection (for example, a collection boat) and using holdout mask out all the collection except the one object itself.
\
The scene should have an HDRI skybox. Each scene should also have a fog object. 
\
When creating the animations for objects following the paths, make sure all the animations are cyclic, so you can generate the animation to be as long as you want.
\
At least one path should be present in _FollowingPaths_ and at least one object in _GeneratingObjects_.


## VOT Toolkit reformat
In order to use the rendered masks in VOT toolkit, use the _mask\_to\_vot.py_ file.

#### Version 0.0.1
