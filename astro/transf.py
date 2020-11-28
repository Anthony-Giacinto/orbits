"""
Useful matrix transformations.

Functions:
    peri_geo: (numpy array) A matrix to transform a vector from the Perifocal frame to the Geocentric-Equatorial frame
    when eccentricity is not 0 and inclination is not 0 or pi.
    peri_geo_e: (numpy array) A matrix to transform a vector from the Perifocal frame to the Geocentric-Equatorial frame
    when eccentricity is 0, but inclination is not 0 or pi.
    peri_geo_i: (numpy array) A matrix to transform a vector from the Perifocal frame to the Geocentric-Equatorial frame
    when inclination is 0 or pi, but eccentricity is not 0.
    rotate_x: (numpy array) Basic rotation matrix about the x-axis.
    rotate_y: (numpy array) Basic rotation matrix about the y-axis.
    rotate_z: (numpy array) Basic rotation matrix about the z-axis.
    vpython_rotation: (numpy array) A matrix to rotate vectors to match the desired axis orientation in VPython.
    rodrigues_rotation: (numpy array) A matrix that rotates about some given vector by some given angle.
    geo_to_topo: (numpy array) A matrix to transform a vector from the Geocentric-Equatorial frame to
    the Topocentric frame.
    topo_to_geo: (numpy array) A matrix to transform a vector from the Topocentric frame to the
    Geocentric-Equatorial frame.
"""


import math
import numpy as np


def peri_to_geo(inclination, longitude_of_ascending_node, periapsis_angle):
    """ A matrix to transform a vector from the Perifocal frame (p-q-w) to the Geocentric-Equatorial frame (i-j-k)
    when eccentricity is not 0 and inclination is not 0 or pi. The periapsis_angle represents the
    argument of periapsis.

    :return: (numpy array) The transformation matrix.
    """

    return np.array([[math.cos(longitude_of_ascending_node)*math.cos(periapsis_angle) -
                      math.sin(longitude_of_ascending_node)*math.sin(periapsis_angle) *
                      math.cos(inclination),
                      -math.cos(longitude_of_ascending_node)*math.sin(periapsis_angle) -
                      math.sin(longitude_of_ascending_node)*math.cos(periapsis_angle) *
                      math.cos(inclination),
                      math.sin(longitude_of_ascending_node)*math.sin(inclination)],
                     [math.sin(longitude_of_ascending_node)*math.cos(periapsis_angle) +
                      math.cos(longitude_of_ascending_node)*math.sin(periapsis_angle) *
                      math.cos(inclination),
                      -math.sin(longitude_of_ascending_node)*math.sin(periapsis_angle) +
                      math.cos(longitude_of_ascending_node)*math.cos(periapsis_angle) *
                      math.cos(inclination),
                      -math.cos(longitude_of_ascending_node)*math.sin(inclination)],
                     [math.sin(periapsis_angle)*math.sin(inclination),
                      math.cos(periapsis_angle)*math.sin(inclination),
                      math.cos(inclination)]])


def peri_to_geo_e(inclination, longitude_of_ascending_node):
    """ A matrix to transform a vector from the Perifocal frame (p-q-w) to the Geocentric-Equatorial frame (i-j-k)
    when eccentricity is 0, but inclination is not 0 or pi.

    :return: (numpy array) The transformation matrix.
    """

    return np.array([[math.cos(longitude_of_ascending_node),
                      -math.sin(longitude_of_ascending_node)*math.cos(inclination),
                      math.sin(longitude_of_ascending_node)*math.sin(inclination)],
                     [math.sin(longitude_of_ascending_node),
                      math.cos(longitude_of_ascending_node)*math.cos(inclination),
                      -math.cos(longitude_of_ascending_node)*math.sin(inclination)],
                     [0, math.sin(inclination), math.cos(inclination)]])


def peri_to_geo_i(periapsis_angle):
    """ A matrix to transform a vector from the Perifocal frame (p-q-w) to the Geocentric-Equatorial frame (i-j-k)
    when inclination is 0 or pi, but eccentricity is not 0. The periapsis_angle represents the longitude of periapsis.

    :return: (numpy array) The transformation matrix.
    """

    return np.array([[math.cos(periapsis_angle), -math.sin(periapsis_angle), 0],
                     [math.sin(periapsis_angle), math.cos(periapsis_angle), 0],
                     [0, 0, 1]])


def rotate_x(angle):
    """ Basic rotation matrix about the x-axis.

    :param angle: (float) The angle of rotation.
    :return: (numpy array) The transformation matrix.
    """

    return np.array([[1, 0, 0], [0, math.cos(angle), -math.sin(angle)], [0, math.sin(angle), math.cos(angle)]])


def rotate_y(angle):
    """ Basic rotation matrix about the y-axis.

    :param angle: (float) The angle of rotation.
    :return: (numpy array) The transformation matrix.
    """

    return np.array([[math.cos(angle), 0, math.sin(angle)], [0, 1, 0], [-math.sin(angle), 0, math.cos(angle)]])


def rotate_z(angle):
    """ Basic rotation matrix about the z-axis.

    :param angle: (float) The angle of rotation.
    :return: (numpy array) The transformation matrix.
    """

    return np.array([[math.cos(angle), -math.sin(angle), 0], [math.sin(angle), math.cos(angle), 0], [0, 0, 1]])


def vpython_rotation():
    """ A matrix to rotate vectors to match the desired axis orientation in VPython
    (x-axis points towards the screen, y-axis points to the right, the z-axis points up).

    :return: (numpy array) The transformation matrix.
    """

    return np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])


def rodrigues_rotation(vector, angle):
    """ A matrix that rotates about some given vector by some given angle.

    :param vector: (numpy array) The vector to be rotated about.
    :param angle: (float) The angle of rotation about the given vector.
    :return: (numpy array) The transformation matrix.
    """

    w = np.array([[0, -vector[2], vector[1]], [vector[2], 0, -vector[0]], [-vector[1], vector[0], 0]])
    return np.identity(3) + math.sin(angle)*w + (2*(math.sin(angle/2))**2)*(w.dot(w))


def geo_to_topo(latitude, local_sidereal_time):
    """ A matrix to transform a vector from the geocentric-equatorial frame to the topocentric frame.

    :param latitude: (float) The latitude of the ground station in radians.
    :param local_sidereal_time: (float) The local sidereal time of the ground station in radians; this is the
    Greenwich sidereal time plus the longitude of the station measured eastward from Greenwich, where the
    Greenwich sidereal time is the angle from the vernal equinox direction to the Greenwich meridian.
    :return: (numpy array) The transformation matrix.
    """

    return np.dot(rotate_y(latitude - math.pi/2), rotate_z(-local_sidereal_time))


def topo_to_geo(latitude, local_sidereal_time):
    """ A matrix to transform a vector from the topocentric frame to the geocentric-equatorial frame.

    :param latitude: (float) The latitude of the ground station in radians.
    :param local_sidereal_time: (float) The local sidereal time of the ground station in radians; this is the
    Greenwich sidereal time plus the longitude of the station measured eastward from Greenwich, where the
    Greenwich sidereal time is the angle from the vernal equinox direction to the Greenwich meridian.
    :return: (numpy array) The transformation matrix.
    """

    return np.linalg.inv(geo_to_topo(latitude, local_sidereal_time))
