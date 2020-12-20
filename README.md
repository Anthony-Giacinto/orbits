# Orbits
This project allows the user to simulate the trajectories of objects in space inside of a browser window using fundamental astrodynamics calculations.

## Table of Contents
* [General info](#general-info)
* [Screenshot](#screenshot)
* [Technologies](#technologies)
* [Features](#features)
* [Controls](#controls)
* [How to Use](#how-to-use)

## General Info
* The recommended browsers to use are Microsoft Edge and Google Chrome.
* On first use, must:
    1. Copy the .../files/images folder and place it in the VPython package folder .../Lib/site-packages/vpython/vpython_data/ .
    2. Copy everything else from .../files/ and place them in .../Lib/site-packages/vpython/vpython_libraries/ to replace the default files.
* To run the GUI:

        import orbits as orb  
        orb.Simulate()
* To exit the Gui, just close the browser window.
* Can perform astrodynamics calculations without the GUI:
        
        import orbits as orb
        orb.astro."function"
    
    or
    
        import orbits.astro as astro
        astro."function"
* The browser GUI was built using VPython:
    * https://www.glowscript.org/docs/VPythonDocs/index.html

## Screenshot
Screenshot of over 2600 satellites orbiting Earth using real satellite data.
![satellites](/files/screenshots/satellites.png)

## Technologies
Project was created with:
* Python 3.7

## Features
* Can animate trajectories of objects in space.
* Contains many useful astrodynamics functions.
* Can animate orbit transfers and plane changes (hohmann transfer, bi-elliptic transfer, general transfer, simple plane change).
* Can calculate the necessary delta-v and burn angle for certain orbit transfers.
* Can determine the position and velocity vectors of an orbiting object (Geocentric-Equatorial frame) from given radar measurements.
* Can determine the position and velocity vectors of an orbiting object (Geocentric-Equatorial frame) from given classical orbit elements and vice versa.
* Deals with orbit perturbations by using Cowell's method.

## Controls
* Run Scenario/End Scenario Button: Starts and ends the simulation.
* Pause/Play Button: Pauses and plays the simulation after it has begun.
* Reset Button: Resets the GUI back to the start up GUI.
* Following Input: Enter the name of the object that you want the camera to focus on.
* Time Step Input: The amount of time that passes between each new position determination in seconds. The smaller the value the more accurate the simulate will be. Cannot be larger than the Time Rate value (default value is 1.0 s).
* Time Rate Input: The amount of simulation time that passes every Time Step in chosen units per Time Step. Increase this value to increase the rate of simulation time. Cannot be smaller than the Time Step value (default value is 1 second/Time Step).

    * Notes on Time Step and Time Rate: Increasing either the Time Rate or the Time Step will "increase" the rate of simulation time, but it is recommended to just use Time    Rate. However, increasing Time Rate will only work up to some limit. If you wish to increase the rate of simulation time further, you will also need to increase the Time Step. Keep in mind that the larger the Time Step value, the less accurate the position data of the objects will be.

* Scenario Menu: Will build the chosen scenario from the menu, or will allow you to create your own scenario.
* Body Menu: Allows you to place objects into the scenario. Can choose from some preset planets or can create your own object.
* Toggle Axes: Toggles on/off cartesian axes on the primary body in the scenario.
* Rotate the camera: Rmb and drag or ctrl + lmb.
* Zoom in/out: Use the mouse scroll wheel or alt + lmb.
* Delete objects: Delete/backspace + lmb.
* Access info on object: Lmb.

## How to Use
* Choose a scenario
    * Can choose between prebuilt scenarios or a custom scenario.  

![choose_scenario](/files/screenshots/choose_scenario.png)    

* If building a custom scenario, choose a body:  

![choose_body](/files/screenshots/choose_body.png)    

* There are four options for postion and velocity determination:  
    * The classical elements, doppler radar, and radar options are meant to be used with respect to some primary body.
    * Enter in all the desired values, and press enter/return for each input.
    * Click "Create Body".

![vectors](/files/screenshots/vectors.png)  
![elements](/files/screenshots/elements.png)  
![doppler](/files/screenshots/doppler.png)  
![radar](/files/screenshots/radar.png)    

* If determining position and velocity from classical elements, you can add a maneuver to the body:
    * Hohmann, Bi-Elliptic, General, Simple Plane Change.
    * The date and time inputs are for the start time of the maneuver.

![hohmann](/files/screenshots/hohmann.png)  
![bielliptic](/files/screenshots/bielliptic.png)  
![general](/files/screenshots/general.png)  
![planechange](/files/screenshots/planechange.png)    

* At any point during the building of the scenario, you can choose the starting time for the scenario:  
    * The default scenario starting time will be the date and time when "Run Scenario" is clicked.

![starttime](/files/screenshots/starttime.png)  
