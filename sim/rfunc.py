"""
Random miscellaneous functions.

Attributes:
    __this_folder: (str) The directory name of the folder that contains this module.
    __satellite_file: (str) The path to the satellite data.

Functions:
    sat_data: Takes satellite orbit data from an excel file. Best used with r'UCS-Satellite-Database-8-1-2020.xls'.
    decimal_length: Finds the amount of decimal places in the given float.
    integer_length: Finds the amount if numbers that make up an integer.
    round_to_place: Rounds some given number (int/float) to the given integer place.
    random_element_angles: Picks random values for longitude of ascending node, periapsis angle, and epoch angle
    in radians.
"""


import math
import random
import os
import numpy as np
import pandas as pd
from orbits.astro.params import Earth


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


def random_element_angles(num, step=0.05):
    """ Picks random values for longitude of ascending node, periapsis angle, and epoch angle in radians.

    :param num: (int) The desired length of the created lists.
    :param step: (float) The step size for the range of random angles that may be chosen from (default is 0.05).
    :return: (lists) Longitude of ascending node, periapsis angle, and epoch angle lists.
    """

    loan, pa, ea = [], [], []
    angles = np.arange(0, 2*math.pi, step)
    for i in range(num):
        loan.append(random.choice(angles))
        pa.append(random.choice(angles))
        ea.append(random.choice(angles))
    return loan, pa, ea


def vector_to_np(vector):
    return np.array([vector.x, vector.y, vector.z])
