import datetime
import pyautogui
from vpython import vector, canvas, rate, mag, label
from orbits_GUI.sim.controls import Controls


class Simulate:
    """ Simulates a system of orbiting spheres within VPython using Newton's Law of Universal Gravitation
    with given starting positions, starting velocities, and masses. Perturbations in orbits from surrounding massive
    bodies are accounted for in the motion of the spheres.

    Methods:
        start: Starts the simulation program.
    """

    _gravity = _scene = _spheres = _massives = _time_stamp = _time = _dt = _frame_rate = _controls = None
    _screen_width, _screen_height = pyautogui.size()
    # display_width = 1900
    # display_height = 685


    def __force_gravity(self, sphere_one, sphere_two):
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
                    force += self.__force_gravity(sph1, sph2)
            return force

        return [f(sph) for sph in self._spheres]

    def __update_spheres(self):
        """ Updates the sphere values. """

        for sph, forces in zip(self._spheres, self.__update_forces()):
            sph.vel += forces*self._dt/sph.mass
            # if self.impulse and i in self._delta_v_indices and time in self._delta_v_times:
            #     self.__apply_impulse(i, time)
            sph.pos += sph.vel*self._dt
            if sph.rotation_speed:
                sph.rotate(angle=sph.rotation_speed*self._dt, axis=vector(0, 1, 0))
            if sph.labelled:
                sph.label.text = sph.label_text()

    def __build_scenario(self):
        """ The scenario building phase of the simulation. """

        if self._time_stamp:
            self._time_stamp.visible = False
            self._time_stamp = None

        while not self._controls.scenario_running:
            self._spheres = self._controls.spheres
            self._dt = self._controls.dt
            self._frame_rate = self._controls.frame_rate

    def __simulate_scenario(self):
        """ Simulates the given scenario. """

        self._massives = [sph for sph in self._spheres if sph.massive]

        #self._scene.height = 850

        self._time = datetime.datetime.now()
        self._time -= datetime.timedelta(microseconds=self._time.microsecond)
        self._time_stamp = label(text=f'{self._time.date()}\n{self._time.time()}', align='left', height=20,
                                 pixel_pos=True, pos=vector(20, self._scene.height-28, 0))

        while self._controls.scenario_running:
            self._dt = self._controls.dt
            self._frame_rate = self._controls.frame_rate
            rate(self._frame_rate)
            if self._controls.running:
                self.__update_spheres()
                self._time_stamp.text = f'{self._time.date()}\n{self._time.time()}'
                self._time += datetime.timedelta(seconds=self._dt)
            else:
                pass

    def __set_controls(self):
        """ Sets the controls for the GUI. """

        cont = Controls(self._scene)
        cont.set_controls()
        self._gravity = cont.gravity
        return cont

    def start(self):
        """ Starts the simulation program. """

        self._scene = canvas(width=self._screen_width-20, height=self._screen_height-395)
        #self._scene.resizable = False
        self._controls = self.__set_controls()

        while True:
            self.__build_scenario()
            self.__simulate_scenario()
