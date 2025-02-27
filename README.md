## Ski Router

Python program the best route from A to B in a ski resort
Authors: Jules-Gaspard GEORGE, Nicolas FAU

## Creating Resort Information

OpenStreetMap has coordinates of all ski pistes and lifts. These can be exported in json format using the overpass-turbo.eu website.
Locate the ski area and create a bounding box to select all runs and lifts then run the following query:

```json
[out:json][timeout:25];
// gather results
(  
  // query part for: “piste:type”  
  way["piste:type"=downhill]({{bbox}});  
  way[aerialway][aerialway!=zip_line]({{bbox}});
  relation["piste:type"=downhill]({{bbox}});
);
// print results
out body;
>;
out skel qt;
```

Export the file as geojson and copy it into the Ski-Areas directory

## Set Up

$ python3 -m venv venv
$ source venv/bin/activate

sudo apt-get install python3-tk


If your terminal does not include the following libraries, they must be installed (e.g.: command to install “bibli”: pip
install bibli):

- geojson
- numpy
- math
- os
- tkinter
- tkintermapview
- PIL
- heapq

## Running

Open the following windows from the folder extracted from the given zip file:

- Class_main_V3
- Class_fenetre_tkinter_V3

To open the graphics window, simply run the “Class_fenetre_tkinter_V3” program.

An initial welcome window opens, showing the application being launched. It quickly closes, and then the final window
opens. The result is a map representing the ski area, with points corresponding to the start and end of pistes and
lifts. These points also represent possible intersections between certain slopes.

You can then click on the point where you are. This point appears in the “Start point” line. You can now click on your
destination point. This is displayed in the “End point” line.

Now click on the “View” button to display the route you need to take. This route is displayed not only on the map, but
also in text in the form of steps to follow in the left-hand section of the graphics window.

If you want to find another route linking 2 points in the station, simply click on another start point, then another end
point, and then on the “Show” button. You can also clear the paths displayed on the map with the “Clear previous routes”
button.

Happy navigation!
