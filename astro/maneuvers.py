"""
Contains functions useful for orbital maneuvers (finding delta v values for specific maneuvers).

Attributes:
    __earth: (float) The gravitational parameter for earth.

Functions:
    hohmann_transfer: Finds the delta v values required for a hohmann transfer.
    bi_elliptic_transfer: Finds the delta v values required for a bi-elliptic transfer.
    general_transfer: Finds the delta v values required for some 'general' transfer between two
    circular coplanar orbits along with their required burn angles.
    simple_plane_change: Finds the delta v value required for a plane change between two circular orbits
    with no change in speed along with the burn angle.
    transfer_time: The time of flight during a hohmann, bi elliptic, or general transfer orbit.
    rocket_equation: Finds the delta v due to engine burn of a rocket in the case of no external forces.
    __delta_v: The delta v between a circular orbit and an elliptical transfer orbit; used for hohmann and bi-elliptic.

Notes:
    All delta v values are positive, unless applied opposite to direction of motion in hohmann, bi-elliptic, & general.
"""


import math
from orbits_GUI.astro.params import Earth
from orbits_GUI.astro.afunc import semi_major_axis, vis_viva, periapsis_length, apoapsis_length, circular_speed, \
    period, flight_time


__earth = Earth.gravitational_parameter


def hohmann_transfer(initial_radius, final_radius, gravitational_parameter=__earth):
    """ Finds the delta v values required for a hohmann transfer (the minimum change in speed required for a transfer
    between two circular coplanar orbits using two impulses).

    :param initial_radius: (float) The radius of the initial circular orbit.
    :param final_radius: (float) The radius of the final circular orbit.
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (list) the delta v required to go from the original orbit to the transfer orbit,
    the delta v required to go from the transfer orbit to the desired orbit.
    """

    semi_major_axis_transfer = semi_major_axis(radii=True, radius_one=initial_radius, radius_two=final_radius)
    delta_v_one = __delta_v(initial_radius, semi_major_axis_transfer, gravitational_parameter)
    delta_v_two = __delta_v(final_radius, semi_major_axis_transfer, gravitational_parameter)

    if initial_radius > final_radius:
        delta_v_one *= -1
        delta_v_two *= -1

    return delta_v_one, delta_v_two


def bi_elliptic_transfer(initial_radius, final_radius, apoapsis, gravitational_parameter=__earth):
    """ Finds the delta v values required for a bi-elliptic transfer (transfer between two circular
    coplanar orbits using three impulses).

    :param initial_radius: (float) The radius of the initial circular orbit.
    :param final_radius: (float) The radius of the final circular orbit.
    :param apoapsis: (float) The apoapsis distance of the transfer orbits.
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (list) the delta v required to go from the original orbit to the first transfer orbit,
    the delta v required to go from the first transfer orbit to the second,
    the delta v required to go from the second transfer orbit to the desired orbit.
    """

    semi_major_axis_one = semi_major_axis(radii=True, radius_one=initial_radius, radius_two=apoapsis)
    semi_major_axis_two = semi_major_axis(radii=True, radius_one=final_radius, radius_two=apoapsis)
    delta_v_one = __delta_v(initial_radius, semi_major_axis_one, gravitational_parameter)
    delta_v_two = abs(vis_viva(apoapsis, semi_major_axis_two, gravitational_parameter) -
                      vis_viva(apoapsis, semi_major_axis_one, gravitational_parameter))
    delta_v_three = -1*__delta_v(final_radius, semi_major_axis_two, gravitational_parameter)

    if initial_radius > final_radius:
        delta_v_two *= -1

    return delta_v_one, delta_v_two, delta_v_three


