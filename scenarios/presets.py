import math
import numpy as np
import random as ran
from orbits_GUI.sim.sphere import Sphere
from orbits_GUI.astro.params import Earth, Moon
from orbits_GUI.astro.rfunc import sat_data
from orbits_GUI.astro.vectors import elements_multiple


def satellites(rows=30, radius=65.0, simple=False, fast=False):
    """ Animates satellite orbits around Earth with given satellite data. """

    def f(val, ins, mass=False):
        if mass:
            x = list(val)
        else:
            x = [val]*len(semi_latus_rectum)
        x.insert(0, ins)
        return x

    row_indices = np.arange(rows)
    data = sat_data(row_indices=row_indices)
    semi_latus_rectum, eccentricity, inclination = data[0], data[1], data[2]
    loan, pa, ea = [], [], []
    angles = np.arange(0, 2*math.pi, 0.05)
    for i in range(len(semi_latus_rectum)):
        loan.append(ran.choice(angles))
        pa.append(ran.choice(angles))
        ea.append(ran.choice(angles))

    vectors = elements_multiple(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity, inclination=inclination,
                                longitude_of_ascending_node=loan, periapsis_angle=pa, epoch_angle=ea)

    positions = vectors[0]
    velocities = vectors[1]
    positions.insert(0, (0, 0, 0))
    velocities.insert(0, (0, 0, 0))
    masses = f(data[3], Earth.mass, mass=True)
    radii = f(radius, Earth.radius)
    rotations = f(0, Earth.angular_rotation)
    textures = f(None, Earth.texture)
    names = [str(Earth()), 'Satellite']

    spheres = []
    s = Sphere(pos=positions[0], vel=velocities[0], mass=masses[0], radius=radii[0], rotation_speed=rotations[0],
               texture=textures[0], name=names[0], massive=True, primary=None, simple=False)
    spheres.append(s)
    if fast:
        massive = False
    else:
        massive = True
    for p, v, m, ra, ro, t in zip(positions[1:], velocities[1:], masses[1:], radii[1:], rotations[1:], textures[1:]):
        spheres.append(Sphere(pos=p, vel=v, mass=m, radius=ra, rotation_speed=ro, texture=t,
                              name=f'{names[1]}_{len(spheres)}', massive=massive, primary=s, simple=simple))
    return spheres


def satellites_perturbed(rows=30, radius=65.0, perturbing_body=Moon, body_semi_latus_rectum=50000.0,
                         body_eccentricity=0.2, simple=False, fast=False):
    """ Animates satellite orbits around Earth with given satellite data along with perturbations
    added by another body. """

    def f(val, ins, mass=False):
        if mass:
            x = list(val)
        else:
            x = [val]*len(semi_latus_rectum)
        x.insert(0, ins)
        return x

    row_indices = np.arange(rows)
    data = sat_data(row_indices=row_indices)
    semi_latus_rectum = list(data[0]) + [body_semi_latus_rectum]
    eccentricity = list(data[1]) + [body_eccentricity]
    inclination = list(data[2]) + [perturbing_body.inclination]
    loan, pa, ea = [], [], []
    angles = np.arange(0, 2*math.pi, 0.05)
    for i in range(len(semi_latus_rectum)):
        loan.append(ran.choice(angles))
        pa.append(ran.choice(angles))
        ea.append(ran.choice(angles))

    vectors = elements_multiple(semi_latus_rectum=semi_latus_rectum, eccentricity=eccentricity, inclination=inclination,
                                longitude_of_ascending_node=loan, periapsis_angle=pa, epoch_angle=ea)

    positions = vectors[0]
    velocities = vectors[1]
    positions.insert(0, (0, 0, 0))
    velocities.insert(0, (0, 0, 0))
    masses = f(data[3], Earth.mass, mass=True) + [perturbing_body.mass]
    radii = f(radius, Earth.radius) + [perturbing_body.radius]
    rotations = f(0, Earth.angular_rotation) + [perturbing_body.angular_rotation]
    textures = f(None, Earth.texture) + [perturbing_body.texture]
    names = [str(Earth()), 'Satellite'] + [str(perturbing_body())] 

    spheres = []
    s = Sphere(pos=positions[0], vel=velocities[0], mass=masses[0], radius=radii[0], rotation_speed=rotations[0],
               texture=textures[0], name=names[0], massive=True, primary=None, simple=False)
    spheres.append(s)
    spheres.append(Sphere(pos=positions[-1], vel=velocities[-1], mass=masses[-1], radius=radii[-1],
                          rotation_speed=rotations[-1], texture=textures[-1], name=names[-1], massive=True, primary=s,
                          simple=False, make_trail=True, retain=200, trail_color='red'))
    if fast:
        massive = False
    else:
        massive = True
    for p, v, m, ra, ro, t in zip(positions[1:-1], velocities[1:-1], masses[1:-1], radii[1:-1], rotations[1:-1],
                                  textures[1:-1]):
        spheres.append(Sphere(pos=p, vel=v, mass=m, radius=ra, rotation_speed=ro, texture=t,
                              name=f'{names[1]}_{len(spheres)}', massive=massive, primary=s, simple=simple))
    return spheres
