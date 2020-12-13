"""
The user controls during simulations.

Classes:
    Controls: Custom controls for interacting with VPython objects.
 """


import math
import copy
import datetime
from vpython import button, winput, wtext, menu, keysdown, vector, textures, label, checkbox
from orbits_GUI.sim.sphere import Sphere
from orbits_GUI.astro.params import Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune, gravity
from orbits_GUI.astro.vectors import Elements, DopplerRadar, Radar
import orbits_GUI.scenarios.presets as presets
from orbits_GUI.astro.maneuvers import Hohmann, BiElliptic, GeneralTransfer, SimplePlaneChange


class Winput(winput):
    def __init__(self, **kwargs):
        kwargs['height'] = 23
        super().__init__(**kwargs)

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value):
        raise AttributeError('Cannot change the winput height attribute.')


class AttributeManager:

    canvas_build_height_sub = 490
    canvas_simulate_height_sub = 250

    attr_dict = {'running': True, 'scenario_running': False, 'previous_sphere': None, 'labelled_sphere': None,
                 'loading_message': None, 'spheres': [], 'dt': 1.0, 'frame_rate': 1080, 'start_time': 'now',
                 '_year': None, '_month': None, '_day': None, '_hour': None, '_minute': None, '_second': None,
                 'maneuver_year': None, 'maneuver_month': None, 'maneuver_day': None, 'maneuver_hour': None,
                 'maneuver_minute': None, 'maneuver_second': None, 'scene_height_sub': canvas_build_height_sub,


                 'initial_radius': None, 'final_radius': None, 'transfer_apoapsis': None, 'transfer_eccentricity': None,
                 'inclination_change': None, 'maneuver_start_time': None, 'current_blocks': None,
                 'maneuver': None, 'axes': False,


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
                         'texture': None, 'positions': [0.0, 0.0, 0.0], 'speeds': [0.0, 0.0, 0.0],
                         'locations': [0.0, 0.0, 0.0], 'positions_1': [0.0, 0.0, 0.0], 'positions_2': [0.0, 0.0, 0.0],
                         'positions_3': [0.0, 0.0, 0.0]}

    attr_dict.update(sphere_value_dict)

    def __init__(self):
        self.default_values()

    def default_values(self):
        for key, value in self.attr_dict.items():
            if isinstance(value, list) and hasattr(self, key):
                if key == 'spheres':
                    getattr(self, key).clear()
                else:
                    getattr(self, key)[0] = 0.0
                    getattr(self, key)[1] = 0.0
                    getattr(self, key)[2] = 0.0
            else:
                setattr(self, key, value)


