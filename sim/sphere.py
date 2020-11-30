from vpython import sphere, simple_sphere, vector, color, textures, local_light, label
from orbits_GUI.astro.params import gravity


class Sphere(simple_sphere, sphere):
    """ Inherits sphere and simple_sphere from VPython with an option to choose between them. """

    def __init__(self, vel=(0.0, 0.0, 0.0), mass=1.0, rotation_speed=0.0, simple=False, massive=True, name='Sphere',
                 primary=None, light=None, light_color='white', labelled=False, label=None, _units='km',
                 shininess=0, up=vector(0, 1, 0),**kwargs):
        """
        :param pos: (tuple or VPython vector) Position of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        :param vel: (tuple or VPython vector) Velocity of the sphere; if primary is given, will be w.r.t the primary
        (default is vector(0, 0, 0)).
        """

        self.mass = mass
        self.rotation_speed = rotation_speed
        self.name = name
        self.primary = primary
        self.massive = massive
        self.light = light
        self.light_color = light_color
        self._labelled = labelled
        self.label = label
        self._units = _units
        self.grav_parameter = self.mass*gravity(self._units)
        self._velocity = self._vel = self.__try_vector(vel)
        if 'pos' in kwargs.keys():
            self._position = kwargs['pos'] = self.__try_vector(kwargs['pos'])
        #  If primary is another Sphere, updates pos and vel to be with respect to the origin of the reference frame.
        if isinstance(self.primary, Sphere):
            kwargs['pos'] = self._position + self.primary.pos
            self._vel = self._velocity + self.primary.vel
        for col in ['color', 'trail_color', 'light_color']:
            if col == 'light_color':
                self.light_color = getattr(color, self.light_color)
            elif col in kwargs.keys():
                if isinstance(kwargs[col], str):
                    kwargs[col] = getattr(color, kwargs[col])
                else:
                    kwargs[col] = self.__try_vector(kwargs[col])
        if 'texture' in kwargs.keys() and isinstance(kwargs['texture'], str):
            try:
                kwargs['texture'] = getattr(textures, kwargs['texture'])
            except AttributeError:
                pass
        kwargs = {'shininess': shininess, 'up': up, **kwargs}
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

    def __str__(self):
        return self.name

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value):
        self._pos = self._position = value
        if self.light:
            self.light.pos = value
        if not self._constructing:
            if self._make_trail and self._interval > 0:
                self.addmethod('pos', value.value)
            else:
                self.addattr('pos')

    @property
    def vel(self):
        return self._vel
    @vel.setter
    def vel(self, value):
        self._vel = self._velocity = value

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

    def label_text(self, list_form=False):
        pos = vector(round(self._position.x, 3), round(self._position.y, 3), round(self._position.z, 3))
        vel = vector(round(self._velocity.x, 3), round(self._velocity.y, 3), round(self._velocity.z, 3))
        name =     f'Name:     {self.name}'
        primary =  f'Primary:  {self.primary}'
        position = f'Position: {pos} km'
        velocity = f'Velocity: {vel} km'
        mass =     f'Mass:     {self.mass} kg'
        text_list = [name, primary, position, velocity, mass]
        if list_form:
            return text_list
        else:
            return '\n'.join(text_list)

    def __make_label(self):
        self.label = label(text=self.label_text(False), align='left', height=20,
                           pixel_pos=True, pos=vector(20, self.canvas.height-100, 0))

    def rotate(self, angle=None, axis=None, origin=None):
        ax = axis
        if axis is None:
            ax = self.up
        super(Sphere, self).rotate(angle=angle, axis=ax, origin=origin)

    def delete(self):
        self.visible = False
        self.luminous = False
        self.labelled = False
        self.clear_trail()
        self.__del__()

    @staticmethod
    def __try_vector(vect):
        try:
            return vector(*vect)
        except TypeError:
            return vector(vect)
