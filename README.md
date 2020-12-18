# Orbits
This project allows the user to simulate the trajectories of objects in space using fundamental astrodynamics calculations.

## Table of Contents
* [General info](#general-info)
* [Screenshot](#screenshot)
* [Technologies](#technologies)
* [Features](#features)
* [How to Use](#how-to-use)

## General Info
* On first use, must:
    1. Copy the .../files/images folder and place it in the VPython package folder .../Lib/site-packages/vpython/vpython_data/ .
    2. Copy everything else from .../files/ and place them in .../Lib/site-packages/vpython/vpython_libraries/ to replace the default files.
* To run:

        import orbits_GUI as orb  
        orb.Simulate()

## Screenshot
Screenshot of over 2600 satellites orbiting Earth using real satellite data.
![satellites](/files/screenshots/satellites.png)

## Technologies
Project was created with:
* Python 3.7

## Features
* Can animate trajectories of objects in space.
* Contains many useful astrodynamics functions.
* Can animate satellites using satellite data from an Excel spreadsheet (perigee, eccentricity, inclination, mass).
* Can animate orbit transfers and plane changes (hohmann transfer, bi-elliptic transfer, general transfer, simple plane change).
* Can calculate the necessary delta-v and burn angle for certain orbit transfers.
* Can determine the position and velocity vectors of an orbiting object (Geocentric-Equatorial frame) from given radar measurements.
* Can determine the position and velocity vectors of an orbiting object (Geocentric-Equatorial frame) from given classical orbit elements and vice versa.
* Deals with orbit perturbations by using Cowell's method.

## How to Use
* Run Scenario / End Scenario: Starts and ends the simulation.
* Pause / Play: Pauses and plays the simulation after it has begun.
* Reset: Resets the UI back to the start up UI.
* Following: Enter the name of the object that you want the camera to focus on.
* Time Step: The amount of time that passes between each new position determination in seconds. The smaller the value the more accurate the simulate will be. Cannot be larger than the Time Rate value (default value is 1.0 s).
* Time Rate: The amount of simulation time that passes every Time Step. Increase this value to increase the rate of simulation time. Cannot be smaller than the Time Step value (default value is 1 second / Time Step).

    * Notes on Time Step and Time Rate: Increasing either the Time Rate or the Time Step will "increase" the rate of simulation time, but it is recommended to just use Time    Rate. However, increasing Time Rate will only work up to some limit. If you wish to increase the rate of simulation time further, you will also need to increase the Time Step. Keep in mind that the larger the Time Step value, the less accurate the position data of the objects will be.
