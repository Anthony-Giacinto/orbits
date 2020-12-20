import math
import numpy as np
from vpython import vector, dot, mag
from orbits.sim.sphere import Sphere
from orbits.sim.rfunc import sat_data, random_element_angles
from orbits.astro.params import Earth, Moon
from orbits.astro.vectors import Elements, elements_multiple
from orbits.astro.maneuvers import Hohmann, BiElliptic, GeneralTransfer, SimplePlaneChange


def satellites(rows=30, radius=65.0, show_axes=False):
    """ Animates satellite orbits around Earth with given satellite data. """

    row_indices = np.arange(rows)
    data = sat_data(row_indices=row_indices)
    semi_latus_rectum, eccentricity, inclination, masses, names = data
    loan, pa, ea = random_element_angles(len(semi_latus_rectum))

    vectors = elements_multiple(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity, inclination=inclination,
                                longitude_of_ascending_node=loan, periapsis_angle=pa, epoch_angle=ea)
    spheres = [Sphere(preset=Earth, show_axes=show_axes)]
    for p, v, m, n in zip(vectors[0], vectors[1], masses, names):
        spheres.append(Sphere(pos=p, vel=v, mass=m, radius=radius, name=n, massive=False,  primary=spheres[0],
                              simple=True))
    return spheres


def satellites_perturbed(rows=30, radius=65.0, perturbing_body=Moon, body_semi_latus_rectum=50000.0,
                         body_eccentricity=0.2, show_axes=False):
    """ Animates satellite orbits around Earth with given satellite data along with perturbations
    added by another body. """

    row_indices = np.arange(rows)
    data = sat_data(row_indices=row_indices)
    semi_latus_rectum = list(data[0]) + [body_semi_latus_rectum]
    eccentricity = list(data[1]) + [body_eccentricity]
    inclination = list(data[2]) + [perturbing_body.inclination]
    masses = list(data[3])
    names = list(data[4])
    loan, pa, ea = random_element_angles(len(semi_latus_rectum))

    vectors = elements_multiple(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity, inclination=inclination,
                                longitude_of_ascending_node=loan, periapsis_angle=pa, epoch_angle=ea)
    positions = vectors[0]
    velocities = vectors[1]
    spheres = [Sphere(preset=Earth, show_axes=show_axes)]
    spheres.append(Sphere(pos=positions.pop(), vel=velocities.pop(), preset=Moon, primary=spheres[0],
                          make_trail=True, retain=200, trail_color='red'))
    for p, v, m, n in zip(positions, velocities, masses, names):
        spheres.append(Sphere(pos=p, vel=v, mass=m, radius=radius, name=n, massive=False, primary=spheres[0],
                              simple=True))
    return spheres


def hohmann(initial_radius=Earth.radius+2000, final_radius=Earth.radius+10000, inclination=0.0,
            longitude_of_ascending_node=0.0, epoch_angle=0.0, mass=10.0, sat_radius=100.0, start_time=10000.0,
            show_axes=False):
    """ Animates a hohmann transfer of a satellite around Earth.

    :param initial_radius: (float) The radius of the initial circular orbit (default is Earth.radius+2000).
    :param final_radius: (float) The radius of the final circular orbit (default is Earth.radius+20000).
    :param inclination: (float) The inclination of the initial circular orbit in radians (default is 0.0).
    :param longitude_of_ascending_node: (float) The longitude of ascending node of the circular orbit in radians;
    does nothing if inclination is 0 (default is 0.0).
    :param epoch_angle: (float) The epoch angle of the circular orbit (default is 0.0).
    :param mass: (float) The mass of the satellite in kg (default is 10.0).
    :param sat_radius: (float) The radius of the satellite sphere (default is 100.0).
    :param start_time: (float) The amount of time that will pass within the simulation in seconds before the
    first impulse (default is 10000.0).
    :param show_axes: (bool) If True, will display the cartesian axes and labels of the spheres (default is False).
    """

    earth = Sphere(preset=Earth, show_axes=show_axes)
    vectors = Elements(semi_latus_rectum=initial_radius, inclination=inclination,
                       longitude_of_ascending_node=longitude_of_ascending_node, epoch_angle=epoch_angle, degrees=True)
    satellite = Sphere(pos=vectors.position, vel=vectors.velocity, mass=mass, radius=sat_radius, name='Satellite',
                       primary=earth, maneuver=Hohmann, make_trail=True, trail_limit=50,
                       initial_radius=initial_radius, final_radius=final_radius,
                       gravitational_parameter=Earth.gravitational_parameter, start_time=start_time)
    return earth, satellite


def bi_elliptic(initial_radius=Earth.radius+2000, final_radius=Earth.radius+7000, transfer_apoapsis=Earth.radius+40000,
                inclination=0.0, longitude_of_ascending_node=0.0, epoch_angle=0.0, mass=10.0, sat_radius=100.0,
                start_time=10000.0, show_axes=False):
    """ Animates a bi elliptic transfer of a satellite around Earth.

    :param initial_radius: (float) The radius of the initial circular orbit (default is Earth.radius+2000).
    :param final_radius: (float) The radius of the final circular orbit (default is Earth.radius+20000).
    :param transfer_apoapsis: (float) The distance from the center of the Earth to the apoapsis of the transfer ellipses
    (default is Earth.radius+40000).
    :param inclination: (float) The inclination of the initial circular orbit in radians (default is 0.0).
    :param longitude_of_ascending_node: (float) The longitude of ascending node of the circular orbit in radians;
    does nothing if inclination is 0 (default is 0.0).
    :param epoch_angle: (float) The epoch angle of the circular orbit (default is 0.0).
    :param mass: (float) The mass of the satellite in kg (default is 10.0).
    :param sat_radius: (float) The radius of the satellite sphere (default is 100.0).
    :param start_time: (float) The amount of time that will pass within the simulation in seconds before the
    first impulse (default is 10000.0).
    :param show_axes: (bool) If True, will display the cartesian axes and labels of the spheres (default is False).
    """

    earth = Sphere(preset=Earth, show_axes=show_axes)
    vectors = Elements(semi_latus_rectum=initial_radius, inclination=inclination,
                       longitude_of_ascending_node=longitude_of_ascending_node, epoch_angle=epoch_angle, degrees=True)
    satellite = Sphere(pos=vectors.position, vel=vectors.velocity, mass=mass, radius=sat_radius, name='Satellite',
                       primary=earth, maneuver=BiElliptic, make_trail=True, trail_limit=50,
                       initial_radius=initial_radius, final_radius=final_radius, transfer_apoapsis=transfer_apoapsis,
                       gravitational_parameter=Earth.gravitational_parameter, start_time=start_time)
    return earth, satellite


