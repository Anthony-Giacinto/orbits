from vpython import sphere, simple_sphere, vector, color, textures
from orbits_GUI.astro.params import gravity


class Sphere(simple_sphere, sphere):
    """ Inherits sphere and simple_sphere from VPython with an option to choose between them. """

    def __init__(self, vel=(0.0, 0.0, 0.0), mass=1.0, rotation_speed=0.0, simple=False, name='Sphere', primary=None,
                 shininess=0, up=vector(0, 1, 0), massive=True, _units='km', **kwargs):
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
        self._units = _units
        self.grav_parameter = self.mass*gravity(self._units)
        self._velocity = self.vel = self.__try_vector(vel)
        if 'pos' in kwargs.keys():
            self._position = kwargs['pos'] = self.__try_vector(kwargs['pos'])
        #  If primary is another Sphere, updates pos and vel to be with respect to the origin of the reference frame.
        if isinstance(self.primary, Sphere):
            kwargs['pos'] = self._position + self.primary.pos
            self.vel = self._velocity + self.primary.vel
        for col in ['color', 'trail_color']:
            if col in kwargs.keys():
                if isinstance(kwargs[col], str):
                    kwargs[col] = getattr(color, kwargs[col])
                else:
                    kwargs[col] = self.__try_vector(kwargs[col])
        if 'texture' in kwargs.keys() and isinstance(kwargs['texture'], str):
            try:
                kwargs['texture'] = getattr(textures, kwargs['texture'])
            except:
                pass

        dictionary = {'shininess': shininess, 'up': up, **kwargs}
        if simple:
            self._type = 'simple_sphere'
            simple_sphere.__init__(self, **dictionary)
        else:
            self._type = 'sphere'
            sphere.__init__(self, **dictionary)

    def __str__(self):
        return self.name

    def rotate(self, angle=None, axis=None, origin=None):
        ax = axis
        if axis is None:
            ax = self.up
        super(Sphere, self).rotate(angle=angle, axis=ax, origin=origin)

    @staticmethod
    def __try_vector(vect):
        try:
            return vector(*vect)
        except TypeError:
            return vector(vect)
