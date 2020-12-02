"""
Contains functions and classes useful for orbital maneuvers (finding delta v values for specific maneuvers).

Functions:
    delta_v: The delta v between a circular orbit and an elliptical transfer orbit.
    transfer_time: The time of flight during a hohmann, bi elliptic, or general transfer orbit.

Classes:
    Hohmann: Describes a hohmann transfer (the minimum change in speed required for a transfer between two
    circular coplanar orbits using two impulses).
    BiElliptic: Describes a bi-elliptic transfer (transfer between two circular coplanar orbits using three impulses).
    GeneralTransfer: Describes a general transfer between two circular coplanar orbits along with the
    required burn angles.
    SimplePlaneChange: Describes a simple plane change between two circular orbits with no change in speed
    along with the burn angle.
    Maneuver: A container for all named maneuver classes.

Notes:
    All delta v values are positive, unless applied opposite to the direction of motion in Hohmann, BiElliptic,
    and GeneralTransfer.
"""


import math
import datetime
from orbits_GUI.astro.params import Earth
from orbits_GUI.astro.afunc import semi_major_axis, vis_viva, periapsis_length, apoapsis_length, circular_speed, \
    period, flight_time


def delta_v(radius, semi_major_axis_transfer_orbit, gravitational_parameter):
    """ The delta v between a circular orbit and an elliptical transfer orbit.

    :param radius: (float) The radius of the orbit.
    :param semi_major_axis_transfer_orbit: (float) The semi-major axis of the transfer orbit.
    :param gravitational_parameter: (float) The gravitational parameter.
    :return: (float) The delta v.
    """

    return abs(vis_viva(radius, semi_major_axis_transfer_orbit, gravitational_parameter) -
               circular_speed(radius, gravitational_parameter))


def transfer_time(initial_radius, final_radius, eccentricity=0.0, rounding=None,
                  gravitational_parameter=Earth.gravitational_parameter):
    """ The time of flight during a hohmann, bi elliptic, or general transfer orbit.

    :param initial_radius: (float) The periapsis distance of the transfer orbit.
    :param final_radius: (float) The apoapsis distance of the transfer orbit.
    :param eccentricity: (float) The eccentricity of the transfer orbit; only needed for general transfers
    (default is 0.0).
    :param rounding: (int or None) Number that indicates the amount of decimal places to round to (default is None).
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (float) The transfer time.
    """

    a = semi_major_axis(radii=True, radius_one=initial_radius, radius_two=final_radius)
    if eccentricity == 0:
        if rounding is None:
            return period(a, gravitational_parameter)/2
        else:
            return round(period(a, gravitational_parameter)/2, rounding)
    else:
        p = a*(1 - eccentricity**2)
        true_anomaly_one = math.acos((((p/initial_radius) - 1)/eccentricity))
        true_anomaly_two = math.acos((((p/final_radius) - 1)/eccentricity))
        time = flight_time(eccentricity, p, true_anomaly_one, true_anomaly_two,
                                 gravitational_parameter=gravitational_parameter)
        if initial_radius > final_radius:
            time *= -1
        if rounding is None:
            return time
        else:
            return round(time, rounding)


