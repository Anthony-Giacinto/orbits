"""
Random miscellaneous functions.

Attributes:
    __this_folder: (str) The directory name of the folder that contains this module.
    __satellite_file: (str) The path to the satellite data.

Functions:
    sat_data: Takes satellite orbit data from an excel file. Best used with r'UCS-Satellite-Database-8-1-2020.xls'.
    station_location: Finds the position vector of a ground station in the geocentric-equatorial frame from its
    latitude, elevation above sea level, and the local sidereal time assuming an ellipsoidal Earth.
    decimal_length: Finds the amount of decimal places in the given float.
"""


import math
import os
import numpy as np
import pandas as pd
from orbits_GUI.astro.params import Earth


__this_folder = os.path.dirname(os.path.abspath(__file__))
__satellite_file = os.path.join(__this_folder, 'data\\UCS-Satellite-Database-8-1-2020.xls')


def sat_data(file=__satellite_file, perigee='Perigee (km)', eccentricity='Eccentricity',
             inclination='Inclination (degrees)', mass='Dry Mass (kg.)', name='Current Official Name of Satellite',
             row_indices=np.arange(30)):
    """ Takes satellite orbit data from an excel file. Best used with r'UCS-Satellite-Database-8-1-2020.xls' which
    has data on 2787 satellites.

    :param file: (str) The excel file that holds the appropriate orbit data
    (default is 'data\\UCS-Satellite-Database-8-1-2020.xls').
    :param perigee: (str) The perigee excel column header (default is 'Perigee (km)').
    :param eccentricity: (str) The eccentricity excel column header (default is 'Eccentricity').
    :param inclination: (str) The inclination excel column header (default is 'Inclination (degrees)').
    :param mass: (str) The mass excel column header (default is 'Dry Mass (kg.)').
    :param name: (str) The name column header (default is 'Current Official Name of Satellite').
    :param row_indices: (list) Index values that indicate the desired excel rows (default is np.arange(30)).
    :return: (list(lists)) The semi_latus_rectums, eccentricities, inclinations, masses, names.
    """

    data = pd.read_excel(file, usecols=[perigee, eccentricity, inclination, mass, name])
    df = pd.DataFrame(data).iloc[row_indices].fillna(1)
    semi_latus_rectum = tuple((df[perigee] + Earth.radius)*(1 + df[eccentricity]))
    e = tuple(df[eccentricity])
    i = tuple(df[inclination]*math.pi/180)
    m = tuple(df[mass])
    n = tuple(df[name])
    return semi_latus_rectum, e, i, m, n


def station_position(latitude, elevation, local_sidereal_time):
    """ Finds the position vector of the ground station in the geocentric-equatorial frame from its
    latitude, elevation above sea level, and the local sidereal time assuming an ellipsoidal Earth.

    :param latitude: (float) The latitude of the ground station in radians.
    :param elevation: (float) The elevation above sea level of the ground station in radians.
    :param local_sidereal_time: (float) The local sidereal time of the ground station in radians; this is the
    Greenwich sidereal time plus the longitude of the station measured eastward from Greenwich, where the
    Greenwich sidereal time is the angle from the vernal equinox direction to the Greenwich meridian.
    :return: (numpy array) The position vector of the ground station in the geocentric-equatorial frame.
    """

    denominator = (1 - Earth.ellipsoid_eccentricity**2*(math.sin(latitude))**2)**0.5
    x = math.cos(latitude)*(Earth.equatorial_radius/denominator + elevation)
    z = math.sin(latitude)*(Earth.polar_radius*(1 - Earth.ellipsoid_eccentricity**2)/denominator + elevation)
    return np.array([x*math.cos(local_sidereal_time), x*math.sin(local_sidereal_time), z])


def inclination_from_launch(latitude, azimuth):
    """ Finds the inclination of a spacecraft launched with a specific latitude and azimuth.

    :param latitude: (float) The latitude of the launch site in radians.
    :param azimuth: (float) The azimuth of the launch in radians.
    """

    return math.acos(math.sin(azimuth)*math.cos(latitude))


def decimal_length(num):
    """ Finds the amount of decimal places in the given float.

    :param num: (float) A floating point number.
    :return: (int) The number of decimal places.
    """

    x = str(num).split('.')[-1]
    if x == '0':
        return 0
    else:
        return len(x)


def integer_length(num):
    """ Finds the amount if numbers that make up an integer.

    :param num: (int/float) An integer (ex. 10.0 will work as well).
    :return: (int) The number of places in the integer.
    """

    try:
        x = str(num).split('.')[0]
    except TypeError:
        x = str(num)
    if '-' in x:
        x = x.replace('-', '')
    return len(x)


def round_to_place(num, place):
    """ Rounds some given number (int/float) to the given integer place. """

    try:
        a = str(num).split('.')[0]
    except TypeError:
        a = str(num)
    len_a = len(a)
    if 0 < place <= len_a:
        b = a[(len_a-place):]
        c = str(int(round(int(b)*10**-(len(b)-1), 0)))
        d = a[:(len_a-place)]+c
        for i in range(len(d), len_a):
            d += '0'
        return int(d)
