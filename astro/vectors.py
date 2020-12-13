"""
Contains classes for getting the position and velocity vectors of spacecraft in the geocentric-equatorial frame.

Functions:
    elements_multiple: Uses Elements class to find position and velocity vectors of multiple orbiting bodies.

Classes:
    Elements: Finds the position and velocity vectors of the orbiting body using classical orbital elements.
    DetermineElements: Finds classical orbital elements using position and velocity vectors in the
    geocentric-equatorial frame.
    DopplerRadar: Contains the position and velocity vectors of a satellite in the geocentric-equatorial frame
    (and topocentric frame) if given doppler radar position and velocity measurements.
    Radar: Contains the position and velocity vectors of a satellite in the geocentric-equatorial frame if given
    three radar position measurements.
"""


import math
import numpy as np
from orbits_GUI.astro.params import Earth
from orbits_GUI.astro.afunc import orbital_radius, angular_momentum, node_vector, eccentricity_vector, \
    semi_latus_rectum, semi_major_axis, mechanical_energy
from orbits_GUI.astro.rfunc import station_position
from orbits_GUI.astro.transf import peri_to_geo, peri_to_geo_i, peri_to_geo_e, topo_to_geo


class Elements:
    """ Finds the position and velocity vectors of the orbiting body from the given classical orbital elements
     (vectors are given in the Geocentric-Equatorial frame).

     Instance Attributes:
        semi_latus_rectum: (float) The semilatus rectum of the orbit (default is 0.0).
        eccentricity: (float) The eccentricity of the orbit (default is 0.0).
        inclination: (float) The inclination of the orbit (default is 0.0).
        longitude_of_ascending_node: (float) The longitude of the ascending node (default is 0.0).
        periapsis_angle: (float) Either the argument of periapsis or the longitude of periapsis (default is 0.0).
        epoch_angle: (float) Either the true anomaly, argument of latitude, or true longitude (default is 0.0).
        gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
        degrees: (bool) True if all angles are given in degrees, False if radians (default is False).

     Property Objects:
         position: (numpy array) The position vector of the orbiting body in the Geocentric-Equatorial frame.
         velocity: (numpy array) The velocity vector of the orbiting body in the Geocentric-Equatorial frame.

     Notes:
        If eccentricity is not 0 and inclination is not 0 or pi, give:
            longitude_of_ascending_node, the argument of periapsis for the periapsis_angle,
            the true anomaly for the epoch_angle
        If eccentricity is not 0 and inclination is 0 or pi, give:
            longitude of periapsis for the periapsis_angle, the true anomaly for the epoch_angle
        If eccentricity is 0 and inclination is not 0 or pi, give:
            longitude_of_ascending_node, the argument of latitude for the epoch_angle
        If eccentricity is 0 and inclination is 0 or pi, give:
            the true longitude for the epoch_angle
     """

    def __init__(self, semi_latus_rectum=0.0, eccentricity=0.0, inclination=0.0, longitude_of_ascending_node=0.0,
                 periapsis_angle=0.0, epoch_angle=0.0, gravitational_parameter=Earth.gravitational_parameter,
                 degrees=False):
        """
        :param semi_latus_rectum: (float) The semilatus rectum of the orbit (default is 0.0).
        :param eccentricity: (float) The eccentricity of the orbit (default is 0.0).
        :param inclination: (float) The inclination of the orbit (default is 0.0).
        :param longitude_of_ascending_node: (float) The longitude of the ascending node (default is 0.0).
        :param periapsis_angle: (float) Either the argument of periapsis or the longitude of periapsis (default is 0.0).
        :param epoch_angle: (float) Either the true anomaly, argument of latitude, or true longitude (default is 0.0).
        :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
        :param degrees: (bool) True if all angles are given in degrees, False if radians (default is False).
        """

        self.semi_latus_rectum = semi_latus_rectum
        self.eccentricity = eccentricity
        self._inclination = inclination
        self._longitude_of_ascending_node = longitude_of_ascending_node
        self._periapsis_angle = periapsis_angle
        self._epoch_angle = epoch_angle
        self.gravitational_parameter = gravitational_parameter
        self.degrees = degrees
        self._chosen_matrix = None

    def __vector_conditions(self, vector):
        """ Transforms the input vector from the perifocal frame to geocentric equatorial if necessary.

        :param vector: (numpy array) The vector to transform.
        :return: (numpy array) The vector (transformed, if necessary).
        """

        if self.eccentricity != 0 and math.sin(self.inclination) != 0:
            self._chosen_matrix = peri_to_geo(self.inclination, self.longitude_of_ascending_node, self.periapsis_angle)
            return self._chosen_matrix.dot(vector)
        elif self.eccentricity != 0 and math.sin(self.inclination) == 0:
            self._chosen_matrix = peri_to_geo_i(self.periapsis_angle)
            return self._chosen_matrix.dot(vector)
        elif self.eccentricity == 0 and math.sin(self.inclination) != 0:
            self._chosen_matrix = peri_to_geo_e(self.inclination, self.longitude_of_ascending_node)
            return self._chosen_matrix.dot(vector)
        else:
            return vector

    def __deg(self, attr):
        if self.degrees:
            return math.radians(attr)
        else:
            return attr

    @property
    def inclination(self):
        return self.__deg(self._inclination)

    @property
    def longitude_of_ascending_node(self):
        return self.__deg(self._longitude_of_ascending_node)

    @property
    def periapsis_angle(self):
        return self.__deg(self._periapsis_angle)

    @property
    def epoch_angle(self):
        return self.__deg(self._epoch_angle)

    @property
    def position(self):
        """ The position vector of the orbiting body in the Geocentric-Equatorial frame. """

        position_magnitude = orbital_radius(self.semi_latus_rectum, self.eccentricity, self.epoch_angle)
        position_vector = position_magnitude*np.array([math.cos(self.epoch_angle), math.sin(self.epoch_angle), 0])
        return self.__vector_conditions(position_vector)

    @property
    def velocity(self):
        """ The velocity vector of the orbiting body in the Geocentric-Equatorial frame. """

        velocity_magnitude = (self.gravitational_parameter/self.semi_latus_rectum)**0.5
        velocity_vector = velocity_magnitude * \
                          np.array([-math.sin(self.epoch_angle), self.eccentricity + math.cos(self.epoch_angle), 0])
        return self.__vector_conditions(velocity_vector)


