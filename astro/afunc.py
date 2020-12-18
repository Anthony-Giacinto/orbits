"""
Astrodynamics functions.

Attributes:
    __earth: (float) The gravitational parameter for earth.

Functions:
    orbital_radius: Finds the distance from a focus to the edge of a conic section.
    vis_viva: Finds the speed of an orbiting object. The vis-viva equation.
    circular_speed: Finds the speed of an object in a circular orbit. Equivalent to vis_viva for a circular orbit.
    escape_velocity: Finds the local escape speed needed for some object orbiting some celestial body.
    escape_speed: Same as escape_velocity.
    hyperbolic_excess_speed: Finds the hyperbolic excess speed of an object.
    turning_angle: Finds the turning angle of an object in a hyperbolic orbit.
    periapsis_length: Finds the periapsis length of an orbit.
    apoapsis_length: Finds the apoapsis length of an orbit.
    apsis_lengths: Finds the both the periapsis and apoapsis lengths of an orbit.
    period: Finds the period of circular or elliptical orbits.
    angular_momentum: Finds the specific angular momentum vector of an orbiting object.
    node_vector: Finds the node vector of an orbit.
    eccentricity_vector: Finds the eccentricity vector.
    semi_latus_rectum: Finds the semilatus rectum of the orbit using angular momentum and the gravitational parameter.
    semi_major_axis: Finds the semi-major axis of the orbit.
    mechanical_energy: Finds the specific mechanical energy of the orbit.
    flight_time: Finds the time of flight between two points along an object's orbit.
    kepler_problem: If given initial position and velocity vectors and a time of flight, this function will
    calculate the final position and velocity vectors using the universal variable formulation
    and the Newton iteration method.
    gauss_problem: If given an initial position vector, final position vector, and time of flight between them,
    this function will find the initial velocity vector and final velocity vector using the universal variable
    formulation and the Newton iteration method.
"""


import math
import numpy as np
from orbits.astro.params import Earth


__earth = Earth.gravitational_parameter


def orbital_radius(semi_latus_rectum, eccentricity, true_anomaly):
    """ Finds the distance from a focus to the edge of a conic section.

    :param semi_latus_rectum: (float) The semilatus rectum of the orbit.
    :param eccentricity: (float) The eccentricity of the orbit.
    :param true_anomaly: (float) The true anomaly of the orbit.
    :return: (float) The radius value.
    """

    return semi_latus_rectum/(1 + eccentricity*math.cos(true_anomaly))


def vis_viva(radius, semi_major_axis, gravitational_parameter=__earth):
    """ Finds the speed of an orbiting object. The vis-viva equation.

    :param radius: (float) Distance to orbiting object.
    :param semi_major_axis: (float) Semi major axis of the object's orbit.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The speed of the object.
    """

    return (gravitational_parameter*(2/radius - 1/semi_major_axis))**0.5


def circular_speed(radius, gravitational_parameter=__earth):
    """ Finds the speed of an object in a circular orbit. Equivalent to vis_viva for a circular orbit.

    :param radius: (float) Radius of the circular orbit.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The speed of the object.
    """

    return (gravitational_parameter/radius)**0.5


def escape_velocity(position, gravitational_parameter=__earth):
    """ Finds the local escape speed needed for some object orbiting some celestial body.

    :param position: (float) The position magnitude of the object.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The escape speed at the given distance.
    """

    return (2*gravitational_parameter/position)**0.5


def escape_speed(position, gravitational_parameter=__earth):
    """ Calculates the local escape speed needed for some object orbiting some celestial body.
    Just returns the escape_velocity method.

    :param position: (float) The position magnitude of the object.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The escape speed at the given distance.
    """

    return escape_velocity(position, gravitational_parameter)


