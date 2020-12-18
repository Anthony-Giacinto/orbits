# orgits_gui
This project allows the user to simulate the trajectories of objects in space using fundamental astrodynamics calculations.

## Table of Contents
* [General info](#general-info)
* [Screenshot](#screenshot)
* [Technologies](#technologies)
* [Features](#features)
* [How to Use](#how-to-use)

## General Info

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
* On first use, must:
    1. Copy the .../files/images folder and place it in the VPython package folder .../Lib/site-packages/vpython/vpython_data/ .
    2. Copy everything else from .../files/ and place them in .../Lib/site-packages/vpython/vpython_libraries/ to replace the default files.
* To run:

        import orbits_GUI as orb  
        orb.Simulate()