class Hohmann:
    """ Describes a hohmann transfer (the minimum change in speed required for a transfer between two
    circular coplanar orbits using two impulses).

    Instance Attributes:
        initial_radius: (float) The radius of the initial circular orbit.
        final_radius: (float) The radius of the final circular orbit.
        gravitational_parameter: (float) Gravitational parameter.
        start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).

    Class Properties:
        delta_v_1: (float) The delta v required to go from the original orbit to the transfer orbit.
        delta_v_2: (float) The delta v required to go from the transfer orbit to the desired orbit.
        transfer_time: (float) The amount of time between delta_v_1 and delta_v_2.
        impulses: (tuple(tuples)) The impulse instructions ((time, delta v, burn angle), ...).
    """

    def __init__(self, initial_radius=0.0, final_radius=0.0, gravitational_parameter=0.0, start_time=0.0):
        """
        :param initial_radius: (float) The radius of the initial circular orbit.
        :param final_radius: (float) The radius of the final circular orbit.
        :param gravitational_parameter: (float) Gravitational parameter.
        :param start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).
        """

        self.initial_radius = initial_radius
        self.final_radius = final_radius
        self.gravitational_parameter = gravitational_parameter
        self.start_time = start_time
        self._semi_major_axis_transfer = semi_major_axis(radii=True, radius_one=self.initial_radius,
                                                         radius_two=self.final_radius)

    def __delta_v(self, radius):
        _delta_v = delta_v(radius, self._semi_major_axis_transfer, self.gravitational_parameter)
        if self.initial_radius > self.final_radius:
            _delta_v *= -1
        return _delta_v

    @property
    def delta_v_1(self):
        return self.__delta_v(self.initial_radius)

    @property
    def delta_v_2(self):
        return self.__delta_v(self.final_radius)

    @property
    def transfer_time(self):
        return transfer_time(self.initial_radius, self.final_radius,
                             gravitational_parameter=self.gravitational_parameter)

    @property
    def impulses(self):
        if isinstance(self.start_time, datetime.datetime):
            time2 = self.start_time + datetime.timedelta(seconds=self.transfer_time)
            return ((self.start_time, self.delta_v_1, 0.0),
                    (time2, self.delta_v_2, 0.0))
        elif isinstance(self.start_time, (int, float)):
            return ((self.start_time, self.delta_v_1, 0.0),
                    (self.start_time+self.transfer_time, self.delta_v_2, 0.0))
        else:
            raise TypeError


class BiElliptic:
    """ Describes a bi-elliptic transfer (transfer between two circular coplanar orbits using three impulses).

    Instance Attributes:
        initial_radius: (float) The radius of the initial circular orbit.
        final_radius: (float) The radius of the final circular orbit.
        gravitational_parameter: (float) Gravitational parameter.
        transfer_apoapsis: (float) The apoapsis distance of the transfer orbits.
        start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).

    Class Properties:
        delta_v_1: The delta v required to go from the original orbit to the first transfer orbit.
        delta_v_2: The delta v required to go from the first transfer orbit to the second.
        delta_v_3: The delta v required to go from the second transfer orbit to the desired orbit.
        transfer_time_1: The amount of time between delta_v_1 and delta_v_2.
        transfer_time_2: The amount of time between delta_v_2 and delta_v_3.
        impulses: (tuple(tuples)) The impulse instructions ((time, delta v, burn angle), ...).
    """

    def __init__(self, initial_radius=0.0, final_radius=0.0, gravitational_parameter=0.0, transfer_apoapsis=0.0,
                 start_time=0.0):
        """
        :param initial_radius: (float) The radius of the initial circular orbit.
        :param final_radius: (float) The radius of the final circular orbit.
        :param gravitational_parameter: (float) Gravitational parameter.
        :param transfer_apoapsis: (float) The apoapsis distance of the transfer orbits.
        :param start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).
        """

        self.initial_radius = initial_radius
        self.final_radius = final_radius
        self.gravitational_parameter = gravitational_parameter
        self.transfer_apoapsis = transfer_apoapsis
        self.start_time = start_time
        self._semi_major_axis_one = semi_major_axis(radii=True, radius_one=self.initial_radius,
                                                    radius_two=self.transfer_apoapsis)
        self._semi_major_axis_two = semi_major_axis(radii=True, radius_one=self.final_radius,
                                                    radius_two=self.transfer_apoapsis)

    @property
    def delta_v_1(self):
        return delta_v(self.initial_radius, self._semi_major_axis_one, self.gravitational_parameter)

    @property
    def delta_v_2(self):
        _delta_v = abs(vis_viva(self.transfer_apoapsis, self._semi_major_axis_two, self.gravitational_parameter) -
                       vis_viva(self.transfer_apoapsis, self._semi_major_axis_one, self.gravitational_parameter))
        if self.initial_radius > self.final_radius:
            _delta_v *= -1
        return _delta_v

    @property
    def delta_v_3(self):
        return -1*delta_v(self.final_radius, self._semi_major_axis_two, self.gravitational_parameter)

    @property
    def transfer_time_1(self):
        return transfer_time(self.initial_radius, self.transfer_apoapsis,
                             gravitational_parameter=self.gravitational_parameter)

    @property
    def transfer_time_2(self):
        return transfer_time(self.transfer_apoapsis, self.final_radius,
                             gravitational_parameter=self.gravitational_parameter)

    @property
    def impulses(self):
        if isinstance(self.start_time, datetime.datetime):
            time2 = self.start_time + datetime.timedelta(seconds=self.transfer_time_1)
            time3 = time2 + datetime.timedelta(seconds=self.transfer_time_2)
            return ((self.start_time, self.delta_v_1, 0.0),
                    (time2, self.delta_v_2, 0.0),
                    (time3, self.delta_v_3, 0.0))
        elif isinstance(self.start_time, (int, float)):
            time2 = self.start_time+self.transfer_time_1
            time3 = self.start_time+self.transfer_time_1+self.transfer_time_2
            return ((self.start_time, self.delta_v_1, 0.0),
                    (time2, self.delta_v_2, 0.0),
                    (time3, self.delta_v_3, 0.0))
        else:
            raise TypeError