def hyperbolic_excess_speed(position, velocity, gravitational_parameter=__earth, esc_vel=False):
    """ Finds the hyperbolic excess speed of an object (the amount of speed the object would have 'left over').

    :param position: (float) The position magnitude of the object; used to find the escape velocity.
    :param velocity: (float) The velocity magnitude of the object.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :param esc_vel: (bool) to determine if the escape speed of the object is also returned (default is False).
    :return: (float or list(float)) The hyperbolic excess speed (and escape speed).
    """

    esc_velocity = escape_velocity(position, gravitational_parameter)
    exc_velocity = (velocity**2 - esc_velocity**2)**0.5
    if esc_vel:
        return exc_velocity, esc_velocity
    else:
        return exc_velocity


def turning_angle(eccentricity):
    """ Finds the turning angle of an object in a hyperbolic orbit (the angle between the two
    asymptotes of the hyperbola).

    :param eccentricity: (float) The eccentricity of the orbit.
    :return: (float) The turning angle in radians if eccentricity is greater than 1, else returns None.
    """

    if eccentricity > 1:
        return 2*math.asin(1/eccentricity)
    else:
        return None


def periapsis_length(distance, eccentricity, semi_major_axis=True):
    """ Finds the periapsis length of an orbit.

    :param distance: (float) Either the semi-major axis or the semilatus rectum of the orbit.
    :param eccentricity: (float) The eccentricity of the orbit.
    :param semi_major_axis: (bool) If True the distance value must be the semi-major axis, if False distance
    must be the semilatus rectum.
    :return: (float) The periapsis length.
    """

    if semi_major_axis:
        return distance*(1 - eccentricity)
    else:
        return distance/(1 + eccentricity)


def apoapsis_length(distance, eccentricity, semi_major_axis=True):
    """ Finds the apoapsis length of an orbit.

    :param distance: (float) Either the semi-major axis or the semilatus rectum of the orbit.
    :param eccentricity: (float) The eccentricity of the orbit.
    :param semi_major_axis: (bool) If True the distance value must be the semi-major axis, if False distance
    must be the semilatus rectum.
    :return: (float) The apoapsis length.
    """

    if semi_major_axis:
        return distance*(1 + eccentricity)
    else:
        return distance/(1 - eccentricity)


def apsis_lengths(distance, eccentricity, semi_major_axis=True):
    """ Finds both the periapsis and apoapsis lengths of an orbit using the periapsis_length and
    apoapsis_length methods. Apoapsis is None if eccentricity is greater than or equal to 1.

    :param distance: (float) Either the semi-major axis or the semilatus rectum of the orbit.
    :param eccentricity: (float) The eccentricity of the orbit.
    :param semi_major_axis: (bool) If True the distance value must be the semi-major axis, if False distance
    must be the semilatus rectum.
    :return: (list) The periapsis length and apoapsis length.
    """

    if 0 <= eccentricity < 1:
        return periapsis_length(distance, eccentricity, semi_major_axis=semi_major_axis), \
               apoapsis_length(distance, eccentricity, semi_major_axis=semi_major_axis)
    else:
        return periapsis_length(distance, eccentricity, semi_major_axis=semi_major_axis), None


def angular_momentum(position_vector, velocity_vector):
    """ Finds the specific angular momentum vector of an orbiting object.

    :param position_vector: (numpy array) The position vector of the orbiting object.
    :param velocity_vector: (numpy array) The velocity vector of the orbiting object.
    :return: (numpy array) The specific angular momentum vector.
    """

    return np.cross(position_vector, velocity_vector)


def node_vector(specific_angular_momentum_vector):
    """ Finds the node vector of an orbit; points along the line of nodes in the direction of the ascending node.

    :param specific_angular_momentum_vector: (numpy array) The specific angular momentum vector of the orbit.
    :return: (numpy array) The node vector.
    """

    return np.cross(np.array([0, 0, 1]), specific_angular_momentum_vector)


