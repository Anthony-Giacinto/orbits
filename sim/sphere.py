import math
import random as ran
import numpy as np
from vpython import sphere, simple_sphere, vector, color, textures, local_light, label, arrow
from orbits_GUI.astro.params import gravity
from orbits_GUI.astro.vectors import Elements
from orbits_GUI.astro.maneuvers import Maneuver
from orbits_GUI.astro.transf import rodrigues_rotation, rotate_y


class Sphere(simple_sphere, sphere, Elements, Maneuver):
    """ Represents any massive object that might be travelling through space (planetoids, stars, spacecraft, etc).

    Class Attributes:
        light: (VPython local_light) A light object located at the Sphere pos; Created when luminous is True
        (default is None).
        label: (VPython label)
        shininess: (int) A measure of the reflectiveness of the Sphere (default is 0).
        up: (VPython vector) Affects the orientation of the Sphere (default is vector(0,1,0)).

    Instance Attributes:
        pos: (tuple/VPython vector) Position of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        vel: (tuple/VPython vector) Velocity of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        mass: (float) The mass of the sphere (default is 1.0).
        rotation_speed: (float) The rotational_speed of the Sphere in rads/s (default is 0.0).
        name: (str) The name of the Sphere (default is 'Sphere').
        simple: (bool) If True will generate VPython simple_sphere instead of sphere (default is False).
        massive: (bool) False indicates that the Sphere' mass can be considered negligible (default is True).
        luminous: (bool) If True, will create a VPython local_light object at the Sphere pos (default is False).
        labelled: (bool) If True, creates a VPython label that contains some Sphere attribute values
        (default is False).
        primary: (Sphere) The self.pos and self.vel values are with respect to the pos and vel of this primary
        (default is None).
        light_color: (str) The color of the class attribute, light (default is 'white').
        impulses: (tuple/tuple(tuples)) The impulse instructions
        ((time, delta v, burn angle), ...) or (time, delta v, burn angle) for only one impulse (default is None).
        maneuver: (class) A named maneuver class; will automatically created impulses instructions based off of
        the maneuver; will need to add the appropriate instance attributes for the maneuver.
        preset: (params class) Some pre-made parameters class (contains radius, mass, rotational speed, etc)
        (default is None).
        show_axes: (bool) If True, will display the cartesian axes and labels of the sphere;
        can be removed and/or replaced afterwards using toggle_axes() (default is False).
        obliquity: The angle of obliquity in radians (default is 0).

        The parameters from simple_sphere, sphere, Elements, and Maneuver are also available.

    Class Methods:
        label_text: The text for the VPython label; contains the name, primary, pos, vel, and mass.
        rotate: Rotates the Sphere about its axis.
        toggle_axes: Toggles on/off the cartesian axes of the sphere.
        update_axes: Updates the positions of the axes and axes labels.
        delete: Deletes the Sphere and removes any lights, labels, axes, and trails associated with the Sphere as well.
    """

    _xaxis = vector(0, 0, 1)
    _yaxis = vector(1, 0, 0)
    _zaxis = vector(0, 1, 0)
    _xarrow = _yarrow = _zarrow = light = label = None
    shininess = 0
    up = _zaxis

    def __init__(self, vel=(0.0,0.0,0.0), mass=1.0, rotation_speed=0.0, name='Sphere', simple=False, massive=True,
                 labelled=False, primary=None, light_color='white', impulses=None, maneuver=None, preset=None,
                 show_axes=False, obliquity=0, **kwargs):
        """
        :param pos: (tuple/VPython vector) Position of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        :param vel: (tuple/VPython vector) Velocity of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        :param mass: (float) The mass of the sphere (default is 1.0).
        :param rotation_speed: (float) The rotational_speed of the Sphere in rads/s (default is 0.0).
        :param name: (str) The name of the Sphere (default is 'Sphere').
        :param simple: (bool) If True will generate VPython simple_sphere instead of sphere (default is False).
        :param massive: (bool) False indicates that the Sphere' mass can be considered negligible (default is True).
        :param luminous: (bool) If True, will create a VPython local_light object at the Sphere pos (default is False).
        :param labelled: (bool) If True, creates a VPython label that contains some Sphere attribute values
        (default is False).
        :param primary: (Sphere) The self.pos and self.vel values are with respect to the pos and vel of this primary
        (default is None).
        :param light_color: (str) The color of the class attribute, light (default is 'white').
        :param impulses: (tuple/tuple(tuples)) The impulse instructions
        ((time, delta v, burn angle), ...) or (time, delta v, burn angle) for only one impulse (default is None).
        :param maneuver: (class) A named maneuver class; will automatically created impulses instructions based off of
        the maneuver; will need to add the appropriate instance attributes for the maneuver.
        :param preset: (params class) Some pre-made parameters class (contains radius, mass, rotational speed, etc)
        (default is None).
        :param show_axes: (bool) If True, will display the cartesian axes and labels of the sphere;
        can be removed and/or replaced afterwards using toggle_axes() (default is False).
        :param obliquity: The angle of obliquity in radians (default is 0).


        The parameters from simple_sphere, sphere, Elements, and Maneuver are also available.
        """

        self.primary = primary
        self.massive = massive
        self.light_color = light_color
        self._labelled = labelled
        self.preset = preset
        self.obliquity = obliquity

        # If a preset is given, uses preset attributes instead of the given attributes.
        if self.preset:
            self.mass = preset.mass
            self.rotation_speed = preset.angular_rotation
            self.grav_parameter = preset.gravitational_parameter
            self.name = str(preset())
            kwargs['radius'] = preset.radius
            kwargs['texture'] = preset.texture
            if isinstance(self.primary, Sphere):
                self.obliquity = preset.obliquity
                angles = np.arange(0, 2*math.pi, 0.05)
                arbitrary_r = rotate_y(ran.choice(angles)).dot(np.array([self._xaxis.x, self._xaxis.y, self._xaxis.z]))
                self.up = vector(*rodrigues_rotation(arbitrary_r, self.obliquity).
                                 dot(np.array([self._zaxis.x, self._zaxis.y, self._zaxis.z])))
        else:
            self.mass = mass
            self.rotation_speed = rotation_speed
            self.name = name
            self.grav_parameter = self.mass*gravity()

        keys = kwargs.keys()

        # If a maneuver class is given, will create the appropriate impulse instructions.
        # If impulses is given with no maneuver class given, will use those instructions instead.
        if maneuver is not None:
            attrs = ['initial_radius', 'final_radius', 'transfer_apoapsis', 'transfer_eccentricity',
                     'inclination_change', 'start_time']
            params = {elem: kwargs.pop(elem) for elem in attrs if elem in keys}
            Maneuver.__init__(self, maneuver=maneuver, gravitational_parameter=self.primary.grav_parameter, **params)
        else:
            self.impulses = impulses

        # If a maneuver class is given or own impulse instructions given, will get a list of the impulse times.
        if self.impulses is not None:
            try:
                self.times = list(zip(*self.impulses))[0]
            except TypeError:
                self.times = [self.impulses[0]]

        # If any of the below attributes are given, will calculate the associated pos and vel values.
        if ('semi_latus_rectum' or 'eccentricity' or 'inclination' or 'longitude_of_ascending_node'
            or 'periapsis_angle' or 'epoch_angle') in keys:
            attrs = ['semi_latus_rectum', 'eccentricity', 'inclination', 'longitude_of_ascending_node',
                     'periapsis_angle', 'epoch_angle']
            elements = [kwargs.pop(elem) for elem in attrs if elem in keys]
            Elements.__init__(self, *elements, gravitational_parameter=self.primary.grav_parameter)
            self._vel = self._velocity = self.vpython_rotation(self.velocity)
            kwargs['pos'] = self._position = self.vpython_rotation(self.position)
        else:
            self._vel = self._velocity = self.vpython_rotation(self.__try_vector(vel))
            if 'pos' in keys:
                self._position = kwargs['pos'] = self.vpython_rotation(self.__try_vector(kwargs['pos']))
            else:
                self._position = vector(0, 0, 0)

        # If primary is another Sphere, pos and vel are with respect to the primary;
        # This will update pos and vel to be with respect to the origin of the VPython reference frame and will
        # set the z-axis (self.up) for the sphere.
        if isinstance(self.primary, Sphere):
            kwargs['pos'] = self._position + self.primary.pos
            self._vel = self._velocity + self.primary.vel

        for col in ['color', 'trail_color', 'light_color']:
            if col == 'light_color':
                self.light_color = getattr(color, self.light_color)
            elif col in keys:
                if isinstance(kwargs[col], str):
                    kwargs[col] = getattr(color, kwargs[col])
                else:
                    kwargs[col] = self.__try_vector(kwargs[col])

        if 'texture' in keys and isinstance(kwargs['texture'], str):
            try:
                kwargs['texture'] = getattr(textures, kwargs['texture'])
            except AttributeError:
                pass

        kwargs['shininess'] = self.shininess
        kwargs['up'] = self.up
        if simple:
            self._type = 'simple_sphere'
            simple_sphere.__init__(self, **kwargs)
        else:
            self._type = 'sphere'
            sphere.__init__(self, **kwargs)

        self._luminous = self.emissive
        if self._luminous:
            self.__make_light()
        if self._labelled:
            self.__make_label()

        self.show_axes = show_axes
        if self.show_axes:
            self.__axes()

    def __str__(self):
        return self.name

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value):
        val = self.__try_vector(value)
        self._pos = self._position = val
        if self.light:
            self.light.pos = val
        if not self._constructing:
            if self._make_trail and self._interval > 0:
                self.addmethod('pos', val.value)
            else:
                self.addattr('pos')

    @property
    def vel(self):
        return self._vel
    @vel.setter
    def vel(self, value):
        self._vel = self._velocity = self.__try_vector(value)

    @property
    def luminous(self):
        return self._luminous
    @luminous.setter
    def luminous(self, value):
        self._luminous = self.emissive = value
        if self._luminous:
            self.__make_light()
        elif self.light:
            self.canvas.lights.remove(self.light)
            self.light.visible = False
            del self.light
            self.light = None

    def __make_light(self):
        self.light = local_light(pos=self.pos, color=self.light_color)

    @property
    def labelled(self):
        return self._labelled
    @labelled.setter
    def labelled(self, value):
        self._labelled = value
        if self._labelled:
            self.__make_label()
        elif self.label:
            self.label.visible = False
            del self.label
            self.label = None

    def label_text(self, places=3):
        """ The text for the VPython label; contains the name, primary, pos, vel, and mass.

        :param places: (int) The number of decimal places for pos and vel (default is 3).
        :return: (str) The label text.
        """

        pos = vector(round(self._position.x, places), round(self._position.y, places), round(self._position.z, places))
        vel = vector(round(self._velocity.x, places), round(self._velocity.y, places), round(self._velocity.z, places))
        if self.mass > 1000:
            m = '{:e}'.format(self.mass)
        name =     f'Name:     {self.name}'
        primary =  f'Primary:  {self.primary}'
        position = f'Position: {pos} km'
        velocity = f'Velocity: {vel} km/s'
        mass =     f'Mass:     {m} kg'
        return '\n'.join([name, primary, position, velocity, mass])

    def __make_label(self):
        self.label = label(text=self.label_text(), align='left', height=20,
                           pixel_pos=True, pos=vector(20, self.canvas.height-100, 0), box=False)

    def rotate(self, angle=None, axis=None, origin=None):
        """ Rotates the Sphere about its axis.

        :param angle: (float) The amount of desired rotation in radians (default is None).
        :param axis: (VPython vector) The axis of rotation (default is self.up).
        :param origin: (VPython vector) The rotation is relative to the origin; if None, its self.pos (default is None).
        """

        if not axis:
            a = self.up
        else:
            a = axis
        super(Sphere, self).rotate(angle=angle, axis=a, origin=origin)

    def __axes(self):
        arrows = {'pos': self.pos, 'length': 1.5*self.radius, 'shaftwidth': self.radius/100,
                  'headwidth': self.radius/30, 'headlength': self.radius/30, 'color': color.red}
        self._xarrow = arrow(axis=self._xaxis, **arrows)
        self._yarrow = arrow(axis=self._yaxis, **arrows)
        self._zarrow = arrow(axis=self._zaxis, **arrows)

        labels = {'box': False, 'opacity': 0}
        self._xarrow_label = label(text='X', pos=self.pos+self._xarrow.axis, **labels)
        self._yarrow_label = label(text='Y', pos=self.pos+self._yarrow.axis, **labels)
        self._zarrow_label = label(text='Z', pos=self.pos+self._zarrow.axis, **labels)

    def toggle_axes(self):
        if self.show_axes:
            self._xarrow.visible = self._yarrow.visible = self._zarrow.visible = self.show_axes = \
                self._xarrow_label.visible = self._yarrow_label.visible = self._zarrow_label.visible = False
            del self._xarrow, self._yarrow, self._zarrow, self._xarrow_label, self._yarrow_label, self._zarrow_label
        else:
            if not all([self._xarrow, self._yarrow, self._zarrow]):
                self.__axes()
            else:
                self._xarrow.visible = self._yarrow.visible = self._zarrow.visible = \
                    self._xarrow_label.visible = self._yarrow_label.visible = self._zarrow_label.visible = True
            self.show_axes = True

    def update_axes(self):
        self._xarrow.pos = self._yarrow.pos = self._zarrow.pos = self.pos
        self._xarrow_label.pos = self.pos+self._xarrow.axis
        self._yarrow_label.pos = self.pos+self._yarrow.axis
        self._zarrow_label.pos = self.pos+self._zarrow.axis

    def delete(self):
        """ Deletes the Sphere and removes any lights, labels, axes, and trails associated with the Sphere as well. """

        self.visible = self.luminous = self.labelled = False
        if self.show_axes:
            self.toggle_axes()
        self.clear_trail()
        self.__del__()

    @staticmethod
    def __try_vector(vect):
        try:
            return vector(*vect)
        except TypeError:
            return vect

    @staticmethod
    def vpython_rotation(v):
        return vector(v.y, v.z, v.x)