class GeneralTransfer:
    """ Describes a general transfer between two circular coplanar orbits along with the required burn angles.

    Instance Attributes:
        initial_radius: (float) The radius of the initial circular orbit.
        final_radius: (float) The radius of the final circular orbit.
        gravitational_parameter: (float) Gravitational parameter.
        transfer_eccentricity: (float) The eccentricity of the desired transfer orbit.
        start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).

    Class Properties:
        delta_v_1: The delta v required to go from the original orbit to the transfer orbit.
        delta_v_2: The delta v required to go from the transfer orbit to the desired orbit.
        burn_angle_1: The burn angle for delta_v_1.
        burn_angle_2: The burn angle for delta_v_2.
        transfer_time: The amount of time between delta_v_1 and delta_v_2.
        impulses: (tuple(tuples)) The impulse instructions ((time, delta v, burn angle), ...).
    """

    def __init__(self, initial_radius=0.0, final_radius=0.0, gravitational_parameter=0.0, transfer_eccentricity=0.0,
                 start_time=0.0):
        """
        :param initial_radius: (float) The radius of the initial circular orbit.
        :param final_radius: (float) The radius of the final circular orbit.
        :param gravitational_parameter: (float) Gravitational parameter.
        :param transfer_eccentricity: (float) The eccentricity of the desired transfer orbit.
        :param start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).
        """

        self.initial_radius = initial_radius
        self.final_radius = final_radius
        self.transfer_eccentricity = transfer_eccentricity
        self.gravitational_parameter = gravitational_parameter
        self.start_time = start_time

        a = semi_major_axis(radii=True, radius_one=self.initial_radius, radius_two=self.final_radius)
        semi_latus_rectum = a*(1 - self.transfer_eccentricity**2)
        periapsis = periapsis_length(semi_latus_rectum, self.transfer_eccentricity, semi_major_axis=False)
        apoapsis = apoapsis_length(semi_latus_rectum, self.transfer_eccentricity, semi_major_axis=False)
        if (periapsis > min(self.initial_radius, self.final_radius)) or \
                (apoapsis < max(self.initial_radius, self.final_radius)):
            raise Exception('Invalid initial_radius, final_radius, and/or transfer_eccentricity value(s).')

        self._angular_momentum_transfer = (self.gravitational_parameter*semi_latus_rectum)**0.5
        self._initial_speed_circular = circular_speed(self.initial_radius, self.gravitational_parameter)
        self._initial_speed_transfer = vis_viva(self.initial_radius, a, self.gravitational_parameter)
        self._final_speed_transfer = vis_viva(self.final_radius, a, self.gravitational_parameter)
        self._final_speed_circular = circular_speed(self.final_radius, self.gravitational_parameter)

    @staticmethod
    def __delta_v(circle_speed, transfer_speed, radius, momentum):
        """ Calculates delta v.

        :param circle_speed: (float) The speed of the circular orbit at the radius distance.
        :param transfer_speed: (float) The speed of the transfer orbit at the radius distance.
        :param radius: (float) The distance to the transfer point.
        :param momentum: (float) The angular momentum of the transfer orbit.
        :return: (float) The delta v.
        """

        cosine_flight_path_angle = momentum/(radius*transfer_speed)
        return (circle_speed**2 + transfer_speed**2 - 2*circle_speed*transfer_speed*cosine_flight_path_angle)**0.5

    @staticmethod
    def __burn_angle(circle_speed, transfer_speed, delta_v):
        """ The burn angle between the initial orbit velocity vector to the delta v velocity vector.

        :param circle_speed: (float) The speed in the circular orbit.
        :param transfer_speed: (float) The speed in the transfer orbit.
        :param delta_v: (float) The delta v needed to transfer between the circular and transfer orbits.
        :return: (float) The burn angle.
        """

        return math.pi - math.acos((delta_v**2 + circle_speed**2 - transfer_speed**2)/(2*delta_v*circle_speed))

    @property
    def delta_v_1(self):
        return self.__delta_v(self._initial_speed_circular, self._initial_speed_transfer, self.initial_radius,
                              self._angular_momentum_transfer)

    @property
    def delta_v_2(self):
        return self.__delta_v(self._final_speed_circular, self._final_speed_transfer, self.final_radius,
                              self._angular_momentum_transfer)

    @property
    def burn_angle_1(self):
        angle = self.__burn_angle(self._initial_speed_circular, self._initial_speed_transfer, self.delta_v_1)
        if self.initial_radius < self.final_radius:
            angle *= -1
        return angle

    @property
    def burn_angle_2(self):
        angle = self.__burn_angle(self._final_speed_transfer, self._final_speed_circular, self.delta_v_2)
        if self.initial_radius > self.final_radius:
            angle *= -1
        return angle

    @property
    def transfer_time(self):
        return transfer_time(self.initial_radius, self.final_radius, eccentricity=self.transfer_eccentricity,
                             gravitational_parameter=self.gravitational_parameter)

    @property
    def impulses(self):
        if isinstance(self.start_time, datetime.datetime):
            time2 = self.start_time + datetime.timedelta(seconds=self.transfer_time)
            return ((self.start_time, self.delta_v_1, self.burn_angle_1),
                    (time2, self.delta_v_2, self.burn_angle_2))
        elif isinstance(self.start_time, (int, float)):
            return ((self.start_time, self.delta_v_1, self.burn_angle_1),
                    (self.start_time+self.transfer_time, self.delta_v_2, self.burn_angle_2))
        else:
            raise TypeError