def general(initial_radius=Earth.radius+2000, final_radius=Earth.radius+20000, transfer_eccentricity=0.6,
            inclination=0.0, longitude_of_ascending_node=0.0, epoch_angle=0.0, mass=10.0, sat_radius=100.0,
            start_time=10000.0, show_axes=False):
    """ Animates a satellite performing a 'general' coplanar transfer around Earth.

    :param initial_radius: (float) The radius of the initial circular orbit (default is Earth.radius+2000).
    :param final_radius: (float) The radius of the final circular orbit (default is Earth.radius+20000).
    :param transfer_eccentricity: (float) The eccentricity of the transfer orbit (default is 0.6).
    :param inclination: (float) The inclination of the initial circular orbit in radians (default is 0.0).
    :param longitude_of_ascending_node: (float) The longitude of ascending node of the circular orbit in radians;
    does nothing if inclination is 0 (default is 0.0).
    :param epoch_angle: (float) The epoch angle of the circular orbit (default is 0.0).
    :param mass: (float) The mass of the satellite in kg (default is 10.0).
    :param sat_radius: (float) The radius of the satellite sphere (default is 100).
    :param start_time: (float) The amount of time that will pass within the simulation in seconds before the
    first impulse (default is 10000.0).
    :param show_axes: (bool) If True, will display the cartesian axes and labels of the spheres (default is False).
    """

    earth = Sphere(preset=Earth, show_axes=show_axes)
    vectors = Elements(semi_latus_rectum=initial_radius, inclination=inclination,
                       longitude_of_ascending_node=longitude_of_ascending_node, epoch_angle=epoch_angle, degrees=True)
    satellite = Sphere(pos=vectors.position, vel=vectors.velocity, mass=mass, radius=sat_radius, name='Satellite',
                       primary=earth, maneuver=GeneralTransfer, make_trail=True, trail_limit=50,
                       initial_radius=initial_radius, final_radius=final_radius, start_time=start_time,
                       transfer_eccentricity=transfer_eccentricity,
                       gravitational_parameter=Earth.gravitational_parameter)
    return earth, satellite


def plane_change(radius=Earth.radius+3000, inclination_one=20, inclination_two=30,
                 longitude_of_ascending_node=0.0, epoch_angle=0.0, mass=10.0, sat_radius=100.0, start_time=10000.0,
                 show_axes=False):
    """ Animates a satellite performing a simple plane change around Earth.

    :param radius: (float) The radius of the orbits (default is Earth.radius+2000).
    :param inclination_one: (float) The inclination of the initial orbit (default is 0.0).
    :param inclination_two: (float) The inclination of the final orbit (default is math.pi/3).
    :param longitude_of_ascending_node: (float) The longitude of ascending node of the circular orbit in radians;
    does nothing if inclination is 0 (default is 0.0).
    :param epoch_angle: (float) The epoch angle of the circular orbit (default is 0.0).
    :param mass: (float) The mass of the satellite in kg (default is 10.0).
    :param sat_radius: (float) The radius of the satellite sphere (default is 100.0).
    :param start_time: (float) The amount of time that will pass within the simulation in seconds before the
    first impulse (default is 10000.0).
    :param show_axes: (bool) If True, will display the cartesian axes and labels of the spheres (default is False).
    """

    earth = Sphere(preset=Earth, show_axes=show_axes)
    vectors = Elements(semi_latus_rectum=radius, inclination=inclination_one,
                       longitude_of_ascending_node=longitude_of_ascending_node, epoch_angle=epoch_angle, degrees=True)
    inclination_change = math.radians(inclination_two - inclination_one)
    satellite = Sphere(pos=vectors.position, vel=vectors.velocity, mass=mass, radius=sat_radius, name='Satellite',
                       primary=earth, maneuver=SimplePlaneChange, make_trail=True, trail_limit=50,
                       initial_radius=radius, start_time=start_time, inclination_change=inclination_change,
                       gravitational_parameter=Earth.gravitational_parameter)
    return earth, satellite


def earth_moon(show_axes=False):
    earth = Sphere(preset=Earth, show_axes=show_axes)
    loan, pa, ea = random_element_angles(1)
    vectors = Elements(semi_latus_rectum=Moon.semi_latus_rectum, eccentricity=Moon.eccentricity,
                       inclination=Moon.inclination, longitude_of_ascending_node=loan[0], periapsis_angle=pa[0],
                       epoch_angle=ea[0])
    r = vector(vectors.position[1], vectors.position[2], vectors.position[0]) - earth.pos
    theta = math.acos(dot(r, vector(0, 0, -1))/(mag(r)))
    moon = Sphere(pos=vectors.position, vel=vectors.velocity, preset=Moon, primary=earth, make_trail=True, retain=500)
    moon.rotate(angle=-theta)
    return earth, moon