def elements_multiple(semi_latus_rectum, eccentricity, inclination, longitude_of_ascending_node, periapsis_angle,
                      epoch_angle, gravitational_parameter=Earth.gravitational_parameter, degrees=False):
    """
    Finds the position and velocity vectors of multiple orbiting bodies from the given classical orbital
    elements (vectors are given in the Geocentric-Equatorial frame).

    :param semi_latus_rectum: (list) Tuple of semilatus rectums for each orbit.
    :param eccentricity: (list) Tuple of eccentricities for each orbit.
    :param inclination: (list) Tuple of inclinations for each orbit.
    :param longitude_of_ascending_node: (list) Tuple of longitudes of the ascending node for each orbit.
    :param periapsis_angle: (list) Tuple of periapsis angles for each orbit; Either the argument of periapsis
    or the longitude of periapsis.
    :param epoch_angle: (list) Tuple of epoch angles for each orbit; Either the true anomaly, argument of latitude,
    or true longitude.
    :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
    :param degrees: (bool) True if all angles are given in degrees, False if radians (default is False).
    :return: (list(lists)) The positions and velocities.
    """

    positions, velocities = [], []
    for slr, e, i, loan, pa, ea in zip(semi_latus_rectum, eccentricity, inclination, longitude_of_ascending_node,
                                       periapsis_angle, epoch_angle):
        vectors = Elements(semi_latus_rectum=slr, eccentricity=e,  inclination=i, periapsis_angle=pa,
                           longitude_of_ascending_node=loan, epoch_angle=ea,
                           gravitational_parameter=gravitational_parameter, degrees=degrees)
        positions.append(vectors.position)
        velocities.append(vectors.velocity)
    return positions, velocities


