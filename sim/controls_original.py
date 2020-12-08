"""
The user controls during simulations.

Classes:
    Controls: Custom controls for interacting with VPython objects.
 """


import datetime
from vpython import button, winput, wtext, menu, keysdown, vector, textures, label
from orbits_GUI.sim.sphere import Sphere
from orbits_GUI.astro.params import Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune, gravity
from orbits_GUI.astro.vectors import Elements
import orbits_GUI.scenarios.presets as presets


class AttributeManager:
    attr_dict = {'running': True, 'scenario_running': False, 'previous_sphere': None, 'labelled_sphere': None,
                 'loading_message': None, 'spheres': [], 'dt': 1.0, 'frame_rate': 1080, 'start_time': 'now',
                 '_year': None, '_month': None, '_day': None, '_hour': None, '_minute': None, '_second': None,


                 'initial_radius': None, 'final_radius': None, 'maneuver_start_time': None, 'current_block': None,


                 'pause': None, 'follow_input': None, 'run_scenario': None, 'scenario_menu': None, 'body_menu': None,
                 'vector_menu': None, 'position_x_input': None, 'position_y_input': None, 'position_z_input': None,
                 'velocity_x_input': None, 'velocity_y_input': None, 'velocity_z_input': None,
                 'semi_latus_rectum_input': None, 'eccentricity_input': None, 'inclination_input': None,
                 'loan_input': None, 'periapsis_angle_input': None, 'epoch_angle_input': None, 'mass_input': None,
                 'radius_input': None, 'rotation_input': None, 'name_input': None, 'primary_input': None,
                 'start_time_menu': None, 'year_input': None, 'month_input': None, 'day_input': None,
                 'hour_input': None, 'minute_input': None, 'second_input': None, 'set_time': None, 'reset': None}

    sphere_value_dict = {'position': [0.0, 0.0, 0.0], 'velocity': [0.0, 0.0, 0.0], 'mass': 10.0, 'radius': 100.0,
                         'rotation': 0.0, 'semi_latus_rectum': 0.0, 'eccentricity': 0.0, 'inclination': 0.0,
                         'loan': 0.0, 'periapsis_angle': 0.0, 'epoch_angle': 0.0, 'primary': None, 'name': '',
                         'texture': None}

    attr_dict.update(sphere_value_dict)

    def __init__(self):
        self.default_values()

    def default_values(self):
        for key, value in self.attr_dict.items():
            setattr(self, key, value)


class LocationManager:
    """ Contains information on the location of widgets. """

    # (title/caption, row, column)

    # Might be easier and better if i use ordered lists for each 'row' instead of dictionaries

    # Title Row:
    title_row = {'run_scenario_button': 'run_scenario', 'pause_button': 'pause', 'reset_button': 'reset',
                 'camera_follow_winput': ('follow_text', 'follow_input') , 'dt_winput': ('dt_text', 'dt_input'),
                 'frame_rate_winput': ('frame_rate_text', 'frame_rate_input')}

    # Caption Rows:
    caption_row = {'scenario_menu_dropdown': 'scenario_menu', 'start_time_menu_dropdown': 'start_time_menu',
                   'body_menu_dropdown': 'body_menu'}

    caption_2_widgets = {'vector_menu_dropdown': 'vector_menu', 'maneuver_menu_dropdown': 'maneuver_menu'}

    # Caption Blocks:
    starting_time_block = {'starting_time)block': [['date_winputs'],
                                                   ['time_winputs'],
                                                   ['set_time_button']]}

    vectors_block = {'vectors_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                       ['position_winput', 'rotation_winput'],
                                       ['velocity_winput', 'name_winput'],
                                       ['mass_winput', 'primary_winput'],
                                       ['radius_winput'],
                                       ['create_body_button']]}

    elements_block = {'elements_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                         ['semi_latus_rectum_winput', 'periapsis_angle_winput', 'rotation_winput'],
                                         ['eccentricity_winput', 'epoch_angle_winput', 'name_winput'],
                                         ['inclination_winput', 'mass_winput', 'primary_winput'],
                                         ['loan_winput', 'radius_winput'],
                                         ['create_body_button']]}

    doppler_radar_widgets = []
    radar_widgets = []

    elements_hohmann_block = {'elements_hohmann_block': [['maneuver_initial_radius_winput', 'maneuver_final_radius_winput', 'date_winputs', 'time_winputs'],
                                                         ['semi_latus_rectum_winput', 'periapsis_angle_winput', 'rotation_winput'],
                                                         ['eccentricity_winput', 'epoch_angle_winput', 'name_winput'],
                                                         ['inclination_winput', 'mass_winput', 'primary_winput'],
                                                         ['loan_winput', 'radius_winput'],
                                                         ['create_body_button']]}
    elements_bielliptic_widgets = []
    elements_general_widgets = []
    elements_planechange_widgets = []