def eccentricity_vector(position_vector, velocity_vector, gravitational_parameter=__earth, magnitudes=False,
                        position_magnitude=0.0, velocity_magnitude=0.0):
    """ Finds the eccentricity vector, points from the focus of the orbit toward periapsis.

    :param position_vector: (numpy array) The position vector of the orbiting object.
    :param velocity_vector: (numpy array) The velocity vector of the orbiting object.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :param magnitudes: (bool) True if you want to provide the position and velocity magnitudes yourself, else will
    ignore position_magnitude and velocity_magnitude (default is False).
    :param position_magnitude: (float) The magnitude of the position vector (default is 0.0).
    :param velocity_magnitude: (float) The magnitude of the velocity vector (default is 0.0).
    :return: (numpy array) The eccentricity vector.
    """

    if magnitudes:
        position_mag = position_magnitude
        velocity_mag = velocity_magnitude
    else:
        position_mag = np.linalg.norm(position_vector)
        velocity_mag = np.linalg.norm(velocity_vector)
    return (1/gravitational_parameter) * \
           ((velocity_mag**2 - gravitational_parameter/position_mag)*position_vector
            - np.dot(position_vector, velocity_vector)*velocity_vector)


def semi_latus_rectum(specific_angular_momentum_magnitude, gravitational_parameter=__earth):
    """ Finds the semilatus rectum of the orbit using angular momentum and the gravitational parameter.

    :param specific_angular_momentum_magnitude: (float) The magnitude of the specific angular momentum.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The semilatus rectum.
    """

    return specific_angular_momentum_magnitude**2/gravitational_parameter


def semi_major_axis(semi_latus_rectum=0.0, eccentricity=0.0, radii=False, radius_one=0.0, radius_two=0.0):
    """ Finds the semi-major axis of the orbit.

    :param semi_latus_rectum: (float) The semilatus rectum of the orbit (default is 0.0).
    :param eccentricity: (float) The eccentricity of the orbit (default is 0.0).
    :param radii: (bool) If True uses radius_one and radius_two, else uses semi_latus_rectum and eccentricity
    (default is False).
    :param radius_one: (float) Distance from first focus (default is 0.0).
    :param radius_two: (float) Distance from second focus (default is 0.0).
    :return: (float) The semi-major axis of the orbit.
    """

    if radii:
        return (radius_one + radius_two)/2
    elif eccentricity != 1:
        return semi_latus_rectum/(1 - eccentricity**2)
    else:
        return None


def mechanical_energy(position_magnitude, velocity_magnitude, gravitational_parameter=__earth):
    """ Finds the specific mechanical energy of the orbit.

    :param position_magnitude: (float) The position magnitude of the orbiting object.
    :param velocity_magnitude: (float) The velocity magnitude of the orbiting object.
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The specific mechanical energy of the orbit.
    """

    return velocity_magnitude**2/2 - gravitational_parameter/position_magnitude


def period(semi_major_axis, gravitational_parameter=__earth):
    """ Finds the period of circular or elliptical orbits.

    :param semi_major_axis: (float) The semi-major axis of the orbit (radius if circular orbit).
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The period of the orbit.
    """

    return 2*math.pi*semi_major_axis**(3/2)/gravitational_parameter**0.5


