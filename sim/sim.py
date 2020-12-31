import datetime
import pyautogui
from vpython import canvas, rate, label, vector, mag, hat, cross
from orbits.sim.controls import Controls
from orbits.astro.transf import rodrigues_rotation
from orbits.sim.rfunc import decimal_length, round_to_place, integer_length, vector_to_np
from orbits.astro.maneuvers import Hohmann, BiElliptic, GeneralTransfer, SimplePlaneChange


class Simulate:
    """ Simulates a system of orbiting spheres within VPython using Newton's Law of Universal Gravitation. """

    def __init__(self):
        self._screen_width, self._screen_height = pyautogui.size()
        self._scene = canvas(width=self._screen_width-20)
        self._scene.lights[1].visible = False
        self._scene.lights.pop(1)
        self._controls = Controls(self._scene)
        self._gravity = self._controls.gravity
        self._time_stamp = None
        while True:
            self.__build_scenario()
            self.__simulate_scenario()

    def __universal_gravitation(self, sphere_one, sphere_two):
        """ Uses Newton's Law of Universal Gravitation to find the force of gravity on
        the first sphere due to the second sphere.

        :param sphere_one: (Sphere) VPython sphere for first sphere.
        :param sphere_two: (Sphere) VPython sphere for second sphere.
        :return: (VPython vector) Force vector due to gravity on sphere_one from sphere_two.
        """

        position_vector = sphere_one.pos - sphere_two.pos
        return -self._gravity*sphere_one.mass*sphere_two.mass*position_vector/mag(position_vector)**3

    def __update_forces(self):
        """ A list of the total gravitational force at one point in time on one sphere due to all
        other spheres (if they are considered 'massive'), for each sphere.

        :return: (list) The total gravitational force on each sphere.
        """

        def f(sph1):
            force = vector(0, 0, 0)
            for sph2 in self._massives:
                if sph1 is not sph2:
                    force += self.__universal_gravitation(sph1, sph2)
            return force

        return [f(sph) for sph in self._spheres]

    def __apply_impulse(self, sphere):
        """ Applies an impulse to the desired sphere. To be used in __update_spheres(). """

        for index, time in enumerate(sphere.times):
            seconds1 = (self._time - self._start_time).total_seconds()
            seconds2 = (time - self._start_time).total_seconds()
            if self._dt < 0:
                round(seconds2, decimal_length(self._dt))
            elif self._dt > 0:
                # A value of 10.1 would be rounded to the nearest 10's value (ignores the decimal places).
                seconds2 = round_to_place(seconds2, integer_length(self._dt) + 1)

            if seconds1 == seconds2:
                if isinstance(sphere.impulses[0], tuple):
                    delta_v = sphere.impulses[index][1]
                    burn_angle = sphere.impulses[index][2]
                else:
                    delta_v = sphere.impulses[1]
                    burn_angle = sphere.impulses[2]

                if sphere.maneuver is Hohmann or sphere.maneuver is BiElliptic:
                    sphere.vel += delta_v*hat(sphere.vel) + sphere.primary.vel
                elif sphere.maneuver is GeneralTransfer:
                    axis = vector_to_np(hat(cross(sphere._position, sphere._velocity)))
                    sphere.vel += vector(*rodrigues_rotation(axis, burn_angle).dot(vector_to_np(delta_v*hat(sphere.vel)))) + sphere.primary.vel
                elif sphere.maneuver is SimplePlaneChange:
                    axis = vector_to_np(hat(sphere._position))
                    sphere.vel += vector(*rodrigues_rotation(axis, burn_angle).dot(vector_to_np(delta_v*hat(sphere.vel)))) + sphere.primary.vel
                else:
                    #  If the user gives their own impulse instructions without a known maneuver title.
                    pass

    def __check_collisions(self, sph1):
        """
        Checks if the radii of any of the spheres intersect. If they do, applies a perfectly inelastic collision.
        The sphere with the greater mass, survives. To be used in __update_spheres().
        
        :return: (list) A list of Spheres that need to be removed from self._spheres due to collisions.
        """

        def f(left_over, destroyed):
            left_over.vel = (left_over.mass*left_over.vel + destroyed.mass*destroyed.vel) / \
                            (left_over.mass + destroyed.mass)
            left_over.mass += destroyed.mass
            deleted.append(destroyed)
            destroyed.delete()
            if destroyed == self._controls.labelled_sphere:
                self._controls.labelled_sphere = False

        deleted = []
        for sph2 in self._spheres:
            self._collisions = self._controls.collisions
            if self._collisions and self._controls.running:
                if (sph1 is not sph2) and (sph1.real_radius + sph2.real_radius > mag(sph1.pos - sph2.pos)):
                    if sph1.mass > sph2.mass:
                        f(sph1, sph2)
                    elif sph1.mass < sph2.mass:
                        f(sph2, sph1)
                    else:
                        deleted.append(sph1)
                        deleted.append(sph2)
                        if sph1 == self._controls.labelled_sphere or sph2 == self._controls.labelled_sphere:
                            self._controls.labelled_sphere = False
                        sph1.delete()
                        sph2.delete()
            elif not self._collisions:
                break
            elif not self._controls.running:
                while not self._controls.running:
                    pass
        return deleted

    def __update_spheres(self):
        """ Updates the sphere values. """

        deleted = []
        for sph, forces in zip(self._spheres, self.__update_forces()):
            sph.vel += forces*self._dt/sph.mass

            if sph.impulses:
                self.__apply_impulse(sph)

            if self._collisions:
                deleted = self.__check_collisions(sph)

            sph.pos += sph.vel*self._dt

            if sph.rotation_speed:
                sph.rotate(angle=sph.rotation_speed*self._dt)

        if len(deleted):
            for sph in deleted:
                self._spheres.remove(sph)

    def __build_scenario(self):
        """ The scenario building phase of the simulation. """

        self._scene.height = self._screen_height - self._controls.scene_height_sub

        if self._time_stamp:
            self._time_stamp.visible = False
            self._time_stamp = None

        while not self._controls.scenario_running:
            self._spheres = self._controls.spheres
            self._dt = self._controls.dt
            self._collisions = self._controls.collisions

    def __simulate_scenario(self):
        """ Simulates the given scenario. """

        self._scene.height = self._screen_height - self._controls.scene_height_sub

        if self._controls.start_time == 'now':
            self._start_time = datetime.datetime.utcnow()
            self._start_time -= datetime.timedelta(microseconds=self._start_time.microsecond)
        else:
            self._start_time = self._controls.start_time

        self._time = self._start_time
        self._time_stamp = label(text=f'Datetime: {self._time} UTC', align='left', height=20, pixel_pos=True, box=False,
                                 pos=vector(20, self._scene.height-28, 0))

        while self._controls.scenario_running:
            self._spheres = self._controls.spheres
            self._dt = self._controls.dt
            self._collisions = self._controls.collisions

            # According to .../vpython/rate_control.py line 19:
            # Unresolved bug: rate(X) yields only about 0.8X iterations per second.
            rate(self._controls.time_rate_seconds/(0.8*self._dt))

            if self._scene.height != self._screen_height - self._controls.scene_height_sub:
                self._scene.height = self._screen_height - self._controls.scene_height_sub
                self._time_stamp.pos = vector(20, self._scene.height-28, 0)

            if self._controls.labelled_sphere:
                self._controls.labelled_sphere.label.pos = vector(20, self._scene.height-100, 0)

            if self._controls.running:
                self._massives = [sph for sph in self._spheres if sph.massive]
                self.__update_spheres()
                self._time += datetime.timedelta(seconds=self._dt)
                self._time_stamp.text = f'Datetime: {self._time} UTC'