class Controls(AttributeManager, LocationManager):
    """ Custom controls for interacting with VPython objects.

    Pause/Run: Hit the Pause/Run button on the screen or press the Shift key.
    Delete Object: Left Mouse Click while holding either delete or backspace.
    Change camera: Enter the index of the desired sphere into text box and hit enter.
    """

    gravity = gravity(units='km')
    preset_bodies = [Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune]
    preset_bodies_dict = {str(body()): body for body in preset_bodies}
    preset_maneuvers = ['Hohmann Transfer', 'Bi-Elliptic Transfer', 'General Transfer', 'Simple Plane Change']


    def __init__(self, scene):
        """
        :param scene: The desired VPython canvas.
        """

        self.scene = scene
        super().__init__()




    def create_title_row(self):
        self.scene.title = ''
        for func in self.title_row:
            getattr(self, func)()

    def create_caption_row(self):
        self.scene.caption = ''
        for func in self.caption_row:
            getattr(self, func)()
        self.scene.append_to_caption('\n\n')

    def create_caption_block(self, block):
        self.current_block = next(iter(block))
        block_values = list(*list(block.values()))
        for row in block_values:
            for func in range(len(row)+1):
                if func != len(row):
                    getattr(self, row[func])()
                else:
                    self.scene.append_to_caption('\n')

    def create_caption(self, block):
        self.create_caption_row()
        self.create_caption_block(block)

    def widget_startup(self):
        self.create_title_row()
        self.create_caption_row()
        self.body_menu.disabled = True
        # self.scene.append_to_caption('\n' + '\u250c' + '\u2500'*10 + '\u2510\n' + '\u2502')

    def sphere_value_reset(self):
        for key, value in self.sphere_value_dict.items():
            setattr(self, key, value)




    def pause_button_func(self, b):
        if self.scenario_running:
            self.running = not self.running
            if self.running:
                b.text = '<b>Pause</b>'
            else:
                b.text = '<b>Run</b>'

    def pause_button(self):
        self.pause = button(text='<b>Pause</b>', pos=self.scene.title_anchor, bind=self.pause_button_func,
                            background=vector(0.7, 0.7, 0.7))

    def reset_button_func(self, b):
        if self.scenario_running:
            self.run_scenario_button_func(self.run_scenario)
        else:
            if self.spheres:
                for sph in self.spheres:
                    sph.delete()
            self.default_values()
            self.scene.caption = ''
            self.scenario_menu_dropdown()

    def reset_button(self):
        self.reset = button(text='<b>Reset</b>', pos=self.scene.title_anchor, bind=self.reset_button_func,
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

    def set_zoom(self, obj_radius, radii_num):
        self.scene.autoscale = False
        self.scene.range = obj_radius + radii_num*obj_radius
        self.scene.autoscale = True




    def scenario_menu_func(self, m):

        def preset(func, zoom=False, **kwargs):
            m.selected = 'Choose Scenario...'
            m.disabled = True
            self.loading(True)
            self.spheres = func(**kwargs)
            self.primary = self.spheres[0]
            if zoom:
                self.set_zoom(self.primary.radius, 5)
            self.loading(False)
            self.body_menu.disabled = False

        if m.selected == 'Choose Scenario...':
            pass

        if m.selected == 'Create Scenario':
            self.body_menu.disabled = False

        elif m.selected == 'Earth Satellites':
            preset(presets.satellites, zoom=True, rows=2600)

        elif m.selected == 'Earth Satellites Perturbed':
            preset(presets.satellites_perturbed, zoom=True, rows=2600, body_semi_latus_rectum=30000,
                   body_eccentricity=0.4)

        elif m.selected == self.preset_maneuvers[0]:
            preset(presets.hohmann, start_time=datetime.datetime.now()+ datetime.timedelta(seconds=5000),
                   inclination=30)

        elif m.selected == self.preset_maneuvers[1]:
            preset(presets.bi_elliptic, start_time=datetime.datetime.now()+ datetime.timedelta(seconds=5000),
                   inclination=75)

        elif m.selected == self.preset_maneuvers[2]:
            preset(presets.general, start_time=datetime.datetime.now()+ datetime.timedelta(seconds=5000),
                   inclination=120)

        elif m.selected == self.preset_maneuvers[3]:
            preset(presets.plane_change, start_time=datetime.datetime.now()+ datetime.timedelta(seconds=5000))

    def scenario_menu_dropdown(self):
        c = ['Choose Scenario...', 'Create Scenario', 'Earth Satellites', 'Earth Satellites Perturbed',
             *self.preset_maneuvers]
        self.scenario_menu = menu(choices=c, bind=self.scenario_menu_func)




    def start_time_menu_func(self, m):
        if m.selected == 'Starting Time...':
            pass

        elif m.selected == 'Present Time':
            self.start_time = 'now'

        elif m.selected == 'Custom Time':
            self.create_caption_block(self.starting_time_block)

    def start_time_menu_dropdown(self):
        c = ['Starting Time...', 'Present Time', 'Custom Time']
        self.start_time_menu = menu(choices=c, bind=self.start_time_menu_func)

    def start_time_winput_func(self, w):
        if isinstance(w.number, int):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def date_winputs(self):
        self.date_text = wtext(text='Date: \u200a')
        self.year_input = winput(text='Year', bind=self.start_time_winput_func, attr='_year')
        self.scene.append_to_caption(' - \u200a')
        self.month_input = winput(text='Month', bind=self.start_time_winput_func, attr='_month')
        self.scene.append_to_caption(' - ')
        self.day_input = winput(text='Day', bind=self.start_time_winput_func, attr='_day')

    def time_winputs(self):
        self.time_text = wtext(text='Time: ')
        self.hour_input = winput(text='Hour', bind=self.start_time_winput_func, attr='_hour')
        self.scene.append_to_caption(' : ')
        self.minute_input = winput(text='Minute', bind=self.start_time_winput_func, attr='_minute')
        self.scene.append_to_caption(' : \u200a')
        self.second_input = winput(text='Second', bind=self.start_time_winput_func, attr='_second')

    def set_time_button_func(self):
        if self._year and self._month and self._day and self._hour and self._minute and self._second:
            self.start_time = datetime.datetime(year=self._year, month=self._month, day=self._day, hour=self._hour,
                                                minute=self._minute, second=self._second)
            self._year = self._month = self._day = self._hour = self._minute = self._second = None

            self.create_caption_row()
            self.body_menu.disabled = True

    def set_time_button(self):
        self.scene.append_to_caption('\n')
        self.set_time = button(text='<b>Set Time</b>', bind=self.set_time_button_func, background=vector(0.7, 0.7, 0.7))




    def body_menu_func(self, m):
        if self.spheres:
            if m.selected == 'Choose Body...':
                pass
            elif m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption(self.vectors_block)
                self.maneuver_menu.disabled = True
            else:
                self.sphere_value_reset()
                preset = self.preset_bodies_dict[m.selected]
                self.mass = preset.mass
                self.radius = preset.radius
                self.rotation = preset.angular_rotation
                self.name = str(preset())
                self.texture = preset.texture
                self.create_caption(self.vectors_block)
        else:
            if m.selected == 'Choose Body...':
                pass
            if m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption_block(self.vectors_block)
                self.maneuver_menu.disabled = True
            else:
                preset = self.preset_bodies_dict[m.selected]
                self.mass = preset.mass
                self.radius = preset.radius
                self.rotation = preset.angular_rotation
                self.name = str(preset())
                self.texture = preset.texture
                self.create_caption_block(self.vectors_block)
                self.vector_menu.disabled = self.maneuver_menu.disabled = self.create_body.disabled = True
                self.previous_sphere = self.primary = Sphere(pos=(0, 0, 0), vel=(0, 0, 0), preset=preset)
                self.spheres.append(self.primary)
                if m.selected is 'Sun':
                    self.scene.lights[0].visible = False
                    self.spheres[0].luminous = True
                self.scene.camera.follow(self.spheres[0])
                m.selected = 'Choose Body...'

    def body_menu_dropdown(self):
        c = ['Choose Body...', 'Custom', *list(self.preset_bodies_dict.keys())]
        self.body_menu = menu(choices=c, bind=self.body_menu_func)




    def run_scenario_button_func(self, b):
        if self.spheres and not self.loading_message:
            self.scenario_running = not self.scenario_running
            if self.scenario_running:
                b.text = '<b>End Scenario</b>'
            else:
                b.text = '<b>Run Scenario</b>'
                for sph in self.spheres:
                    sph.delete()
                self.spheres = []
                self.create_caption_row()

    def run_scenario_button(self):
        self.run_scenario = button(text='<b>Run Scenario</b>', bind=self.run_scenario_button_func,
                                   background=vector(0.7, 0.7, 0.7), pos=self.scene.title_anchor)




    def vector_menu_func(self, m):
        if m.selected == 'Vectors':
            self.sphere_value_reset()
            self.create_caption(self.vectors_block)
            self.maneuver_menu.disabled = True

        elif m.selected == 'Elements':
            self.sphere_value_reset()
            self.maneuver_menu.disabled = False
            self.create_caption(self.elements_block)
            self.vector_menu.selected = m.selected

        elif m.selected == 'Doppler Radar':
            pass

        else:
            pass

    def vector_menu_dropdown(self):
        c = ['Vectors', 'Elements', 'Doppler Radar', 'Radar']
        self.vector_menu = menu(choices=c, bind=self.vector_menu_func)




    def maneuver_menu_func(self, m):
        if m.selected == 'No Maneuver':
            pass

        elif m.selected == 'Hohmann Transfer':
            self.create_caption(self.elements_hohmann_block)

        elif m.selected == 'Bi-Elliptic Transfer':
            self.maneuver_bielliptic_winput()

        elif m.selected == 'General Transfer':
            self.maneuver_general_winput()

        elif m.selected == 'Simple Plane Change':
            self.maneuver_plane_change_winput()

    def maneuver_menu_dropdown(self):
        c = ['No Maneuver', *self.preset_maneuvers]
        self.maneuver_menu = menu(choices=c, bind=self.maneuver_menu_func)

    def maneuver_start_time_func(self):
        # put this into create body button instead
        self.maneuver_start_time = datetime.datetime(year=self._year, month=self._month, day=self._day,
                                                     hour=self._hour, minute=self._minute, second=self._second)
        self._year = self._month = self._day = self._hour = self._minute = self._second = None

    def maneuver_initial_radius_winput(self):
        self.maneuver_inital_radius_text = wtext(text='Initial Radius: ')
        self.maneuver_initial_radius_input = winput(text='', bind=self.template_winput_func, attr='initial_radius')

    def maneuver_final_radius_winput(self):
        self.maneuver_final_radius_text = wtext(text='Final Radius: ')
        self.maneuver_final_radius_input = winput(text='', bind=self.template_winput_func, attr='final_radius')

    # def maneuver_bielliptic_winput(self):
    #     self.maneuver_radii_winput()
    #     self.maneuver_apoapsis_text = wtext(text='Apoapsis: ')
    #     self.maneuver_apoapsis_input = winput(text='', bind=self.template_winput_func)
    #     self.scene.append_to_caption('\n')
    #     self.start_time_winputs(spaces=False)
    #
    # def maneuver_general_winput(self):
    #     self.maneuver_radii_winput()
    #     self.maneuver_eccentricity_text = wtext(text='Eccentricity: ')
    #     self.maneuver_eccentricitys_input = winput(text='', bind=self.template_winput_func)
    #     self.scene.append_to_caption('\n')
    #     self.start_time_winputs(spaces=False)
    #
    # def maneuver_plane_change_winput(self):
    #     self.maneuver_inital_radius_text = wtext(text='Radius: ')
    #     self.maneuver_initial_radius_input = winput(text='', bind=self.template_winput_func)
    #     self.scene.append_to_caption('\n')
    #     self.maneuver_inclination_change_text = wtext(text='Inclination Change: ')
    #     self.maneuver_inclination_change_input = winput(text='', bind=self.template_winput_func)
    #     self.scene.append_to_caption('\n')
    #     self.start_time_winputs(spaces=False)





    def vector_winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr[w.coord], w.number)

    def position_winput(self):
        kwargs = {'bind': self.vector_winput_func, 'attr': 'position'}
        self.position_text = wtext(text='Position (km): ')
        self.scene.append_to_caption(' '*4+'\u200a'*4)
        self.position_x_input = winput(coord=0, text=str(self.position[0]), **kwargs)
        self.position_y_input = winput(coord=1, text=str(self.position[1]), **kwargs)
        self.position_z_input = winput(coord=2, text=str(self.position[2]), **kwargs)

    def velocity_winput(self):
        kwargs = {'bind': self.vector_winput_func, 'attr': 'velocity'}
        self.velocity_text = wtext(text='Velocity (km/s): ')
        self.scene.append_to_caption(' '*2)
        self.velocity_x_input = winput(coord=0, text=str(self.velocity[0]), **kwargs)
        self.velocity_y_input = winput(coord=1, text=str(self.velocity[1]), **kwargs)
        self.velocity_z_input = winput(coord=2, text=str(self.velocity[2]), **kwargs)

    def template_winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def semi_latus_rectum_winput(self):
        self.semi_latus_rectum_text = wtext(text='Semilatus Rectum (km): ')
        self.scene.append_to_caption(' '*2)
        self.semi_latus_rectum_input = winput(bind=self.template_winput_func, text=str(self.semi_latus_rectum),
                                              attr='semi_latus_rectum')

    def eccentricity_winput(self):
        self.eccentricity_text = wtext(text='Eccentricity: ')
        self.scene.append_to_caption(' '*19+'\u200a'*2)
        self.eccentricity_input = winput(bind=self.template_winput_func, text=str(self.eccentricity),
                                         attr='eccentricity')

    def inclination_winput(self):
        self.inclination_text = wtext(text='Inclination (\u00b0): ')
        self.scene.append_to_caption(' '*15+'\u200a'*4)
        self.inclination_input = winput(bind=self.template_winput_func, text=str(self.inclination),
                                        attr='inclination')

    def loan_winput(self):
        self.loan_text = wtext(text='Long. of Asc. Node (\u00b0): ')
        self.scene.append_to_caption(' '*3+'\u200a'*4)
        self.loan_input = winput(bind=self.template_winput_func, text=str(self.loan), attr='loan')

    def periapsis_angle_winput(self):
        self.scene.append_to_caption(' '*5)
        self.periapsis_text = wtext(text='Periapsis Angle (\u00b0): ')
        self.scene.append_to_caption(' '*2)
        self.periapsis_angle_input = winput(bind=self.template_winput_func, text=str(self.periapsis_angle),
                                            attr='periapsis_angle')

    def epoch_angle_winput(self):
        self.scene.append_to_caption(' '*5)
        self.epoch_angle_text = wtext(text='Epoch Angle (\u00b0): ')
        self.scene.append_to_caption(' '*6)
        self.epoch_angle_input = winput(bind=self.template_winput_func, text=str(self.epoch_angle),
                                        attr='epoch_angle')

    def mass_winput(self):
        spacing = {'vectors_block': ('', ' '*9+'\u200a'*4), 'elements_block': (' '*5, ' '*14+'\u200a'*3)}
        spacing['elements_hohmann_block'] = spacing['elements_block']
        self.scene.append_to_caption(spacing[self.current_block][0])
        self.mass_text = wtext(text='Mass (kg): ')
        self.scene.append_to_caption(spacing[self.current_block][1])
        self.mass_input = winput(bind=self.template_winput_func, text=str(self.mass), attr='mass')

    def radius_winput(self):
        spacing = {'vectors_block': ('', ' '*6+'\u200a'*2), 'elements_block': (' '*5, ' '*11+'\u200a')}
        spacing['elements_hohmann_block'] = spacing['elements_block']
        self.scene.append_to_caption(spacing[self.current_block][0])
        self.radius_text = wtext(text='Radius (km): ')
        self.scene.append_to_caption(spacing[self.current_block][1])
        self.radius_input = winput(bind=self.template_winput_func, text=str(self.radius), attr='radius')

    def rotation_winput(self):
        self.scene.append_to_caption(' '*5)
        self.rotation_text = wtext(text='Angular Velocity (rad/s): ')
        self.scene.append_to_caption(' '*2)
        self.rotation_input = winput(bind=self.template_winput_func, text=str(self.rotation), attr='rotation')

    def name_winput_func(self, w):
        if isinstance(w.text, str):
            self.name = w.text.lower()

    def name_winput(self):
        spacing = {'vectors_block': (' '*5, ' '*27+'\u200a'*4), 'elements_block': (' '*5, ' '*27+'\u200a'*5)}
        spacing['elements_hohmann_block'] = spacing['elements_block']
        self.scene.append_to_caption(spacing[self.current_block][0])
        self.name_text = wtext(text='Name: ')
        self.scene.append_to_caption(spacing[self.current_block][1])
        if not self.name:
            self.name = f'Custom {len(self.spheres)}'
        self.name_input = winput(bind=self.name_winput_func, text=self.name, type='string')

    def primary_winput_func(self, w):
        if isinstance(w.text, str):
            for sph in self.spheres:
                if w.text.lower() == sph.name:
                    self.primary = sph

    def primary_winput(self):
        spacing = {'vectors_block': (' '*44+'\u200a'*3, ' '*24+'\u200a'*6), 'elements_block': (' '*5, ' '*24+'\u200a'*6)}
        spacing['elements_hohmann_block'] = spacing['elements_block']
        self.scene.append_to_caption(spacing[self.current_block][0])
        self.primary_text = wtext(text='Primary: ')
        self.scene.append_to_caption(spacing[self.current_block][1])
        if self.primary:
            text = self.primary.name
        else:
            text = str(self.primary)
        self.primary_input = winput(bind=self.primary_winput_func, text=text, type='string')







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
        self.body_menu_reset('Choose Body...')
        self.full_value_reset()

    def create_body_button(self):
        self.scene.append_to_caption('\n')
        self.create_body = button(text='<b>Create Body</b>', bind=self.create_body_func,
                                  background=vector(0.7, 0.7, 0.7))





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
        keys = keysdown()
        obj = self.scene.mouse.pick

        if isinstance(obj, Sphere):
            if 'delete' in keys or 'backspace' in keys:
                if obj.luminous and len(self.scene.lights) == 2:
                    self.scene.lights[0].visible = True
                self.spheres.remove(obj)
                obj.delete()

            else:
                if isinstance(self.labelled_sphere, Sphere):
                    self.labelled_sphere.labelled = False
                self.labelled_sphere = obj
                obj.labelled = True

        else:
            if isinstance(self.labelled_sphere, Sphere):
                self.labelled_sphere.labelled = False
            self.labelled_sphere = None

    def bindings(self):
        self.scene.bind('keyup', self.space_up)
        self.scene.bind('mousedown', self.mouse_down)

    def set_controls(self):
        self.widget_startup()
        self.bindings()