class DetermineElements:
    """ Finds orbital elements using position and velocity vectors in the Geocentric-Equatorial frame.

    Instance Attributes:
        position_vector: (numpy array) Position vector from the center of the main body to the orbiting body.
        velocity_vector: (numpy array) Velocity vector of the orbiting body relative to the main body.
        gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).

    Property Objects:
        position_magnitude: (float) The magnitude of position_vector.
        velocity_magnitude: (float) The magnitude of velocity_vector.
        specific_angular_momentum_vector: (numpy array) The specific angular momentum vector of the orbit.
        specific_angular_momentum_magnitude: (float) The magnitude of the specific_angular_momentum_vector.
        node_vector: (numpy array) The node vector; points along the line of nodes in the direction of the
        ascending node.
        node_magnitude: (float) The magnitude of the node_vector.
        eccentricity_vector: (numpy array) The eccentricity vector; points from the focus of the orbit toward periapsis.
        eccentricity: (float) The magnitude of the eccentricity vector (a.k.a. eccentricity).
        semi_latus_rectum: (float) The semilatus rectum of the orbit.
        semi_major_axis: (float) The semi-major axis of the orbit.
        specific_mechanical_energy: (float) The specific mechanical energy of the orbit.
        inclination: (float) The inclination of the orbit in radians.
        longitude_of_ascending_node: (float) The longitude of the ascending node in radians.
        argument_of_periapsis: (float) The argument of periapsis in radians.
        true_anomaly: (float) The true anomaly at epoch in radians.
        longitude_of_periapsis: (float) The longitude of periapsis in radians.
        argument_of_latitude: (float) The argument of latitude at epoch in radians.
        true_longitude: (float) The true longitude at epoch in radians.
        conic_section: (str) The conic section of the orbit.
    """

    def __init__(self, position_vector, velocity_vector, gravitational_parameter=Earth.gravitational_parameter):
        """
        :param position_vector: (numpy array) Position vector from the center of the main body to the orbiting body.
        :param velocity_vector: (numpy array) Velocity vector of the orbiting body relative to the main body.
        :param gravitational_parameter: (float) Gravitational parameter (default is Earth.gravitational_parameter).
        """

        self.position_vector = position_vector
        self.velocity_vector = velocity_vector
        self.gravitational_parameter = gravitational_parameter

    @property
    def position_magnitude(self):
        """ The magnitude of position_vector. """

        return np.linalg.norm(self.position_vector)

    @property
    def velocity_magnitude(self):
        """ The magnitude of velocity_vector. """

        return np.linalg.norm(self.velocity_vector)

    @property
    def specific_angular_momentum_vector(self):
        """ The specific angular momentum vector of an orbit; perpendicular to the plane of the orbit. """

        return angular_momentum(self.position_vector, self.velocity_vector)

    @property
    def specific_angular_momentum_magnitude(self):
        """ The magnitude of the specific_angular_momentum_vector. """

        return np.linalg.norm(self.specific_angular_momentum_vector)

    @property
    def node_vector(self):
        """ The node vector; points along the line of nodes in the direction of the ascending node. """

        return node_vector(self.specific_angular_momentum_vector)

    @property
    def node_magnitude(self):
        """ The magnitude of the node_vector. """

        return np.linalg.norm(self.node_vector)

    @property
    def eccentricity_vector(self):
        """ The eccentricity vector, points from the focus of the orbit toward perigee. """

        return eccentricity_vector(self.position_vector, self.velocity_vector, self.gravitational_parameter,
                                   magnitudes=True, position_magnitude=self.position_magnitude,
                                   velocity_magnitude=self.velocity_magnitude)

    @property
    def eccentricity(self):
        """ The magnitude of the eccentricity vector (a.k.a. eccentricity). """

        return np.linalg.norm(self.eccentricity_vector)

    @property
    def semi_latus_rectum(self):
        """ The semilatus rectum of the orbit. """

        return semi_latus_rectum(self.specific_angular_momentum_vector, self.gravitational_parameter)

    @property
    def semi_major_axis(self):
        """ The semi-major axis of the orbit. """

        return semi_major_axis(semi_latus_rectum=self.semi_latus_rectum, eccentricity=self.eccentricity)

    @property
    def specific_mechanical_energy(self):
        """ The specific mechanical energy of the orbit. """

        return mechanical_energy(self.position_magnitude, self.velocity_magnitude, self.gravitational_parameter)

    @property
    def inclination(self):
        """ The inclination of the orbit (angle). """

        if self.specific_angular_momentum_magnitude == 0:
            return None
        else:
            return math.acos(np.dot(self.specific_angular_momentum_vector, np.array([0, 0, 1])) /
                             self.specific_angular_momentum_magnitude)

    @property
    def longitude_of_ascending_node(self):
        """ The longitude of the ascending node (angle). """

        if self.node_magnitude == 0:
            return None
        else:
            return math.acos(np.dot(self.node_vector, np.array([1, 0, 0])) / self.node_magnitude)

    @property
    def argument_of_periapsis(self):
        """ The argument of periapsis (angle). """

        if self.node_magnitude == 0 or self.eccentricity == 0:
            return None
        else:
            return math.acos(np.dot(self.node_vector, self.eccentricity_vector) /
                             (self.node_magnitude * self.eccentricity))

    @property
    def true_anomaly(self):
        """ The true anomaly at epoch (angle). """

        if self.eccentricity == 0 or self.position_magnitude == 0:
            return None
        else:
            return math.acos(np.dot(self.eccentricity_vector, self.position_vector) /
                             (self.eccentricity * self.position_magnitude))

    @property
    def longitude_of_periapsis(self):
        """ The longitude of periapsis (angle). """

        if self.eccentricity == 0:
            return None
        elif self.node_magnitude == 0:
            return math.cos(np.dot(self.eccentricity_vector, np.array([1, 0, 0])) / self.eccentricity) ** 0.5
        else:
            return self.longitude_of_ascending_node + self.argument_of_periapsis

    @property
    def argument_of_latitude(self):
        """ The argument of latitude at epoch (angle). """

        if self.node_magnitude == 0 or self.position_magnitude == 0:
            return None
        else:
            return math.acos(np.dot(self.node_vector, self.position_vector) /
                             (self.node_magnitude * self.position_magnitude))

    @property
    def true_longitude(self):
        """ The true longitude at epoch (angle). """

        if self.position_magnitude == 0:
            return None
        elif self.node_magnitude != 0 and self.eccentricity != 0:
            return self.longitude_of_ascending_node + self.argument_of_periapsis + self.true_anomaly
        elif self.node_magnitude == 0 and self.eccentricity != 0:
            return self.longitude_of_periapsis + self.true_anomaly
        elif self.node_magnitude != 0 and self.eccentricity == 0:
            return self.longitude_of_ascending_node + self.argument_of_latitude
        else:
            return math.acos(np.dot(self.position_vector, np.array([1, 0, 0])) / self.position_magnitude)

    @property
    def conic_section(self):
        """ The conic section of the orbit. """

        if self.eccentricity == 0:
            return 'circle'
        elif 0 < self.eccentricity < 1:
            return 'ellipse'
        elif self.eccentricity == 1:
            return 'parabola'
        else:
            return 'hyperbola'