class LocationManager:
    """ Contains information on the location of widgets. """

    # (title/caption, row, column)

    # Title Row:
    title_row = {'run_scenario_button': 'run_scenario', 'pause_button': 'pause', 'reset_button': 'reset',
                 'camera_follow_Winput': ('follow_text', 'follow_input'), 'dt_Winput': ('dt_text', 'dt_input'),
                 'frame_rate_Winput': ('frame_rate_text', 'frame_rate_input')}

    # Caption Rows:
    caption_row = {'scenario_menu_dropdown': 'scenario_menu', 'body_menu_dropdown': 'body_menu',
                   'show_axes_checkbox': 'show_axes'}

    # Caption Blocks:
    starting_time_block = {'starting_time_block': [['start_time_menu_dropdown'],
                                                   ['date_Winputs'],
                                                   ['time_Winputs'],
                                                   ['set_time_button']],
                           'length': 22}

    vectors_block = {'vectors_block': [['vector_menu_dropdown'],
                                       ['position_Winput'],
                                       ['velocity_Winput'],
                                       ['mass_Winput'],
                                       ['radius_Winput'],
                                       ['rotation_Winput'],
                                       ['name_Winput'],
                                       ['primary_Winput'],
                                       ['create_body_button']],
                     'length': 25}

    elements_block = {'elements_block': [['vector_menu_dropdown'],
                                         ['semi_latus_rectum_Winput', 'mass_Winput'],
                                         ['eccentricity_Winput', 'radius_Winput'],
                                         ['inclination_Winput', 'rotation_Winput'],
                                         ['loan_Winput', 'name_Winput'],
                                         ['periapsis_angle_Winput', 'primary_Winput'],
                                         ['epoch_angle_Winput'],
                                         ['create_body_button']],
                      'length': 30}

    doppler_radar_block = {'doppler_radar_block': [['vector_menu_dropdown'],
                                                   ['positions_Winput'],
                                                   ['speeds_Winput'],
                                                   ['locations_Winput'],
                                                   ['mass_Winput'],
                                                   ['radius_Winput'],
                                                   ['rotation_Winput'],
                                                   ['name_Winput'],
                                                   ['primary_Winput'],
                                                   ['create_body_button']],
                           'length': 25}

    radar_block = {'radar_block': [['vector_menu_dropdown'],
                                   ['positions_1_Winput'],
                                   ['positions_2_Winput'],
                                   ['positions_3_Winput'],
                                   ['locations_Winput'],
                                   ['mass_Winput'],
                                   ['radius_Winput'],
                                   ['rotation_Winput'],
                                   ['name_Winput'],
                                   ['primary_Winput'],
                                   ['create_body_button']],
                   'length': 25}

    no_maneuver_block = {'no_maneuver_block': [['maneuver_menu_dropdown']],
                         'length': 22}

    hohmann_block = {'hohmann_block': [['maneuver_menu_dropdown'],
                                       ['maneuver_date_Winputs'],
                                       ['maneuver_time_Winputs'],
                                       ['maneuver_initial_radius_Winput'],
                                       ['maneuver_final_radius_Winput']],
                     'length': 22}

    bielliptic_block = {'bielliptic_block': [['maneuver_menu_dropdown'],
                                             ['maneuver_date_Winputs'],
                                             ['maneuver_time_Winputs'],
                                             ['maneuver_initial_radius_Winput'],
                                             ['maneuver_final_radius_Winput'],
                                             ['maneuver_transfer_apoapsis_Winput']],
                        'length': 22}

    general_block = {'general_block': [['maneuver_menu_dropdown'],
                                       ['maneuver_date_Winputs'],
                                       ['maneuver_time_Winputs'],
                                       ['maneuver_initial_radius_Winput'],
                                       ['maneuver_final_radius_Winput'],
                                       ['maneuver_transfer_eccentricity_Winput']],
                     'length': 22}

    plane_change_block = {'plane_change_block': [['maneuver_menu_dropdown'],
                                                 ['maneuver_date_Winputs'],
                                                 ['maneuver_time_Winputs'],
                                                 ['maneuver_initial_radius_Winput'],
                                                 ['maneuver_inclination_change_Winput']],
                          'length': 22}


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
    thin_space = '\u200a'


    def __init__(self, scene):
        """
        :param scene: The desired VPython canvas.
        """

        self.scene = scene
        super().__init__()

    def box_char(self, char):
        chars = {'top_l': '\u256d' + ' ', 'top_r': '\u256e', 'bot_l': '\u2570' + ' ', 'bot_r': '\u256f',
                 'vert': '\u254f', 'horiz': '\u254c' + ' '}
        return chars[char]

    def create_title_row(self):
        self.scene.title = ''
        for func in self.title_row:
            getattr(self, func)()

    def create_caption_row(self):
        self.scene.caption = ''
        for func in self.caption_row:
            getattr(self, func)()
        self.scene.append_to_caption('\n\n')
        if self.axes:
            self.show_axes.checked = True

    def create_caption(self, block):
        self.create_caption_row()
        self.create_caption_block(block)

    def widget_startup(self):
        self.create_title_row()
        self.create_caption_row()
        self.body_menu.disabled = self.pause.disabled = True

    def sphere_value_reset(self, full=False):
        for key, value in self.sphere_value_dict.items():
            if not full and key is not 'primary':
                setattr(self, key, value)




    def create_caption_block(self, block):
        chars = {'top_l': '\u256d'+' ', 'top_r': '\u256e', 'bot_l': '\u2570'+' ', 'bot_r': '\u256f',
                 'vert': '\u254f', 'horiz': '\u254c'+' '}

        self.current_blocks = [list(getattr(self, arg).keys())[0] for arg in block]
        block_values = [self.create_box_block(arg) for arg in block if hasattr(self, arg)]

        # gets the length of the longest row
        i = 0
        for row in block_values:
            l = len(row)
            if l > i:
                i = l

        # creates a new list with the elements in the proper order
        blocks = []
        for j in range(i):
            temp = []
            for k in range(len(block_values)):
                try:
                    temp.append(block_values[k][j])
                except IndexError:
                    pass
            blocks.append(temp)

        # removes some redundant list brackets
        for l in range(len(blocks)):
            for m in range(len(blocks[l])):
                if m == 0:
                    pass
                else:
                    blocks[l][0] = blocks[l][0] + blocks[l][m]
            blocks[l] = blocks[l][0]

        # displays the contents of the list
        for row in blocks:
            for func in range(len(row)+1):
                if func != len(row):
                    if row[func] in chars.keys():
                        self.scene.append_to_caption(chars[row[func]])
                    else:
                        getattr(self, row[func])()
                else:
                    self.scene.append_to_caption('\n')

    def create_box_block(self, block):
        dictionary = getattr(self, block)
        new_dictionary = copy.deepcopy(dictionary)
        block_values = new_dictionary[block]
        horiz_num = new_dictionary['length']

        horiz = ['horiz']*horiz_num
        box_block = [['top_l', *horiz, 'top_r'],
                     'vert',
                     ['bot_l', *horiz, 'bot_r']]

        block_values.append(box_block[2])
        block_values.insert(0, box_block[0])
        for i in range(len(block_values)):
            if i != 0 and i != len(block_values)-1:
                block_values[i].insert(0, box_block[1])
                block_values[i].append(box_block[1])
        return block_values




    def save_scenario_button_func(self, b):
        # save as option
        # will need a winput
        return
    def save_scenario_button(self):
        return




    def pause_button_func(self, b):
        if self.scenario_running:
            self.running = not self.running
            if self.running:
                b.text = '<b>Pause</b>'
            else:
                b.text = '<b>Play</b>'

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
            self.widget_startup()

    def reset_button(self):
        self.reset = button(text='<b>\u21BA</b>', pos=self.scene.title_anchor, bind=self.reset_button_func,
                            background=vector(0.7, 0.7, 0.7))

    def camera_follow_func(self, w):
        if isinstance(w.number, int):
            w.text = w.number
            sph = self.spheres[w.number]
            self.scene.camera.follow(sph)
            #self.set_zoom(sph.radius, 0.75)

    def camera_follow_Winput(self):
        self.follow_text = wtext(text='   <b>Sphere to Follow: </b>', pos=self.scene.title_anchor)
        self.follow_input = Winput(bind=self.camera_follow_func, text='index', pos=self.scene.title_anchor)

    def dt_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            self.dt = w.text = w.number

    def dt_Winput(self):
        self.dt_text = wtext(text='   <b>Time Step (s): </b>', pos=self.scene.title_anchor)
        self.dt_input = Winput(bind=self.dt_Winput_func, text=f'{self.dt}', pos=self.scene.title_anchor)

    def frame_rate_Winput_func(self, w):
        if isinstance(w.number, int):
            self.frame_rate = w.text = w.number

    def frame_rate_Winput(self):
        self.frame_rate_text = wtext(text='   <b>Frame Rate: </b>', pos=self.scene.title_anchor)
        self.frame_rate_input = Winput(bind=self.frame_rate_Winput_func, text=f'{self.frame_rate}',
                                       pos=self.scene.title_anchor)

    def show_axes_checkbox_func(self, c):
        self.axes = not self.axes
        if self.primary:
            self.primary.toggle_axes()

    def show_axes_checkbox(self):
        self.show_axes = checkbox(pos=self.scene.caption_anchor, bind=self.show_axes_checkbox_func, text='Toggle Axes')




    def loading(self, state):
        if state:
            self.loading_message = label(text='Building Scenario', height=45, font='sans', box=False)
        else:
            self.loading_message.visible = False
            del self.loading_message
            self.loading_message = None

    def set_zoom(self, obj_radius, radii_num):
        self.scene.autoscale = False
        self.scene.range = obj_radius+radii_num*obj_radius
        self.scene.autoscale = True




    def scenario_menu_func(self, m):

        def preset(func, zoom=False, **kwargs):
            m.selected = 'Choose Scenario...'
            m.disabled = True
            self.loading(True)
            self.spheres = list(func(**kwargs))
            self.primary = self.spheres[0]
            self.scene.camera.follow(self.primary)
            if zoom:
                self.set_zoom(self.primary.radius, 5)
            self.loading(False)
            #self.body_menu.disabled = False

        if m.selected == 'Choose Scenario...':
            pass

        if m.selected == 'Create Scenario':
            self.body_menu.disabled = False

        elif m.selected == 'Earth Satellites':
            self.dt_input.text = self.dt = 100
            preset(presets.satellites, zoom=True, rows=2600, show_axes=self.axes)

        elif m.selected == 'Earth Satellites Perturbed':
            self.dt_input.text = self.dt = 100
            preset(presets.satellites_perturbed, zoom=True, rows=2600, body_semi_latus_rectum=30000,
                   body_eccentricity=0.4, show_axes=self.axes)

        elif m.selected == self.preset_maneuvers[0]:
            preset(presets.hohmann, start_time=datetime.datetime.now() + datetime.timedelta(seconds=5000),
                   inclination=30, show_axes=self.axes)

        elif m.selected == self.preset_maneuvers[1]:
            preset(presets.bi_elliptic, start_time=datetime.datetime.now() + datetime.timedelta(seconds=5000),
                   inclination=75, show_axes=self.axes)

        elif m.selected == self.preset_maneuvers[2]:
            preset(presets.general, start_time=datetime.datetime.now() + datetime.timedelta(seconds=5000),
                   inclination=120, show_axes=self.axes)

        elif m.selected == self.preset_maneuvers[3]:
            preset(presets.plane_change, start_time=datetime.datetime.now() + datetime.timedelta(seconds=5000),
                   show_axes=self.axes)

        elif m.selected == 'Earth and Moon':
            preset(presets.earth_moon, show_axes=self.axes)

    def scenario_menu_dropdown(self):
        c = ['Choose Scenario...', 'Create Scenario', 'Earth Satellites', 'Earth Satellites Perturbed',
             'Earth and Moon', *self.preset_maneuvers]
        self.scenario_menu = menu(choices=c, bind=self.scenario_menu_func)




    def start_time_menu_func(self, m):
        if m.selected == 'Present Time':
            self.start_time = 'now'
            self.year_input.disabled = self.month_input.disabled = self.day_input.disabled = \
                self.hour_input.disabled = self.minute_input.disabled = self.second_input.disabled = True

        elif m.selected == 'Custom Time':
            self.year_input.disabled = self.month_input.disabled = self.day_input.disabled = \
                self.hour_input.disabled = self.minute_input.disabled = self.second_input.disabled = False
            #self.create_caption_block(self.starting_time_block)

    def start_time_menu_dropdown(self):
        c = ['Present Time', 'Custom Time']
        self.start_time_menu = menu(choices=c, bind=self.start_time_menu_func)
        self.scene.append_to_caption(' '*63+self.thin_space*2)

    def start_time_Winput_func(self, w):
        if isinstance(w.number, int):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def date_Winputs(self):
        self.date_text = wtext(text='Date (UTC): ')
        self.scene.append_to_caption(' '*2+self.thin_space)
        self.year_input = Winput(text='Year', attr='_year', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(' ')
        self.month_input = Winput(text='Month', attr='_month', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(' ')
        self.day_input = Winput(text='Day', attr='_day', bind=self.start_time_Winput_func)
        self.year_input.disabled = self.month_input.disabled = self.day_input.disabled = True

    def time_Winputs(self):
        self.time_text = wtext(text='Time (UTC): ')
        self.scene.append_to_caption(' '*2)
        self.hour_input = Winput(text='Hour', attr='_hour', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(' ')
        self.minute_input = Winput(text='Minute', attr='_minute', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(' ')
        self.second_input = Winput(text='Second', attr='_second', bind=self.start_time_Winput_func)
        self.hour_input.disabled = self.minute_input.disabled = self.second_input.disabled = True

    def set_time_button_func(self):
        if self.start_time_menu.selected == 'Custom Time' and self._year is not None and self._month is not None and \
                        self._day is not None and self._hour is not None and self._minute is not None and self._second:
            self.start_time = datetime.datetime(year=self._year, month=self._month, day=self._day, hour=self._hour,
                                                minute=self._minute, second=self._second)
            self._year = self._month = self._day = self._hour = self._minute = self._second = None
            self.create_caption_row()
            self.body_menu.disabled = True

    def set_time_button(self):
        self.set_time = button(text='<b>Set Start Time</b>', bind=self.set_time_button_func,
                               background=vector(0.7, 0.7, 0.7))
        self.scene.append_to_caption(' '*62+self.thin_space*3)




    def body_menu_func(self, m):
        if self.spheres:
            if m.selected == 'Choose Body...':
                pass
            elif m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption(('vectors_block', 'starting_time_block'))
                self.body_menu.selected = m.selected

                if self.scenario_running:
                    self.scene_height_sub = self.canvas_build_height_sub

            else:
                self.sphere_value_reset()
                preset = self.preset_bodies_dict[m.selected]
                self.mass = preset.mass
                self.radius = preset.radius
                self.rotation = preset.angular_rotation
                self.name = str(preset())
                self.texture = preset.texture
                self.body_menu.selected = m.selected
                self.create_caption(('vectors_block', 'starting_time_block'))

                if self.scenario_running:
                    self.scene_height_sub = self.canvas_build_height_sub

        else:
            if m.selected == 'Choose Body...':
                pass
            if m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption(('vectors_block', 'starting_time_block'))
                self.body_menu.selected = m.selected
                self.vector_menu.selected = 'Vectors'
            else:
                preset = self.preset_bodies_dict[m.selected]
                self.mass = preset.mass
                self.radius = preset.radius
                self.rotation = preset.angular_rotation
                self.name = str(preset())
                self.texture = preset.texture
                self.create_caption_block(('vectors_block', 'starting_time_block'))
                self.vector_menu.disabled = self.create_body.disabled = True
                self.previous_sphere = self.primary = Sphere(pos=(0, 0, 0), vel=(0, 0, 0), preset=preset,
                                                             show_axes=self.axes)
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
                self.widget_startup()
                self.run_scenario.text = '<b>End Scenario</b>'
                self.pause.disabled = self.body_menu.disabled = False
                self.scene_height_sub = self.canvas_simulate_height_sub
            else:
                #b.text = '<b>Run Scenario</b>'
                self.pause.disabled = True
                for sph in self.spheres:
                    sph.delete()
                self.default_values()
                self.widget_startup()
                self.scene_height_sub = self.canvas_build_height_sub

    def run_scenario_button(self):
        self.run_scenario = button(text='<b>Run Scenario</b>', bind=self.run_scenario_button_func,
                                   background=vector(0.7, 0.7, 0.7), pos=self.scene.title_anchor)




    def vector_menu_func(self, m):
        if m.selected == 'Vectors':
            #self.sphere_value_reset()
            self.create_caption(('vectors_block', 'starting_time_block'))
            self.vector_menu.selected = m.selected

        elif m.selected == 'Elements':
            #self.sphere_value_reset()
            self.create_caption(('elements_block', 'hohmann_block', 'starting_time_block'))
            self.vector_menu.selected = m.selected

        elif m.selected == 'Doppler Radar':
            # self.sphere_value_reset()
            self.create_caption(('doppler_radar_block', 'starting_time_block'))
            self.vector_menu.selected = m.selected

        elif m.selected == 'Radar':
            # self.sphere_value_reset()
            self.create_caption(('radar_block', 'starting_time_block'))
            self.vector_menu.selected = m.selected

    def vector_menu_dropdown(self):
        spacing = {'vectors_block': ' '*72+self.thin_space*2, 'elements_block': ' '*91+self.thin_space*2,
                   'doppler_radar_block': ' '*71+self.thin_space*6, 'radar_block': ' '*72}
        c = ['Vectors', 'Elements', 'Doppler Radar', 'Radar']
        self.vector_menu = menu(choices=c, bind=self.vector_menu_func)

        for key in spacing.keys():
            if key in self.current_blocks:
                self.scene.append_to_caption(spacing[key])




    def maneuver_menu_func(self, m):

        def func(m):
            vector_options = {'Elements': 'elements_block', 'Doppler Radar': 'doppler_radar_block',
                              'Radar': 'radar_block'}
            maneuver_options = {'No Maneuver': 'hohmann_block', 'Hohmann Transfer': 'hohmann_block',
                                'Bi-Elliptic Transfer': 'bielliptic_block', 'General Transfer': 'general_block',
                                'Simple Plane Change': 'plane_change_block'}

            selected = m.selected
            if selected == 'No Maneuver':
                boolean = True
            else:
                boolean = False
            vect = self.vector_menu.selected
            self.create_caption((vector_options[vect], maneuver_options[selected], 'starting_time_block'))
            self.vector_menu.selected = vect
            self.maneuver_menu.selected = selected
            self.maneuver_year_input.disabled = self.maneuver_month_input.disabled = \
                self.maneuver_day_input.disabled = self.maneuver_hour_input.disabled = \
                self.maneuver_minute_input.disabled = self.maneuver_second_input.disabled = boolean
            self.semi_latus_rectum_input.disabled = self.eccentricity_input.disabled = \
                self.periapsis_angle_input.disabled = not boolean

        if m.selected == 'No Maneuver':
            func(m)
            self.maneuver = None

        elif m.selected == 'Hohmann Transfer':
            func(m)
            self.maneuver = Hohmann

        elif m.selected == 'Bi-Elliptic Transfer':
            func(m)
            self.maneuver = BiElliptic

        elif m.selected == 'General Transfer':
            func(m)
            self.maneuver = GeneralTransfer

        elif m.selected == 'Simple Plane Change':
            func(m)
            self.maneuver = SimplePlaneChange

    def maneuver_menu_dropdown(self):
        c = ['No Maneuver', *self.preset_maneuvers]
        self.maneuver_menu = menu(choices=c, bind=self.maneuver_menu_func)
        self.scene.append_to_caption(' '*52)

    def initial_radius_Winput_func(self, w):
        self.template_Winput_func(w)
        self.semi_latus_rectum_input.text = self.semi_latus_rectum = getattr(self, w.attr)

    def maneuver_initial_radius_Winput(self):
        spacing = {'hohmann_block': (' '*2, ' '*35+self.thin_space*5), 'bielliptic_block': (' '*8+self.thin_space*3, ' '*29),
                   'general_block': (' '*4+self.thin_space*2, ' '*33), 'plane_change_block': (' '*7+self.thin_space, ' '*30)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        self.maneuver_initial_radius_text = wtext(text='Initial Radius (km): ')
        self.scene.append_to_caption(space_1)
        self.maneuver_initial_radius_input = Winput(text='', bind=self.initial_radius_Winput_func,
                                                    attr='initial_radius')
        self.scene.append_to_caption(space_2)

    def maneuver_final_radius_Winput(self):
        spacing = {'hohmann_block': (' '*3+self.thin_space*3, ' '*35+self.thin_space*5), 'bielliptic_block': (' '*10, ' '*29),
                   'general_block': (' '*6, ' '*33)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        self.maneuver_final_radius_text = wtext(text='Final Radius (km): ')
        self.scene.append_to_caption(space_1)
        self.maneuver_final_radius_input = Winput(text='', bind=self.template_Winput_func, attr='final_radius')
        self.scene.append_to_caption(space_2)

    def maneuver_transfer_apoapsis_Winput(self):
        self.maneuver_transfer_apoapsis_text = wtext(text='Transfer Apoapsis (km): ')
        self.scene.append_to_caption(' '*2)
        self.maneuver_transfer_apoapsis_input = Winput(text='', bind=self.template_Winput_func,
                                                       attr='transfer_apoapsis')
        self.scene.append_to_caption(' '*29)

    def maneuver_transfer_eccentricity_Winput(self):
        self.maneuver_transfer_eccentricity_text = wtext(text='Transfer Eccentricity: ')
        self.scene.append_to_caption(' '*2)
        self.maneuver_transfer_eccentricity_input = Winput(text='', bind=self.template_Winput_func,
                                                           attr='transfer_eccentricity')
        self.scene.append_to_caption(' '*33)

    def maneuver_inclination_change_Winput(self):
        self.maneuver_inclination_change_text = wtext(text='Inclination Change (\u00b0): ')
        self.scene.append_to_caption(' '*2)
        self.maneuver_inclination_change_input = Winput(text='', bind=self.template_Winput_func,
                                                           attr='inclination_change')
        self.scene.append_to_caption(' '*30)

    def maneuver_date_Winputs(self):
        self.maneuver_date_text = wtext(text='Date (UTC): ')
        self.scene.append_to_caption(' '*2+self.thin_space)
        self.maneuver_year_input = Winput(text='Year', bind=self.start_time_Winput_func, attr='maneuver_year')
        self.scene.append_to_caption(' ')
        self.maneuver_month_input = Winput(text='Month', bind=self.start_time_Winput_func, attr='maneuver_month')
        self.scene.append_to_caption(' ')
        self.maneuver_day_input = Winput(text='Day', bind=self.start_time_Winput_func, attr='maneuver_day')
        self.maneuver_year_input.disabled = self.maneuver_month_input.disabled = \
            self.maneuver_day_input.disabled = True

    def maneuver_time_Winputs(self):
        self.maneuver_time_text = wtext(text='Time (UTC): ')
        self.scene.append_to_caption(' '*2)
        self.maneuver_hour_input = Winput(text='Hour', bind=self.start_time_Winput_func, attr='maneuver_hour')
        self.scene.append_to_caption(' ')
        self.maneuver_minute_input = Winput(text='Minute', bind=self.start_time_Winput_func, attr='maneuver_minute')
        self.scene.append_to_caption(' ')
        self.maneuver_second_input = Winput(text='Second', bind=self.start_time_Winput_func, attr='maneuver_second')
        self.maneuver_hour_input.disabled = self.maneuver_minute_input.disabled = \
            self.maneuver_second_input.disabled = True




    def vector_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            getattr(self, w.attr)[w.index] = w.number

    def position_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'position'}
        self.position_text = wtext(text='Position (km): ')
        self.scene.append_to_caption(' '*16+self.thin_space*4)
        self.position_x_input = Winput(index=0, text=str(self.position[0]), **kwargs)
        self.position_y_input = Winput(index=1, text=str(self.position[1]), **kwargs)
        self.position_z_input = Winput(index=2, text=str(self.position[2]), **kwargs)

    def velocity_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'velocity'}
        self.velocity_text = wtext(text='Velocity (km/s): ')
        self.scene.append_to_caption(' '*13+self.thin_space*5)
        self.velocity_x_input = Winput(index=0, text=str(self.velocity[0]), **kwargs)
        self.velocity_y_input = Winput(index=1, text=str(self.velocity[1]), **kwargs)
        self.velocity_z_input = Winput(index=2, text=str(self.velocity[2]), **kwargs)
        self.scene.append_to_caption(self.thin_space)

    def template_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def semi_latus_rectum_Winput(self):
        self.semi_latus_rectum_text = wtext(text='Semilatus Rectum (km): ')
        self.scene.append_to_caption(' '*2)
        self.semi_latus_rectum_input = Winput(bind=self.template_Winput_func, text=str(self.semi_latus_rectum),
                                              attr='semi_latus_rectum')

    def eccentricity_Winput(self):
        self.eccentricity_text = wtext(text='Eccentricity: ')
        self.scene.append_to_caption(' '*19+self.thin_space*3)
        self.eccentricity_input = Winput(bind=self.template_Winput_func, text=str(self.eccentricity),
                                         attr='eccentricity')

    def inclination_Winput(self):
        self.inclination_text = wtext(text='Inclination (\u00b0): ')
        self.scene.append_to_caption(' '*15+self.thin_space*5)
        self.inclination_input = Winput(bind=self.template_Winput_func, text=str(self.inclination),
                                        attr='inclination')

    def loan_Winput(self):
        self.loan_text = wtext(text='Long. of Asc. Node (\u00b0): ')
        self.scene.append_to_caption(' '*3+self.thin_space*5)
        self.loan_input = Winput(bind=self.template_Winput_func, text=str(self.loan), attr='loan')

    def periapsis_angle_Winput(self):
        self.periapsis_text = wtext(text='Periapsis Angle (\u00b0): ')
        self.scene.append_to_caption(' '*9+self.thin_space)
        self.periapsis_angle_input = Winput(bind=self.template_Winput_func, text=str(self.periapsis_angle),
                                            attr='periapsis_angle')

    def epoch_angle_Winput(self):
        self.epoch_angle_text = wtext(text='Epoch Angle (\u00b0): ')
        self.scene.append_to_caption(' '*13+self.thin_space)
        self.epoch_angle_input = Winput(bind=self.template_Winput_func, text=str(self.epoch_angle),
                                        attr='epoch_angle')
        self.scene.append_to_caption(' '*58+self.thin_space*3)

    def mass_Winput(self):
        spacing = {'vectors_block': ('', ' '*21+self.thin_space*4, ' '*39+self.thin_space*2),
                   'elements_block': (' '*3+self.thin_space*2, ' '*19, ''),
                   'doppler_radar_block': ('', ' '*21+self.thin_space*2, ' '*39+self.thin_space*3),
                   'radar_block': ('', ' '*21+self.thin_space*3, ' '*39+self.thin_space*2)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]
                space_3 = spacing[key][2]

        self.scene.append_to_caption(space_1)
        self.mass_text = wtext(text='Mass (kg): ')
        self.scene.append_to_caption(space_2)
        self.mass_input = Winput(bind=self.template_Winput_func, text=str(self.mass), attr='mass')
        self.scene.append_to_caption(space_3)

    def radius_Winput(self):
        spacing = {'vectors_block': ('', ' '*18+self.thin_space, ' '*39+self.thin_space*3),
                   'elements_block': (' '*3+self.thin_space*2, ' '*15+self.thin_space*3, ''),
                   'doppler_radar_block': ('', ' '*17+self.thin_space*6, ' '*39+self.thin_space*2),
                   'radar_block': ('', ' '*18, ' '*39+self.thin_space*3)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]
                space_3 = spacing[key][2]

        self.scene.append_to_caption(space_1)
        self.radius_text = wtext(text='Radius (km): ')
        self.scene.append_to_caption(space_2)
        self.radius_input = Winput(bind=self.template_Winput_func, text=str(self.radius), attr='radius')
        self.scene.append_to_caption(space_3)

    def rotation_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, math.radians(w.number))

    def rotation_Winput(self):
        spacing = {'vectors_block': ('', ' '*4+self.thin_space*4, ' '*39+self.thin_space*3),
                   'elements_block': (' '*3+self.thin_space*2, ' '*2, ''),
                   'doppler_radar_block': ('', ' '*4+self.thin_space*3, ' '*39+self.thin_space*2),
                   'radar_block': ('', ' '*4+self.thin_space*3, ' '*39+self.thin_space*3)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]
                space_3 = spacing[key][2]

        self.scene.append_to_caption(space_1)
        self.rotation_text = wtext(text='Angular Velocity (\u00b0/s): ')
        self.scene.append_to_caption(space_2)
        self.rotation_input = Winput(bind=self.rotation_Winput_func, text=str(self.rotation), attr='rotation')
        self.scene.append_to_caption(space_3)

    def name_Winput_func(self, w):
        if isinstance(w.text, str):
            self.name = w.text.lower()

    def name_Winput(self):
        spacing = {'vectors_block': ('', ' '*27+self.thin_space*2, ' '*39+self.thin_space*3),
                   'elements_block': (' '*3+self.thin_space*2, ' '*24+self.thin_space*4, ''),
                   'doppler_radar_block': ('', ' '*27+self.thin_space, ' '*39+self.thin_space*2),
                   'radar_block': ('', ' '*27+self.thin_space, ' '*39+self.thin_space*3)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]
                space_3 = spacing[key][2]

        self.scene.append_to_caption(space_1)
        self.name_text = wtext(text='Name: ')
        self.scene.append_to_caption(space_2)
        if not self.name:
            self.name = f'Custom {len(self.spheres)}'
        self.name_input = Winput(bind=self.name_Winput_func, text=self.name, type='string')
        self.scene.append_to_caption(space_3)

    def primary_Winput_func(self, w):
        if isinstance(w.text, str):
            for sph in self.spheres:
                if w.text.lower() == sph.name:
                    self.primary = sph

    def primary_Winput(self):
        spacing = {'vectors_block': ('', ' '*24+self.thin_space*4, ' '*39+self.thin_space*2),
                   'elements_block': (' '*3+self.thin_space*2, ' '*22, ''),
                   'doppler_radar_block': ('', ' '*24+self.thin_space*3, ' '*39+self.thin_space*2),
                   'radar_block': ('', ' '*24+self.thin_space*3, ' '*39+self.thin_space*3)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]
                space_3 = spacing[key][2]

        self.scene.append_to_caption(space_1)
        self.primary_text = wtext(text='Primary: ')
        self.scene.append_to_caption(space_2)
        if self.primary:
            text = self.primary.name
        else:
            text = str(self.primary)
        self.primary_input = Winput(bind=self.primary_Winput_func, text=text, type='string')
        self.scene.append_to_caption(space_3)





    def positions_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions'}
        self.positions_text = wtext(text='Position (km, \u00b0, \u00b0):  ')
        self.scene.append_to_caption(' '*8+self.thin_space*2)
        self.range_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_input = Winput(index=2, text='Altitude', **kwargs)

    def speeds_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'speeds'}
        self.speeds_text = wtext(text='Speed (km/s, \u00b0/s, \u00b0/s):  ')
        self.scene.append_to_caption(' '*2+self.thin_space)
        self.range_speed_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_speed_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_speed_input = Winput(index=2, text='Altitude', **kwargs)

    def locations_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'locations'}
        self.locations_text = wtext(text='Location (km, \u00b0, \u00b0):  ')
        self.scene.append_to_caption(' '*7+self.thin_space*2)
        self.elevation_input = Winput(index=0, text='Elevation', **kwargs)
        self.latitude_input = Winput(index=1, text='Latitude', **kwargs)
        self.local_sidereal_time_input = Winput(index=2, text='LST', **kwargs)


    def positions_1_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_1'}
        self.positions_1_text = wtext(text='Position 1 (km, \u00b0, \u00b0):  ')
        self.scene.append_to_caption(' '*5+self.thin_space*3)
        self.range_1_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_1_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_1_input = Winput(index=2, text='Altitude', **kwargs)

    def positions_2_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_2'}
        self.positions_2_text = wtext(text='Position 2 (km, \u00b0, \u00b0):  ')
        self.scene.append_to_caption(' '*5+self.thin_space*3)
        self.range_2_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_2_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_2_input = Winput(index=2, text='Altitude', **kwargs)

    def positions_3_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_3'}
        self.positions_3_text = wtext(text='Position 3 (km, \u00b0, \u00b0):  ')
        self.scene.append_to_caption(' '*5+self.thin_space*3)
        self.range_3_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_3_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_3_input = Winput(index=2, text='Altitude', **kwargs)



    def create_body_func(self):
        kwargs = {'mass': self.mass, 'radius': self.radius, 'rotation_speed': self.rotation, 'texture': self.texture,
                  'make_trail': True, 'retain': 200, 'name': self.name, 'primary': self.primary,
                  'maneuver': self.maneuver, 'initial_radius': self.initial_radius, 'final_radius': self.final_radius,
                  'transfer_apoapsis': self.transfer_apoapsis, 'transfer_eccentricity': self.transfer_eccentricity,
                  'inclination_change': self.inclination_change}

        if self.maneuver_year is not None and self.maneuver_month is not None and self.maneuver_day is not None and \
                        self.maneuver_hour is not None and self.maneuver_minute is not None and \
                        self.maneuver_second is not None:
            kwargs['start_time'] = datetime.datetime(year=self.maneuver_year, month=self.maneuver_month,
                                                     day=self.maneuver_day, hour=self.maneuver_hour,
                                                     minute=self.maneuver_minute, second=self.maneuver_second)
            self.maneuver_year = self.maneuver_month = self.maneuver_day = self.maneuver_hour = \
                self.maneuver_minute = self.maneuver_second = None

        if self.vector_menu.selected == 'Elements':
            vectors = Elements(self.semi_latus_rectum, self.eccentricity, self.inclination, self.loan,
                               self.periapsis_angle, self.epoch_angle, self.primary.grav_parameter, True)

            self.previous_sphere = Sphere(pos=vectors.position, vel=vectors.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
            if self.previous_sphere is self.primary:
                self.previous_sphere.toggle_axes()

        elif self.vector_menu.selected == 'Doppler Radar':
            vectors = DopplerRadar(positions=self.positions, speeds=self.speeds, station_location=self.locations,
                                   angular_velocity=self.primary.rotational_speed, degrees=True)
            self.previous_sphere = Sphere(pos=vectors.geo_position, vel=vectors.geo_velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
            if self.previous_sphere is self.primary:
                self.previous_sphere.toggle_axes()

        elif self.vector_menu.selected == 'Radar':
            pass

        elif self.vector_menu.selected == 'Vectors':
            # The given position & velocity Winput values are with respect to some chosen primary body,
            # and then those values are converted to be with respect to the system primary body
            self.previous_sphere = Sphere(pos=self.position, vel=self.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
            if self.previous_sphere is self.primary:
                self.previous_sphere.toggle_axes()

        self.sphere_value_reset()
        self.create_caption_row()
        if self.scenario_running:
            self.scene_height_sub = self.canvas_simulate_height_sub

    def create_body_button(self):
        spacing = {'vectors_block': ' '*75+self.thin_space*3, 'elements_block': ' '*94+self.thin_space*5,
                   'doppler_radar_block': ' '*75+self.thin_space*2, 'radar_block': ' '*75+self.thin_space*2}

        self.create_body = button(text='<b>Create Body</b>', bind=self.create_body_func,
                                  background=vector(0.7, 0.7, 0.7))

        for key in spacing.keys():
            if key in self.current_blocks:
                self.scene.append_to_caption(spacing[key])




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
                if obj is self.primary:
                    self.primary = None
                obj.delete()

            elif self.scenario_running:
                if isinstance(self.labelled_sphere, Sphere):
                    self.labelled_sphere.labelled = False
                self.labelled_sphere = obj
                obj.labelled = True

        elif self.scenario_running:
            if isinstance(self.labelled_sphere, Sphere):
                self.labelled_sphere.labelled = False
            self.labelled_sphere = None

    def set_controls(self):
        self.widget_startup()
        self.scene.bind('keyup', self.space_up)
        self.scene.bind('mousedown', self.mouse_down)