def flight_time(eccentricity, semi_latus_rectum, true_anomaly_one, true_anomaly_two, periapsis_num=0,
                gravitational_parameter=__earth):
    """ Finds the time of flight between two points along an object's orbit using the eccentricity,
    semilatus rectum, and an initial and final true anomaly.

    :param eccentricity: (float) The eccentricity of the orbit.
    :param semi_latus_rectum: (float) The semi-latus rectum of the orbit.
    :param true_anomaly_one: (float) The initial true anomaly in radians.
    :param true_anomaly_two: (float) The final true anomaly in radians.
    :param periapsis_num: (int) The number of times the object passes through periapsis en route from true_anomaly_one
    to true_anomaly_two (default is 0).
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (float) The time of flight between true_anomaly_one and true_anomaly_two.
    """

    if 0 <= eccentricity < 1:
        e0 = math.acos((eccentricity + math.cos(true_anomaly_one))/(1 + eccentricity*math.cos(true_anomaly_one)))
        e1 = math.acos((eccentricity + math.cos(true_anomaly_two))/(1 + eccentricity*math.cos(true_anomaly_two)))
        a = semi_major_axis(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity)
        return ((a**3/gravitational_parameter)**0.5) * \
               (2*periapsis_num*math.pi + (e1 - eccentricity*math.sin(e1)) - (e0 - eccentricity*math.sin(e0)))
    elif eccentricity == 1:
        d0 = semi_latus_rectum**0.5*math.tan(true_anomaly_one/2)
        d1 = semi_latus_rectum**0.5*math.tan(true_anomaly_two/2)
        return (1/(2*gravitational_parameter**0.5)) * \
               ((semi_latus_rectum*d1 + d1**3/3) - (semi_latus_rectum*d0 + d0**3/3))
    elif eccentricity > 1:
        f0 = math.cosh((eccentricity + math.cos(true_anomaly_one))/(1 + eccentricity*math.cos(true_anomaly_one)))
        f1 = math.cosh((eccentricity + math.cos(true_anomaly_two))/(1 + eccentricity*math.cos(true_anomaly_two)))
        a = semi_major_axis(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity)
        if math.pi < true_anomaly_one < 2*math.pi:
            f0 *= -1
        if math.pi < true_anomaly_two < 2*math.pi:
            f1 *= -1
        return ((a**3/gravitational_parameter)**0.5) * \
               ((eccentricity*math.sinh(f1) - f1) - (eccentricity*math.sinh(f0) - f0))
    else:
        raise Exception('eccentricity must be greater than or equal to 0')


def kepler_problem(position_vector, velocity_vector, flight_time, trial_variable=0.0, uncertainty=0.0001,
                   gravitational_parameter=__earth):
    """ If given initial position and velocity vectors and a time of flight, this function will
    calculate the final position and velocity vectors using the universal variable formulation
    and the Newton iteration method.

    :param position_vector: (numpy array) The position vector of the orbiting body (relative to barycenter).
    :param velocity_vector: (numpy array) The velocity vector of the orbiting body (relative to barycenter).
    :param flight_time: (float) The desired time of flight for the orbiting object; time unit must be
    consistent with gravitational parameter.
    :param trial_variable: (float) Your initial guess for the universal variable (default is 0.0).
    :param uncertainty: (float) The desired uncertainty in the accuracy of t; t should equal flight_time
    (default is 0.0001).
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :return: (list) The final position vector, final velocity vector, the universal variable, and a check
    to determine the accuracy of the f and g values (equals 1 if f and g are accurate).
    """

    universal_variable = trial_variable
    position_magnitude, velocity_magnitude = np.linalg.norm(position_vector), np.linalg.norm(velocity_vector)
    reciprocal_semi_major_axis = -(velocity_magnitude**2 - (2*gravitational_parameter/position_magnitude)) / \
                                 gravitational_parameter
    while True:
        z = reciprocal_semi_major_axis*universal_variable**2
        if z == 0:
            c = 1/2
            s = 1/6
        elif z > 0:
            c = (1 - math.cos(z**0.5))/z
            s = (z**0.5 - math.sin(z**0.5))/z**(3/2)
        else:
            c = (1 - math.cosh((-z)**0.5))/z
            s = (math.sinh((-z)**0.5) - (-z)**0.5)/((-z)**3)**0.5
        t = np.dot(position_vector, velocity_vector)*universal_variable**2*c / \
            gravitational_parameter + (1 - position_magnitude*reciprocal_semi_major_axis)*universal_variable**3*s / \
                                      gravitational_parameter**0.5 + position_magnitude*universal_variable / \
                                                                     gravitational_parameter**0.5
        if flight_time - uncertainty < t < flight_time + uncertainty:
            break
        else:
            dtdx = universal_variable**2*c/gravitational_parameter**0.5 + \
                   (np.dot(position_vector, velocity_vector))*universal_variable*(1 - z*s) / \
                   gravitational_parameter + position_magnitude*(1 - z*c)/gravitational_parameter**0.5
            universal_variable += (flight_time - t)/dtdx

    f = 1 - c*universal_variable**2/position_magnitude
    g = t - s*universal_variable**3/gravitational_parameter**0.5
    position_vector_final = f*position_vector + g*velocity_vector
    position_magnitude_final = np.linalg.norm(position_vector_final)
    dfdt = gravitational_parameter**0.5*universal_variable*(z*s - 1)/(position_magnitude*position_magnitude_final)
    dgdt = 1 - c*universal_variable**2/position_magnitude_final
    velocity_vector_final = dfdt*position_vector + dgdt*velocity_vector
    check = f*dgdt - dfdt*g
    return position_vector_final, velocity_vector_final, universal_variable, check