class DopplerRadar:
    """ Contains the position and velocity vectors of a satellite in the geocentric-equatorial frame
    (and topocentric frame) if given doppler radar position and velocity measurements.

    Properties:
        topo_position: (numpy array) The satellite position vector in the topocentric frame.
        Requires the positions argument.
        topo_velocity: (numpy array) The satellite velocity vector in the topocentric frame.
        Requires the positions and speeds arguments.
        geo_position: (numpy array) The satellite position vector in the geocentric frame.
        Requires the positions and station_location arguments.
        geo_velocity: (numpy array) The satellite velocity vector in the geocentric frame.
        Requires the positions, speeds, and station_location arguments.
        angular_velocity: (numpy array) The angular velocity of earth.
    """

    def __init__(self, positions, speeds, station_location, angular_velocity=Earth.angular_rotation, degrees=False):
        """
        :param positions: (tuple(float)) The distance, azimuth, and altitude of the spacecraft.
        :param speeds: (tuple(float)) The rate of change of distance, azimuth, and altitude of the spacecraft.
        :param station_location: (tuple(float)) The elevation, latitude, and the local sidereal time.
        :param angular_velocity: (float) The magnitude of the angular velocity of earth; gets converted into a
        numpy array (default is Earth.angular_rotation).
        :param degrees: (bool) True if all angles are given in degrees, False if radians (default is False).
        """

        self._distance = positions[0]
        self._azimuth = positions[1]
        self._altitude = positions[2]
        self._distance_dot = speeds[0]
        self._azimuth_dot = speeds[1]
        self._altitude_dot = speeds[2]
        self._elevation = station_location[0]
        self._latitude = station_location[1]
        self._local_sidereal_time = station_location[2]
        self._angular_velocity = angular_velocity
        self._degrees = degrees

    def __deg(self, attr):
        if self._degrees:
            return math.radians(attr)
        else:
            return attr

    def __transform(self):
        """ A matrix to transform a vector from the topocentric frame to the geocentric-equatorial frame. """

        return topo_to_geo(self.latitude, self.local_sidereal_time)

    @property
    def distance(self):
        return self.__deg(self._distance)

    @property
    def azimuth(self):
        return self.__deg(self._azimuth)

    @property
    def altitude(self):
        return self.__deg(self._altitude)

    @property
    def distance_dot(self):
        return self.__deg(self._distance_dot)

    @property
    def azimuth_dot(self):
        return self.__deg(self._azimuth_dot)

    @property
    def altitude_dot(self):
        return self.__deg(self._altitude_dot)

    @property
    def latitude(self):
        return self.__deg(self._latitude)

    @property
    def elevation(self):
        return self.__deg(self._elevation)

    @property
    def local_sidereal_time(self):
        return self.__deg(self._local_sidereal_time)

    @property
    def angular_velocity(self):
        return np.array([0, 0, self.__deg(self._angular_velocity)])

    @property
    def topo_position(self):
        """ The satellite position vector in the topocentric frame.
        Requires the positions argument. """

        return np.array([-self.distance*math.cos(self.altitude)*math.cos(self.azimuth),
                         self.distance*math.cos(self.altitude)*math.sin(self.azimuth),
                         self.distance*math.sin(self.altitude)])

    @property
    def topo_velocity(self):
        """ The satellite velocity vector in the topocentric frame.
        Requires the positions and speeds arguments. """

        return np.array([-self.distance_dot*math.cos(self.altitude)*math.cos(self.azimuth) +
                         self.distance*math.sin(self.altitude)*self.altitude_dot*math.cos(self.azimuth) +
                         self.distance*math.cos(self.altitude)*math.sin(self.azimuth)*self.azimuth_dot,
                         self.distance_dot*math.cos(self.altitude)*math.sin(self.azimuth) -
                         self.distance*math.sin(self.altitude)*self.altitude_dot*math.sin(self.azimuth) +
                         self.distance*math.cos(self.altitude)*math.cos(self.azimuth)*self.azimuth_dot,
                         self.distance_dot*math.sin(self.altitude) +
                         self.distance*math.cos(self.altitude)*self.altitude_dot])

    @property
    def geo_position(self):
        """ The satellite position vector in the geocentric-equatorial frame.
        Requires the positions and station_location arguments. """

        return np.dot(self.__transform(), self.topo_position) + \
               station_position(self.latitude, self.elevation, self.local_sidereal_time)

    @property
    def geo_velocity(self):
        """ The satellite velocity vector in the geocentric-equatorial frame.
        Requires the positions, speeds, and station_location arguments. """

        return np.dot(self.__transform(), self.topo_velocity + np.cross(self.angular_velocity, self.geo_position))


