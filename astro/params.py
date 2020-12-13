"""
Contains important constants and parameters of some celestial bodies such as radius, mass, gravitational parameter, etc.
Parameters are taken from Wikipedia.

Units for the celestial bodies:
    distance: km
    mass: kg
    time: s
    angle: radians

Functions:
    gravity: The gravitational constant (default units: km**3*kg**-1*s**-2).
    convert_to_seconds: Converts time units to seconds.
    convert_to_km: Converts distance units to kilometers.

Classes:
    Textures: Contains celestial body textures.
    Sun
    Mercury
    Venus
    Earth
    Moon
    Mars
    Jupiter
    Saturn
    Uranus
    Neptune
"""


import math
from astropy.constants import G


_earth_year = 365.256363004  # (days)


def gravity(units='km'):
    """ The gravitational constant (default units: km**3*kg**-1*s**-2).

    :param units: (str) 'km', 'm', or 'natural' units (default is 'km').
    :return: (float) The gravitational constant in the desired units.
    """

    vals = {'km': G.value*1e-9, 'm': G.value, 'natural': 1.0}
    if units not in vals.keys():
        raise ValueError("distance_unit must be either 'km', 'm', or 'natural'")
    else:
        return vals[units]


def convert_to_seconds(val, unit):
    """ Converts time units to seconds. """

    units = {'hours': 3600, 'days': 86400, 'years': _earth_year*86400}
    return val*units[unit]


def convert_to_km(val, unit):
    """ Converts distance units to kilometers. """

    units = {'AU': 149598073}
    return val*units[unit]


class Textures:
    """ Contains celestial body textures. """

    sun = 'images/sun_2.jpg'
    mercury = 'images/2k_mercury.jpg'
    mercury_8k = 'images/8k_mercury.jpg'
    venus = 'images/2k_venus_atmosphere.jpg'
    venus_4k = 'images/4k_venus_atmosphere.jpg'
    venus_surf = 'images/2k_venus_surface.jpg'
    venus_surf_8k = 'images/8k_venus_surface.jpg'
    earth = 'earth_texture.jpg'
    earth_8k = 'images/8k_earth_daymap.jpg'
    moon = 'images/2k_moon.jpg'
    moon_8k = 'images/8k_moon.jpg'
    mars = 'images/2k_mars.jpg'
    mars_8k = 'images/8k_mars.jpg'
    jupiter = 'images/2k_jupiter.jpg'
    jupiter_8k = 'images/8k_jupiter.jpg'
    saturn = 'images/2k_saturn.jpg'
    saturn_8k = 'images/8k_saturn.jpg'
    uranus = 'images/2k_uranus.jpg'
    neptune = 'images/2k_neptune.jpg'
    ceres = 'images/4k_ceres_fictional.jpg'
    eris = 'images/4k_eris_fictional.jpg'
    haumea = 'images/4k_haumea_fictional.jpg'
    makemake = 'images/4k_makemake_fictional.jpg'