class SimplePlaneChange:
    """ Describes a simple plane change between two circular orbits with no change in speed along with the burn angle.

    Instance Attributes:
        radius: (float) The radius of the circular orbit.
        inclination_change: (float) The angle between the current orbit and the desired orbit in radians.
        gravitational_parameter: (float) Gravitational parameter.
        start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).

    Class Properties:
        delta_v: The delta v required for the plane change.
        burn_angle: The burn angle required for the plane change.
        impulses: (tuple) The impulse instructions (time, delta v, burn angle).
    """

    def __init__(self, initial_radius=0.0, inclination_change=0.0, gravitational_parameter=0.0, start_time=0.0):
        """
        :param initial_radius: (float) The radius of the circular orbit.
        :param inclination_change: (float) The angle between the current orbit and the desired orbit in radians.
        :param gravitational_parameter: (float) Gravitational parameter.
        :param start_time: (float/datetime object) The starting time of the maneuver (default is 0.0s).
        """

        self.initial_radius = initial_radius
        self.inclination_change = inclination_change
        self.gravitational_parameter = gravitational_parameter
        self.start_time = start_time
        self._speed = circular_speed(self.initial_radius, self.gravitational_parameter)

    @property
    def delta_v(self):
        return 2*self._speed*math.sin(self.inclination_change/2)

    @property
    def burn_angle(self):
        return math.pi - math.acos(self.delta_v/(2*self._speed))

    @property
    def impulses(self):
        return (self.start_time, self.delta_v, self.burn_angle)


class Maneuver:
    """ A container for all named maneuver classes. """

    def __init__(self, maneuver=None, **kwargs):
        """
        :param maneuver: (class) The maneuver class name (default is None).

        The parameters from Hohmann, BiElliptic, GeneralTransfer, and SimpePlaneChange are also available.
        """

        self.maneuver = maneuver
        if self.maneuver:
            self.impulses = self.maneuver(**kwargs).impulses
