"""
The user controls during simulations.

Classes:
    Controls: Custom controls for interacting with VPython objects.
 """


from vpython import button, winput, wtext, menu, keysdown, vector, textures, local_light, color, label
from orbits_GUI.sim.sphere import Sphere
from orbits_GUI.astro.params import Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune, gravity
from orbits_GUI.astro.vectors import Elements
import orbits_GUI.scenarios.presets as presets


class Controls:
    """ Custom controls for interacting with VPython objects.

    Pause/Run: Hit the Pause/Run button on the screen or press the Shift key.
    Delete Object: Left Mouse Click while holding either delete or backspace.
    Change camera: Enter the index of the desired sphere into text box and hit enter.
    """

    # Default Values
    gravity = gravity(units='km')
    running = True
    scenario_running = False
    system_primary = None
    previous_sphere = None
    loading_message = None
    spheres, lamps = [], []
    dt = 1.0
    frame_rate = 1080
    position, velocity = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    mass = 10.0
    radius = 100.0
    rotation = 0.0
    semi_latus_rectum = eccentricity = inclination = loan = periapsis_angle = epoch_angle = 0.0
    primary = None
    name = ''

    # Widgets
    pause = follow_input = run_scenario = None
    scenario_menu = system_primary_body_menu = new_body_menu = vector_menu = None
    position_x_input = position_y_input = position_z_input = None
    velocity_x_input = velocity_y_input = velocity_z_input = None
    semi_latus_rectum_input = eccentricity_input = inclination_input = None
    loan_input = periapsis_angle_input = epoch_angle_input = None
    mass_input = radius_input = rotation_input = None
    name_input = primary_input = None

    celestials = [Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune]
    celestial_dict = {str(celest()): celest for celest in celestials}

    def __init__(self, scene):
        """
        :param scene: The desired VPython canvas.
        """

        self.scene = scene

    def pause_button_func(self, b):
        self.running = not self.running
        if self.running:
            b.text = '<b>Pause</b>'
        else:
            b.text = '<b>Run</b>'

    def pause_button(self):
        self.pause = button(text='<b>Pause</b>', pos=self.scene.title_anchor, bind=self.pause_button_func,
                            background=vector(0.7, 0.7, 0.7))

    def camera_follow_func(self, w):
        if isinstance(w.number, int):
            w.text = w.number
            sph = self.spheres[w.number]
            self.scene.camera.follow(sph)
            #self.set_zoom(sph.radius, 0.75)

    def camera_follow_winput(self):
        self.follow_text = wtext(text='   <b>Sphere to Follow: </b>', pos=self.scene.title_anchor)
        self.follow_input = winput(bind=self.camera_follow_func, text='index', pos=self.scene.title_anchor)




    def dt_winput_func(self, w):
        if isinstance(w.number, (int, float)):
            self.dt = w.text = w.number

    def dt_winput(self):
        self.dt_text = wtext(text='   <b>Time Step (s): </b>', pos=self.scene.title_anchor)
        self.dt_input = winput(bind=self.dt_winput_func, text=f'{self.dt}', pos=self.scene.title_anchor)

    def frame_rate_winput_func(self, w):
        if isinstance(w.number, int):
            self.frame_rate = w.text = w.number

    def frame_rate_winput(self):
        self.frame_rate_text = wtext(text='   <b>Frame Rate: </b>', pos=self.scene.title_anchor)
        self.frame_rate_input = winput(bind=self.frame_rate_winput_func, text=f'{self.frame_rate}',
                                       pos=self.scene.title_anchor)

    def loading(self, state):
        if state:
            self.loading_message = label(text='Building Scenario', height=45, font='sans', box=False)
        else:
            self.loading_message.visible = False
            del self.loading_message
            self.loading_message = None

    def menu_reset(self, menu_dropdown, menu_str, selected):
        menu_dropdown()
        getattr(self, menu_str).selected = selected

    def set_zoom(self, obj_radius, radii_num):
        self.scene.autoscale = False
        self.scene.range = obj_radius + radii_num*obj_radius
        self.scene.autoscale = True

    def scenario_menu_func(self, m):
        if m.selected == 'Create Scenario' and not self.system_primary_body_menu:
            self.system_primary_body_menu_dropdown()

        elif m.selected == 'Earth Satellites':
            m.disabled = True
            self.loading(True)
            self.spheres = presets.satellites()
            self.system_primary = self.spheres[0]
            self.loading(False)

        elif m.selected == 'Earth Satellites Fast':
            m.disabled = True
            self.loading(True)
            self.spheres = presets.satellites(rows=2600, simple=True, fast=True)
            self.system_primary = self.spheres[0]
            self.set_zoom(self.system_primary.radius, 5)
            self.loading(False)

        elif m.selected == 'Earth Satellites Perturbed':
            m.disabled = True
            self.loading(True)
            self.spheres = presets.satellites_perturbed(rows=2600, simple=True, fast=True, body_semi_latus_rectum=30000,
                                                        body_eccentricity=0.4)
            self.system_primary = self.spheres[0]
            self.set_zoom(self.system_primary.radius, 5)
            self.loading(False)

    def scenario_menu_dropdown(self):
        c = ['Choose Scenario', 'Create Scenario', 'Earth Satellites', 'Earth Satellites Fast',
             'Earth Satellites Perturbed', 'Other Scenarios']
        self.scenario_menu = menu(choices=c, bind=self.scenario_menu_func)

    def scenario_menu_reset(self, selected):
        self.menu_reset(self.scenario_menu_dropdown, 'scenario_menu', selected)

    def system_primary_body_menu_func(self, m):

        def make_system_primary(m):
            self.scene.lights[0].visible = self.scene.lights[1].visible = True
            self.system_primary = self.celestial_dict[str(m.selected)]
            self.previous_sphere = self.primary = Sphere(pos=(0, 0, 0), vel=(0, 0, 0), mass=self.system_primary.mass,
                                                         radius=self.system_primary.radius, shininess=0,
                                                         rotation_speed=self.system_primary.angular_rotation,
                                                         texture=self.system_primary.texture,
                                                         name=self.system_primary.name)
            self.spheres.append(self.primary)
            if str(m.selected) is 'Sun':
                self.scene.lights[0].visible = self.scene.lights[1].visible = False
                self.spheres[0].emissive = True

                light = local_light(pos=self.spheres[0].pos, color=color.white, index=len(self.spheres)-1)
                self.spheres[0].light = light
                self.lamps.append(light)

        # if spheres has no system primary body, makes one
        if not self.spheres:
            if m.selected == 'Custom' or m.selected == 'Spacecraft':
                pass
            else:
                make_system_primary(m)
                self.scene.camera.follow(self.spheres[0])
                self.new_body_menu_dropdown()
        # if spheres already has a system primary body, replaces it
        else:
            if m.selected == 'Custom' or m.selected == 'Spacecraft':
                pass
            else:
                self.primary = None
                self.spheres[0].visible = False
                del self.spheres[0]
                self.spheres = []
                make_system_primary(m)
                self.scene.camera.follow(self.spheres[0])

    def system_primary_body_menu_dropdown(self):
        c = ['Primary Body', 'Custom', *list(self.celestial_dict.keys()), 'Spacecraft']
        self.system_primary_body_menu = menu(choices=c, bind=self.system_primary_body_menu_func)

    def system_primary_body_menu_reset(self, selected):
        self.menu_reset(self.system_primary_body_menu_dropdown, 'system_primary_body_menu', selected)

    def new_body_menu_func(self, m):
        if m.selected == 'Spacecraft':
            self.full_value_reset()
            self.vector_menu_dropdown()
            self.pos_vel_winput()
            self.mass_rad_rot_winput()
            self.name_winput()
            self.primary_winput()
            self.create_body_button()

    def new_body_menu_dropdown(self):
        c = ['New Body', 'Custom', 'Spacecraft']
        self.new_body_menu = menu(choices=c, bind=self.new_body_menu_func)

    def new_body_menu_reset(self, selected):
        self.menu_reset(self.new_body_menu_dropdown, 'new_body_menu', selected)

    def run_scenario_button_func(self, b):
        if self.spheres and not self.loading_message:
            self.scenario_running = not self.scenario_running
            if self.scenario_running:
                b.text = '<b>End Scenario</b>'
            else:
                try:
                    self.new_body_menu.delete()
                    self.new_body_menu = None
                except:
                    pass
                try:
                    self.system_primary_body_menu.delete()
                    self.system_primary_body_menu = None
                except:
                    pass
                self.scenario_menu.selected = 'Choose Scenario'
                self.spheres = []
                b.text = '<b>Run Scenario</b>'

                for obj in self.scene.objects:
                    obj.visible = False
                    obj.clear_trail()
                    del obj

                # Deletes everything in the scene caption and creates the scenario menu again
                # Avoids having an increasing number of spaces after the scenario menu (must also do this for buttons)
                self.scene.caption = ''
                self.scenario_menu_dropdown()

    def run_scenario_button(self):
        self.run_scenario = button(text='<b>Run Scenario</b>', bind=self.run_scenario_button_func,
                                   background=vector(0.7, 0.7, 0.7), pos=self.scene.title_anchor)

    def vector_menu_func(self, m):

        def f(func):
            self.full_winput_delete()
            self.create_body_button()
            self.scene.caption = ''

            self.scenario_menu_reset('Create Scenario')
            self.system_primary_body_menu_reset(str(self.system_primary()))
            self.new_body_menu_reset('Spacecraft')
            self.vector_menu_reset(m.selected)

            func()
            self.mass_rad_rot_winput()
            self.name_winput()
            self.primary_winput()
            self.create_body_button()

        if m.selected == 'Vectors':
            f(self.pos_vel_winput)

        elif m.selected == 'Elements':
            f(self.elements_winput)

        elif m.selected == 'Doppler Radar':
            pass
        else:
            pass

    def vector_menu_dropdown(self):
        c = ['Vectors', 'Elements', 'Doppler Radar', 'Radar']
        self.vector_menu = menu(choices=c, bind=self.vector_menu_func)
        self.scene.append_to_caption('\n\n')

    def vector_menu_reset(self, selected):
        self.menu_reset(self.vector_menu_dropdown, 'vector_menu', selected)

    def vector_winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            if w.coord is 'x':
                setattr(self, w.attr[0], w.number)
            elif w.coord is 'y':
                setattr(self, w.attr[1], w.number)
            else:
                setattr(self, w.attr[2], w.number)

    def position_winput(self):
        kwargs = {'bind': self.vector_winput_func, 'text': 0.0, 'attr': 'position'}
        self.position_text = wtext(text='Position (km): ')
        self.scene.append_to_caption(' '*15)
        self.position_x_input = winput(coord='x', **kwargs)
        self.position_y_input = winput(coord='y', **kwargs)
        self.position_z_input = winput(coord='z', **kwargs)
        self.scene.append_to_caption('\n')

    def velocity_winput(self):
        kwargs = {'bind': self.vector_winput_func, 'text': 0.0, 'attr': 'velocity'}
        self.velocity_text = wtext(text='Velocity (km/s): ')
        self.scene.append_to_caption(' '*12)
        self.velocity_x_input = winput(coord='x', **kwargs)
        self.velocity_y_input = winput(coord='y', **kwargs)
        self.velocity_z_input = winput(coord='z', **kwargs)
        self.scene.append_to_caption('\n')

    def template_winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def semi_latus_rectum_winput(self):
        self.semi_latus_rectum_text = wtext(text='Semilatus Rectum (km): ')
        self.semi_latus_rectum_input = winput(bind=self.template_winput_func, text=str(self.semi_latus_rectum),
                                              attr='semi_latus_rectum')
        self.scene.append_to_caption('\n')

    def eccentricity_winput(self):
        self.eccentricity_text = wtext(text='Eccentricity: ')
        self.scene.append_to_caption(' '*17)
        self.eccentricity_input = winput(bind=self.template_winput_func, text=str(self.eccentricity),
                                         attr='eccentricity')
        self.scene.append_to_caption('\n')

    def inclination_winput(self):
        self.inclination_text = wtext(text='Inclination (\u00b0): ')
        self.scene.append_to_caption(' '*14)
        self.inclination_input = winput(bind=self.template_winput_func, text=str(self.inclination),
                                        attr='inclination')
        self.scene.append_to_caption('\n')

    def loan_winput(self):
        self.loan_text = wtext(text='Long. of Asc. Node (\u00b0): ')
        self.scene.append_to_caption(' '*2)
        self.loan_input = winput(bind=self.template_winput_func, text=str(self.loan), attr='loan')
        self.scene.append_to_caption('\n')

    def periapsis_angle_winput(self):
        self.periapsis_text = wtext(text='Periapsis Angle (\u00b0): ')
        self.scene.append_to_caption(' '*8)
        self.periapsis_angle_input = winput(bind=self.template_winput_func, text=str(self.periapsis_angle),
                                            attr='periapsis_angle')
        self.scene.append_to_caption('\n')

    def epoch_angle_winput(self):
        self.epoch_angle_text = wtext(text='Epoch Angle (\u00b0): ')
        self.scene.append_to_caption(' '*12)
        self.epoch_angle_input = winput(bind=self.template_winput_func, text=str(self.epoch_angle),
                                        attr='epoch_angle')
        self.scene.append_to_caption('\n')

    def mass_winput(self):
        self.mass_text = wtext(text='Mass (kg): ')
        self.scene.append_to_caption(' '*20)
        self.mass_input = winput(bind=self.template_winput_func, text=str(self.mass), attr='mass')
        self.scene.append_to_caption('\n')

    def radius_winput(self):
        self.radius_text = wtext(text='Radius (km): ')
        self.scene.append_to_caption(' '*17)
        self.radius_input = winput(bind=self.template_winput_func, text=str(self.radius), attr='radius')
        self.scene.append_to_caption('\n')

    def rotation_winput(self):
        self.rotation_text = wtext(text='Angular Velocity (rad/s): ')
        self.rotation_input = winput(bind=self.template_winput_func, text=str(self.rotation), attr='rotation')
        self.scene.append_to_caption('\n')

    def name_winput_func(self, w):
        if isinstance(w.text, str):
            self.name = w.text.lower()

    def name_winput(self):
        self.name_text = wtext(text='Name: ')
        self.scene.append_to_caption(' '*26)
        self.name_input = winput(bind=self.name_winput_func, text=f'Custom {len(self.spheres)}', type='string')
        self.scene.append_to_caption('\n')

    def primary_winput_func(self, w):
        if isinstance(w.text, str):
            for sph in self.spheres:
                if w.text.lower() == sph.name:
                    self.primary = sph

    def primary_winput(self):
        self.primary_text = wtext(text='Primary: ')
        self.scene.append_to_caption(' '*23)
        self.primary_input = winput(bind=self.primary_winput_func, text=str(self.system_primary()), type='string')
        self.scene.append_to_caption('\n\n')

    def create_body_func(self):
        kwargs = {'mass': self.mass, 'radius': self.radius, 'rotation_speed': self.rotation, 'shininess': 0,
                  'texture': textures.rough, 'make_trail': True, 'name': self.name, 'primary': self.primary}

        if self.semi_latus_rectum_input:
            vectors = Elements(self.semi_latus_rectum, self.eccentricity, self.inclination, self.loan,
                               self.periapsis_angle, self.epoch_angle, self.primary.grav_parameter, True)
            self.previous_sphere = Sphere(pos=vectors.position, vel=vectors.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
        else:
            # The given position & velocity winput values are with respect to some chosen primary body,
            # and then those values are converted to be with respect to the system primary body
            self.previous_sphere = Sphere(pos=self.position, vel=self.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)

        self.scene.caption = ''
        self.scenario_menu_reset('Create Scenario')
        self.system_primary_body_menu_reset(str(self.system_primary()))
        self.new_body_menu_reset('New Body')
        self.full_value_reset()

    def create_body_button(self):
        self.create_body = button(text='<b>Create Body</b>', bind=self.create_body_func,
                                  background=vector(0.7, 0.7, 0.7))

    @staticmethod
    def __try_delete(args):
        for arg in args:
            try:
                arg.delete()
            except:
                pass

    def mass_rad_rot_winput(self):
        self.mass_winput()
        self.radius_winput()
        self.rotation_winput()

    def mass_rod_rot_delete(self):
        winputs = [self.mass_input, self.radius_input, self.rotation_input]
        self.__try_delete(winputs)

    def mass_rad_rot_reset(self):
        self.mass = 10.0
        self.radius = 100.0
        self.rotation = 0.0

    def pos_vel_winput(self):
        self.position_winput()
        self.velocity_winput()

    def pos_vel_delete(self):
        winputs = [self.position_x_input, self.position_y_input, self.position_z_input, self.velocity_x_input,
                   self.velocity_y_input, self.velocity_z_input]
        self.__try_delete(winputs)

    def pos_vel_reset(self):
        self.position = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0, 0.0]

    def elements_winput(self):
        self.semi_latus_rectum_winput()
        self.eccentricity_winput()
        self.inclination_winput()
        self.loan_winput()
        self.periapsis_angle_winput()
        self.epoch_angle_winput()

    def elements_delete(self):
        winputs = [self.semi_latus_rectum_input, self.eccentricity_input, self.inclination_input, self.loan_input,
                   self.periapsis_angle_input, self.epoch_angle_input]
        self.__try_delete(winputs)

    def elements_reset(self):
        self.semi_latus_rectum = self.eccentricity = self.inclination = self.loan = self.periapsis_angle = \
            self.epoch_angle = 0.0

    def full_value_reset(self):
        self.mass_rad_rot_reset()
        self.pos_vel_reset()
        self.elements_reset()

    def full_winput_delete(self):
        self.pos_vel_delete()
        self.mass_rod_rot_delete()
        self.elements_delete()




    def show_axes_checkbox_func(self, c):
        return
    def show_axes_checkbox(self):
        return

    def change_date_winput_func(self, w):
        return
    def change_date_winput(self):
        return

    def save_scenario_button_func(self, b):
        return
    def save_scenario_button(self):
        return





    def space_up(self):
        if 'shift' in keysdown():
            self.pause_button_func(self.pause)

    def mouse_down(self):
        key = keysdown()
        sph = self.scene.mouse.pick

        # deletes the selected shape.
        if sph is not None and ('delete' in key or 'backspace' in key):
            sph.clear_trail()
            sph.visible = False
            self.spheres.remove(sph)
            del sph

    def bindings(self):
        self.scene.bind('keyup', self.space_up)
        self.scene.bind('mousedown', self.mouse_down)

    def set_controls(self):
        self.pause_button()
        self.camera_follow_winput()
        self.dt_winput()
        self.frame_rate_winput()
        self.scene.append_to_title('\t'*25 + ' ')
        self.run_scenario_button()
        self.scenario_menu_dropdown()
        self.bindings()