def gauss_problem(initial_position, final_position, flight_time, trial_variable=0.0, uncertainty=0.0001,
                  gravitational_parameter=__earth, short=True):
    """ If given an initial position vector, final position vector, and time of flight between them,
    this function will find the initial velocity vector and final velocity vector using the universal variable
    formulation and the Newton iteration method.

    :param initial_position: (numpy array) The initial position vector.
    :param final_position: (numpy array) The final position vector.
    :param flight_time: (float) The time of flight between initial_position and final_position; time unit must be
    consistent with gravitational parameter.
    :param trial_variable: (float) Your initial guess for the universal variable, z (default is 0.0).
    :param uncertainty: (float) The desired uncertainty in the accuracy of t; t should equal flight_time
    (default is 0.0001).
    :param gravitational_parameter: (float) The gravitational parameter of the main body
    (default is Earth.gravitational_parameter).
    :param short: (bool) True if using the short path and false if using the long path between the position vectors
    (default is True).
    :return: (list) The initial velocity, the final velocity, and the universal variable.
    """

    universal_variable = trial_variable
    initial_magnitude, final_magnitude = np.linalg.norm(initial_position), np.linalg.norm(final_position)
    theta = math.acos(np.dot(initial_position, final_position)/(initial_magnitude*final_magnitude))
    if short:
        direction_of_motion = np.sign(math.pi - theta)
    else:
        direction_of_motion = np.sign(theta - math.pi)
    a = direction_of_motion*(initial_magnitude*final_magnitude*(1 + math.cos(theta)))**0.5
    while True:
        if universal_variable == 0:
            c = 1/2
            s = 1/6
        elif universal_variable > 0:
            c = (1 - math.cos(universal_variable**0.5))/universal_variable
            s = (universal_variable**0.5 - math.sin(universal_variable**0.5))/universal_variable**(3/2)
        else:
            c = (1 - math.cosh((-universal_variable)**0.5))/universal_variable
            s = (math.sinh((-universal_variable)**0.5) - (-universal_variable)**0.5)/((-universal_variable)**3)**0.5
        y = initial_magnitude + final_magnitude - a*(1 - universal_variable*s)/c**0.5
        if np.sign(y) >= 0:
            x = (y/c)**0.5
        else:
            raise Exception('y cannot be a negative value')
        t = (1/gravitational_parameter**0.5)*(x**3*s + a*y**0.5)
        if flight_time - uncertainty < t < flight_time + uncertainty:
            break
        else:
            if universal_variable == 0:
                dcdz = 1/24
                dsdz = 1/120
            else:
                dcdz = (1 - universal_variable*s - 2*c)/(2*universal_variable)
                dsdz = (c - 3*s)/(2*universal_variable)
            dtdz = (1/gravitational_parameter)**0.5*(x**3*(dsdz - 3*s*dcdz/2*c) + (a/8)*(3*s*y**0.5/c + a/x))

            if short:
                universal_variable += (flight_time - t)/dtdz
            else:
                universal_variable -= (flight_time - t)/dtdz

    f = 1 - y/initial_magnitude
    g = a*(y/gravitational_parameter)**0.5
    dgdt = 1 - y/final_magnitude
    initial_velocity = (final_position - f*initial_position)/g
    final_velocity = (dgdt*final_position - initial_position)/g
    return initial_velocity, final_velocity, universal_variable