class Sun:
    """ Some sun parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Sun

    Class Variables:
        radius: (float) The equatorial radius of the sun.
        mass: (float) The mass of the sun.
        angular_rotation: (float) The angular speed of the sun about its axis.
        gravitational_parameter: (float) The gravitational parameter of the sun.
        same: (str) The lowercase of 'Sun'.
        texture: (str) The sun texture.
    """

    radius = 695700
    mass = 1.9891e30
    sidereal_rotation_period = convert_to_seconds(27.47, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 1.32712440018e11
    name = 'sun'
    texture = Textures.sun

    def __str__(self):
        return 'Sun'


class Mercury:
    """ Some mercury parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Mercury_(planet)

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of mercury.
        mass: (float) The mass of mercury.
        orbital_period: (float) The orbital period of mercury.
        sidereal_rotation_period: (float) The sidereal rotation period of mercury.
        angular_rotation: (float) The angular speed of mercury about its axis.
        gravitational_parameter: (float) The gravitational parameter of mercury.
        semi_major_axis: (float) The semi-major axis of mercury's orbit.
        eccentricity: (float) The eccentricity of mercury's orbit.
        semi_latus_rectum: (float) The semilatus rectum of mercury's orbit.
        inclination: (float) The inclination of mercury's orbit.
        name: (str) The lowercase of 'Mercury'.
        texture: (str) The mercury texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of mercury with respect to its orbital plane.
    """

    radius = 2439.7
    mass = 3.3011e23
    orbital_period = convert_to_seconds(87.9691, 'days')
    sidereal_rotation_period = convert_to_seconds(58.646, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 2.2032e4
    semi_major_axis = 57909050
    eccentricity = 0.205630
    semi_latus_rectum = semi_major_axis*(1 - eccentricity**2)
    inclination = math.radians(7.005)
    name = 'mercury'
    texture = Textures.mercury
    texture_8k = Textures.mercury_8k
    obliquity = math.radians(0.034)

    def __str__(self):
        return 'Mercury'


class Venus:
    """ Some venus parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Venus

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of venus.
        mass: (float) The mass of venus.
        orbital_period: (float) The orbital period of venus.
        sidereal_rotation_period: (float) The sidereal rotation period of venus.
        angular_rotation: (float) The angular speed of venus about its axis.
        gravitational_parameter: (float) The gravitational parameter of venus.
        semi_major_axis: (float) The semi-major axis of venus's orbit.
        eccentricity: (float) The eccentricity of venus's orbit.
        semi_latus_rectum: (float) The semilatus rectum of venus's orbit.
        inclination: (float) The inclination of venus's orbit.
        name: (str) The lowercase of 'Venus'.
        texture: (str) The venus texture.
        texture_4k: (str) A 4k version of texture.
        texture_surf: (str) The venus surface texture.
        texture_surf_8k: (str) An 8k version of texture_surf.
        obliquity: (float) The obliquity of venus with respect to its orbital plane.
    """

    radius = 6051.8
    mass = 4.8675e24
    orbital_period = convert_to_seconds(224.701, 'days')
    sidereal_rotation_period = convert_to_seconds(-243.025, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 3.24859e5
    semi_major_axis = 108208000
    eccentricity = 0.006772
    semi_latus_rectum = semi_major_axis*(1 - eccentricity**2)
    inclination = math.radians(3.39458)
    name = 'venus'
    texture = Textures.venus
    texture_4k = Textures.venus_4k
    texture_surface = Textures.venus_surf
    texture_surface_8k = Textures.venus_surf_8k
    obliqutiy = math.radians(177.36)

    def __str__(self):
        return 'Venus'


class Earth:
    """ Some earth parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Earth

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of earth.
        polar_radius: (float) The polar radius of earth.
        equatorial_radius: (float) The equatorial radius of earth.
        mass: (float) The mass of earth.
        orbital_period: (float) The orbital period of earth.
        sidereal_rotation_period: (float) The sidereal rotation period of earth.
        angular_rotation: (float) The angular speed of earth about its axis.
        gravitational_parameter: (float) The gravitational parameter of earth.
        semi_major_axis: (float) The semi-major axis of earth's orbit.
        eccentricity: (float) The eccentricity of earth's orbit.
        semi_latus_rectum: (float) The semilatus rectum of earth's orbit.
        inclination: (float) The inclination of earth's orbit.
        ellipsoid_eccentricity: (float) The eccentricity of the equatorial cross section of an ellipsoidal Earth model.
        name: (str) The lowercase of 'Earth'.
        texture: (str) The earth texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of earth with respect to its orbital plane.
    """

    radius = 6371
    polar_radius = 6356.8
    equatorial_radius = 6378.1
    mass = 5.97237e24
    orbital_period = convert_to_seconds(_earth_year, 'days')
    sidereal_rotation_period = convert_to_seconds(0.99726968, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 3.986004418e5
    semi_major_axis = 149598023
    eccentricity = 0.0167086
    semi_latus_rectum = semi_major_axis*(1 - eccentricity**2)
    inclination = math.radians(5e-5)
    ellipsoid_eccentricity = 0.08182
    name = 'earth'
    texture = Textures.earth
    texture_8k = Textures.earth_8k
    obliquity = math.radians(23.4392811)

    def __str__(self):
        return 'Earth'


class Moon:
    """ Some moon parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Moon

    Notes:
        All orbital elements and obliquity are in relation to orbit around Earth.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of the moon.
        polar_radius: (float) The polar radius of the moon.
        equatorial_radius: (float) The equatorial radius of the moon.
        mass: (float) The mass of the moon.
        orbital_period: (float) The orbital period of the moon.
        sidereal_rotation_period: (float) The sidereal rotation period of the moon.
        angular_rotation: (float) The angular speed of the moon about its axis.
        gravitational_parameter: (float) The gravitational parameter of the moon.
        semi_major_axis: (float) The semi-major axis of the moon's orbit.
        eccentricity: (float) The eccentricity of the moon's orbit.
        semi_latus_rectum: (float) The semilatus rectum of the moon's orbit.
        inclination: (float) The inclination of the moon's orbit.
        name: (str) The lowercase of 'Moon'.
        texture: (str) The moon texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of the moon with respect to its orbital plane.
    """

    radius = 1737.4
    polar_radius = 1736.0
    equatorial_radius = 1738.1
    mass = 7.342e22
    orbital_period = convert_to_seconds(27.321661, 'days')
    sidereal_rotation_period = orbital_period
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 4.9048695e3
    semi_major_axis = 384399
    eccentricity = 5.49e-2
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(5.145)
    name = 'moon'
    texture = Textures.moon
    texture_8k = Textures.moon_8k
    obliquity = math.radians(6.687)

    def __str__(self):
        return 'Moon'


class Mars:
    """ Some mars parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Mars

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of mars.
        polar_radius: (float) The polar radius of mars.
        equatorial_radius: (float) The equatorial radius of mars.
        mass: (float) The mass of mars.
        orbital_period: (float) The orbital period of mars.
        sidereal_rotation_period: (float) The sidereal rotation period of mars.
        angular_rotation: (float) The angular speed of mars about its axis.
        gravitational_parameter: (float) The gravitational parameter of mars.
        semi_major_axis: (float) The semi-major axis of mars's orbit.
        eccentricity: (float) The eccentricity of mars's orbit.
        semi_latus_rectum: (float) The semilatus rectum of mars's orbit.
        inclination: (float) The inclination of mars's orbit.
        name: (str) The lowercase of 'Mars'.
        texture: (str) The mars texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of mars with respect to its orbital plane.
    """

    radius = 3389.5
    polar_radius = 3376.2
    equatorial_radius = 3396.2
    mass = 6.4171e23
    orbital_period = convert_to_seconds(686.971, 'days')
    sidereal_rotation_period = convert_to_seconds(1.025957, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 4.282837e4
    semi_major_axis = 227939200
    eccentricity = 0.0934
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(1.850)
    name = 'mars'
    texture = Textures.mars
    texture_8k = Textures.mars_8k
    obliquity = math.radians(25.19)

    def __str__(self):
        return 'Mars'


class Jupiter:
    """ Some jupiter parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Jupiter

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of jupiter.
        polar_radius: (float) The polar radius of jupiter.
        equatorial_radius: (float) The equatorial radius of jupiter.
        mass: (float) The mass of jupiter.
        orbital_period: (float) The orbital period of jupiter.
        sidereal_rotation_period: (float) The sidereal rotation period of jupiter.
        angular_rotation: (float) The angular speed of jupiter about its axis.
        gravitational_parameter: (float) The gravitational parameter of jupiter.
        semi_major_axis: (float) The semi-major axis of jupiter's orbit.
        eccentricity: (float) The eccentricity of jupiter's orbit.
        semi_latus_rectum: (float) The semilatus rectum of jupiter's orbit.
        inclination: (float) The inclination of jupiter's orbit.
        name: (str) The lowercase of 'Jupiter'.
        texture: (str) The jupiter texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of jupiter with respect to its orbital plane.
    """

    radius = 66911
    polar_radius = 66854
    equatorial_radius = 71492
    mass = 1.8982e27
    orbital_period = convert_to_seconds(11.862, 'years')
    sidereal_rotation_period = convert_to_seconds(9.925, 'hours')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 1.26686534e8
    semi_major_axis = 778.57e6
    eccentricity = 0.0489
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(1.303)
    name = 'jupiter'
    texture = Textures.jupiter
    texture_8k = Textures.jupiter_8k
    obliquity = math.radians(3.13)

    def __str__(self):
        return 'Jupiter'


class Saturn:
    """ Some saturn parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Saturn

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of saturn.
        polar_radius: (float) The polar radius of saturn.
        equatorial_radius: (float) The equatorial radius of saturn.
        mass: (float) The mass of saturn.
        orbital_period: (float) The orbital period of saturn.
        sidereal_rotation_period: (float) The sidereal rotation period of saturn.
        angular_rotation: (float) The angular speed of saturn about its axis.
        gravitational_parameter: (float) The gravitational parameter of saturn.
        semi_major_axis: (float) The semi-major axis of saturn's orbit.
        eccentricity: (float) The eccentricity of saturn's orbit.
        semi_latus_rectum: (float) The semilatus rectum of saturn's orbit.
        inclination: (float) The inclination of saturn's orbit.
        name: (str) The lowercase of 'Saturn'.
        texture: (str) The saturn texture.
        texture_8k: (str) An 8k version of texture.
        obliquity: (float) The obliquity of saturn with respect to its orbital plane.
    """

    radius = 58232
    polar_radius = 54364
    equatorial_radius = 60268
    mass = 5.6834e26
    orbital_period = convert_to_seconds(29.4571, 'years')
    sidereal_rotation_period = convert_to_seconds(10+(33/60)+(38/3600), 'hours')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 3.7931187e7
    semi_major_axis = 1433.53e6
    eccentricity = 0.0565
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(2.485)
    name = 'saturn'
    texture = Textures.saturn
    texture_8k = Textures.saturn_8k
    obliquity = math.radians(26.73)

    def __str__(self):
        return 'Saturn'


class Uranus:
    """ Some uranus parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Uranus

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of uranus.
        polar_radius: (float) The polar radius of uranus.
        equatorial_radius: (float) The equatorial radius of uranus.
        mass: (float) The mass of uranus.
        orbital_period: (float) The orbital period of uranus.
        sidereal_rotation_period: (float) The sidereal rotation period of uranus.
        angular_rotation: (float) The angular speed of uranus about its axis.
        gravitational_parameter: (float) The gravitational parameter of uranus.
        semi_major_axis: (float) The semi-major axis of uranus's orbit.
        eccentricity: (float) The eccentricity of uranus's orbit.
        semi_latus_rectum: (float) The semilatus rectum of uranus's orbit.
        inclination: (float) The inclination of uranus's orbit.
        name: (str) The lowercase of 'Uranus'.
        texture: (str) The uranus texture.
        obliquity: (float) The obliquity of uranus with respect to its orbital plane.
    """

    radius = 25362
    polar_radius = 24973
    equatorial_radius = 25559
    mass = 8.6810e25
    orbital_period = convert_to_seconds(84.0205, 'years')
    sidereal_rotation_period = convert_to_seconds(-0.71833, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 5.793939e6
    semi_major_axis = convert_to_km(19.2184, 'AU')
    eccentricity = 0.046381
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(0.773)
    name = 'uranus'
    texture = Textures.uranus
    obliquity = math.radians(97.77)

    def __str__(self):
        return 'Uranus'


class Neptune:
    """ Some neptune parameters taken from Wikipedia.
    https://en.wikipedia.org/wiki/Neptune

    Notes:
        All orbital elements and obliquity are in relation to orbit around the Sun.
        Inclination is in relation to the ecliptic, however.

    Class Variables:
        radius: (float) The mean radius of neptune.
        polar_radius: (float) The polar radius of neptune.
        equatorial_radius: (float) The equatorial radius of neptune.
        mass: (float) The mass of neptune.
        orbital_period: (float) The orbital period of neptune.
        sidereal_rotation_period: (float) The sidereal rotation period of neptune.
        angular_rotation: (float) The angular speed of neptune about its axis.
        gravitational_parameter: (float) The gravitational parameter of neptune.
        semi_major_axis: (float) The semi-major axis of neptune's orbit.
        eccentricity: (float) The eccentricity of neptune's orbit.
        semi_latus_rectum: (float) The semilatus rectum of neptune's orbit.
        inclination: (float) The inclination of neptune's orbit.
        name: (str) The lowercase of 'Neptune'.
        texture: (str) The neptune texture.
        obliquity: (float) The obliquity of neptune with respect to its orbital plane.
    """

    radius = 24622
    polar_radius = 24341
    equatorial_radius = 24764
    mass = 1.02413e26
    orbital_period = convert_to_seconds(164.8, 'years')
    sidereal_rotation_period = convert_to_seconds(0.6713, 'days')
    angular_rotation = 2*math.pi/sidereal_rotation_period
    gravitational_parameter = 6.836529e6
    semi_major_axis = convert_to_km(30.07, 'AU')
    eccentricity = 0.008678
    semi_latus_rectum = semi_major_axis*(1-eccentricity**2)
    inclination = math.radians(1.767975)
    name = 'neptune'
    texture = Textures.neptune
    obliquity = math.radians(28.32)
    
    def __str__(self):
        return 'Neptune'