class Radar:
    """ Contains the position and velocity vectors of a satellite in the geocentric-equatorial frame if given
    three radar position measurements (the distance, azimuth, and altitude values for three measurements).

    Instance Attributes:
        positions_one: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement one (angles in radians).
        positions_two: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement two (angles in radians).
        positions_three: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement three (angles in radians).
        station_location: (list(float)) The latitude, elevation, and the local sidereal time all in radians.
        measurement: (int) The radar measurement number; 1, 2, or 3 (default is 1).
        gravitational_parameter: The gravitational parameter (default is Earth.gravitational_parameter).
        degrees: (bool) True if all angles are given in degrees, False if radians (default is False).

    Properties:
        position: (numpy array) The satellite position vector in the geocentric-equatorial frame.
        velocity: (numpy array) The satellite velocity vector in the geocentric-equatorial frame.
    """

    def __init__(self, positions_one, positions_two, positions_three, station_location, measurement=1,
                 gravitational_parameter=Earth.gravitational_parameter, degrees=False):
        """
        :param positions_one: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement one (angles in radians).
        :param positions_two: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement two (angles in radians).
        :param positions_three: (list(float)) The distance, azimuth, and altitude of the spacecraft for
        measurement three (angles in radians).
        :param station_location: (list(float)) The elevation, latitude, and the local sidereal time all in radians.
        :param measurement: (int) The radar measurement number; 1, 2, or 3 (default is 1).
        :param gravitational_parameter: The gravitational parameter (default is Earth.gravitational_parameter).
        :param degrees: (bool) True if all angles are given in degrees, False if radians (default is False).
        """

        self.degrees = degrees
        self._positions = [DopplerRadar(positions=pos, speeds=(0, 0, 0), station_location=station_location,
                                        degrees=self.degrees).geo_position
                            for pos in [positions_one, positions_two, positions_three]]
        self.__test_coplanar()
        self._magnitudes = [np.linalg.norm(pos) for pos in self._positions]
        self.measurement = measurement
        self.gravitational_parameter = gravitational_parameter
        self._chosen_position = self.__meas()

    def __test_coplanar(self):
        """ Checks that the three radar measurements describe three coplanar position vectors. """

        if np.dot(self._positions[0], np.cross(self._positions[1], self._positions[2])) != 0:
            raise Exception('The radar measurements do not describe three coplanar position vectors.')

    def __meas(self):
        """ Determines the chosen position measurement.

        :return: (list) The position vector and position magnitude.
        """

        if self.measurement == 2:
            return self._positions[1], self._magnitudes[1]
        elif self.measurement == 3:
            return self._positions[2], self._magnitudes[2]
        else:
            return self._positions[0], self._magnitudes[0]

    @property
    def position(self):
        """ The satellite position vector in the geocentric-equatorial frame. """

        return self._chosen_position[0]

    @property
    def velocity(self):
        """ The satellite velocity vector in the geocentric-equatorial frame. """

        cross_1_2 = np.cross(self._positions[0], self._positions[1])
        cross_2_3 = np.cross(self._positions[1], self._positions[2])
        cross_3_1 = np.cross(self._positions[2], self._positions[0])
        d_vec = cross_1_2 + cross_2_3 + cross_3_1
        n_vec = self._magnitudes[2]*cross_1_2 + self._magnitudes[0]*cross_2_3 + self._magnitudes[1]*cross_3_1
        s_vec = (self._magnitudes[1] - self._magnitudes[2])*self._positions[0] + \
                (self._magnitudes[2] - self._magnitudes[0])*self._positions[1] + \
                (self._magnitudes[0] - self._magnitudes[1])*self._positions[2]

        return (np.cross(d_vec, self._chosen_position[0])/self._chosen_position[1] + s_vec) * \
               (self.gravitational_parameter/(np.linalg.norm(d_vec)*np.linalg.norm(n_vec)))**0.5