def general_transfer(initial_radius, final_radius, eccentricity, gravitational_parameter=__earth):
    """ Finds the delta v values required to transfer between two circular coplanar orbits along with the
    required burn angles.

    :param initial_radius: (float) The radius of the initial circular orbit.
    :param final_radius: (float) The radius of the final circular orbit.
    :param eccentricity: (float) The eccentricity of the desired transfer orbit.
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (list) the delta v required to go from the original orbit to the transfer orbit,
    the delta v required to go from the transfer orbit to the desired orbit,
    the burn angle for the first delta v,
    the burn angle for the second delta v.
    """

    def __delta_v_general(circle_speed, transfer_speed, radius, momentum):
        """ Calculates delta v.

        :param circle_speed: (float) The speed of the circular orbit at the radius distance.
        :param transfer_speed: (float) The speed of the transfer orbit at the radius distance.
        :param radius: (float) The distance to the transfer point.
        :param momentum: (float) The angular momentum of the transfer orbit.
        :return: (float) The delta v.
        """

        cosine_flight_path_angle = momentum/(radius*transfer_speed)
        return (circle_speed**2 + transfer_speed**2 - 2*circle_speed*transfer_speed*cosine_flight_path_angle)**0.5

    def __burn_angle(circle_speed, transfer_speed, delta_v):
        """ The burn angle between the initial orbit velocity vector to the delta v velocity vector.

        :param circle_speed: (float) The speed in the circular orbit.
        :param transfer_speed: (float) The speed in the transfer orbit.
        :param delta_v: (float) The delta v needed to transfer between the circular and transfer orbits.
        :return: (float) The burn angle.
        """

        return math.pi - math.acos((delta_v**2 + circle_speed**2 - transfer_speed**2)/(2*delta_v*circle_speed))

    a = semi_major_axis(radii=True, radius_one=initial_radius, radius_two=final_radius)
    semi_latus_rectum = a*(1-eccentricity**2)
    periapsis = periapsis_length(semi_latus_rectum, eccentricity, semi_major_axis=False)
    apoapsis = apoapsis_length(semi_latus_rectum, eccentricity, semi_major_axis=False)
    if periapsis > min(initial_radius, final_radius) or apoapsis < max(initial_radius, final_radius):
        raise Exception('Invalid semi_latus_rectum and/or eccentricity value(s).')

    angular_momentum_transfer = (gravitational_parameter*semi_latus_rectum)**0.5
    initial_speed_circular = circular_speed(initial_radius, gravitational_parameter)
    initial_speed_transfer = vis_viva(initial_radius, a, gravitational_parameter)
    final_speed_transfer = vis_viva(final_radius, a, gravitational_parameter)
    final_speed_circular = circular_speed(final_radius, gravitational_parameter)

    delta_v_one = __delta_v_general(initial_speed_circular, initial_speed_transfer, initial_radius,
                                    angular_momentum_transfer)
    delta_v_two = __delta_v_general(final_speed_circular, final_speed_transfer, final_radius,
                                    angular_momentum_transfer)
    burn_angle_one = __burn_angle(initial_speed_circular, initial_speed_transfer, delta_v_one)
    burn_angle_two = __burn_angle(final_speed_transfer, final_speed_circular, delta_v_two)

    if initial_radius < final_radius:
        burn_angle_one *= -1
    else:
        burn_angle_two *= -1

    return delta_v_one, delta_v_two, burn_angle_one, burn_angle_two


def simple_plane_change(radius, inclination_change, gravitational_parameter=__earth):
    """ Finds the delta v value required for a plane change between two circular orbits
    with no change in speed along with the burn angle.

    :param radius: (float) The radius of the circular orbit.
    :param inclination_change: (float) The angle between the current orbit and the desired orbit in radians.
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (list) The delta v and the burn angle.
    """

    speed = circular_speed(radius, gravitational_parameter)
    delta_v = 2*speed*math.sin(inclination_change/2)
    burn_angle = math.pi - math.acos(delta_v/(2*speed))
    return delta_v, burn_angle


def transfer_time(initial_radius, final_radius, general=False, eccentricity=0.1, rounding=None,
                  gravitational_parameter=__earth):
    """ The time of flight during a hohmann, bi elliptic, or general transfer orbit.

    :param initial_radius: (float) The periapsis distance of the transfer orbit.
    :param final_radius: (float) The apoapsis distance of the transfer orbit.
    :param general: (bool) If True, will determine the transfer time for some general transfer.
    :param eccentricity: (float) The eccentricity of the transfer orbit (default is 0.1).
    :param rounding: (int or None) Number that indicates the amount of decimal places to round to (default is None).
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :return: (float) The transfer time.
    """

    a = semi_major_axis(radii=True, radius_one=initial_radius, radius_two=final_radius)
    if not general:
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


def rocket_equation(exhaust_velocity, initial_mass, final_mass):
    """ Finds the delta v due to engine burn of a rocket in the case of no external forces.

    :param exhaust_velocity: (float) The exhaust velocity relative to the center of mass of the rocket.
    :param initial_mass: (float) The initial mass of the rocket (before the burn).
    :param final_mass: (float) The final mass of the rocket (after the burn).
    :return: (float) The change in velocity from before and after the burn; the delta v.
    """

    return -exhaust_velocity*math.log(initial_mass/final_mass)


def __delta_v(radius, semi_major_axis_transfer_orbit, gravitational_parameter):
    """ The delta v between a circular orbit and an elliptical transfer orbit.

    :param radius: (float) The radius of the orbit.
    :param semi_major_axis_transfer_orbit: (float) The semi-major axis of the transfer orbit.
    :param gravitational_parameter: (float) The gravitational parameter.
    :return: (float) The delta v.
    """

    return abs(vis_viva(radius, semi_major_axis_transfer_orbit, gravitational_parameter) -
               circular_speed(radius, gravitational_parameter))
