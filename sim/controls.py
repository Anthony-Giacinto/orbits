import math
import copy
import datetime
from vpython import button, winput, wtext, menu, keysdown, vector, label, checkbox
from orbits.sim.sphere import Sphere
from orbits.astro.params import Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune, gravity
from orbits.astro.vectors import Elements, DopplerRadar, Radar
import orbits.scenarios.presets as presets
from orbits.astro.maneuvers import Hohmann, BiElliptic, GeneralTransfer, SimplePlaneChange


class Winput(winput):
    def __init__(self, width=98.95, **kwargs):
        kwargs['height'] = 23
        kwargs['width'] = width
        super().__init__(**kwargs)

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value):
        raise AttributeError('Cannot change the winput height attribute.')


class AttributeManager:
    """ Contains important class attributes. """

    canvas_build_height_sub = 490
    canvas_simulate_height_sub = 250
    gravity = gravity(units='km')
    preset_bodies_dict = {body.classname: body
                          for body in [Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn, Uranus, Neptune]}
    preset_maneuvers_dict = {maneuver.classname: maneuver
                             for maneuver in [Hohmann, BiElliptic, GeneralTransfer, SimplePlaneChange]}
    pixel_per_space = 197.9/18 # approximate amount of pixels per character on startup with current font settings
    convert_time_units = {'s': 1, 'min': 60, 'hr': 3600}

    attr_dict = {'running': True, 'scenario_running': False, 'previous_sphere': None, 'labelled_sphere': None,
                 'loading_message': None, 'spheres': [], 'dt': 1.0, 'time_rate': 1, 'start_time': 'now',
                 '_year': None, '_month': None, '_day': None, '_hour': None, '_minute': None, '_second': None,
                 'scene_height_sub': canvas_build_height_sub, 'axes': False, 'current_blocks': None, 'maneuver': None,
                 'year_input': None, 'month_input': None, 'day_input': None, 'hour_input': None, 'minute_input': None,
                 'second_input': None, 'maneuver_year': None,  'maneuver_month': None, 'maneuver_day': None,
                 'maneuver_hour': None, 'maneuver_minute': None, 'maneuver_second': None, 'time_units': 's',
                 'time_rate_seconds': 1}

    sphere_value_dict = {'position': [0.0, 0.0, 0.0], 'velocity': [0.0, 0.0, 0.0], 'mass': 10.0, 'radius': 100.0,
                         'rotation': 0.0, 'semi_latus_rectum': 0.0, 'eccentricity': 0.0, 'inclination': 0.0,
                         'loan': 0.0, 'periapsis_angle': 0.0, 'epoch_angle': 0.0, 'primary': None, 'name': '',
                         'texture': None, 'positions': [0.0, 0.0, 0.0], 'speeds': [0.0, 0.0, 0.0],
                         'locations': [0.0, 0.0, 0.0], 'positions_1': [0.0, 0.0, 0.0], 'positions_2': [0.0, 0.0, 0.0],
                         'positions_3': [0.0, 0.0, 0.0], 'initial_radius': None, 'final_radius': None,
                         'transfer_apoapsis': None, 'transfer_eccentricity': None, 'inclination_change': None}

    attr_dict.update(sphere_value_dict)

    def __init__(self):
        self.default_values()

    def default_values(self):
        for key, value in self.attr_dict.items():
            if isinstance(value, list) and hasattr(self, key) and key == 'spheres':
                getattr(self, key).clear()
            elif isinstance(value, list) and hasattr(self, key) and key != 'spheres':
                getattr(self, key)[0] = 0.0
                getattr(self, key)[1] = 0.0
                getattr(self, key)[2] = 0.0
            else:
                setattr(self, key, value)


class LocationManager:
    """ Contains information on widget order. """

    # Title Row:
    title_row = {'run_scenario_button': 'run_scenario', 'pause_button': 'pause', 'reset_button': 'reset',
                 'camera_follow_Winput': ('follow_text', 'follow_input'), 'dt_Winput': ('dt_text', 'dt_input'),
                 'time_rate_Winput': ('time_rate_text', 'time_rate_input'),
                 'time_rate_units_menu_dropdown': 'time_rate_units_menu'}

    # Caption Rows:
    caption_row = {'scenario_menu_dropdown': 'scenario_menu', 'body_menu_dropdown': 'body_menu',
                   'show_axes_checkbox': 'show_axes'}

    # Caption Blocks:
    starting_time_block = {'starting_time_block': [['start_time_menu_dropdown'],
                                                   ['date_Winputs'],
                                                   ['time_Winputs'],
                                                   ['set_time_button']],
                           'length': 41}

    vectors_block = {'vectors_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                       ['position_Winput'],
                                       ['velocity_Winput'],
                                       ['mass_Winput'],
                                       ['radius_Winput'],
                                       ['rotation_Winput'],
                                       ['name_Winput'],
                                       ['primary_Winput'],
                                       ['create_body_button']],
                     'length': 51}

    elements_block = {'elements_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                         ['semi_latus_rectum_Winput', 'mass_Winput'],
                                         ['eccentricity_Winput', 'radius_Winput'],
                                         ['inclination_Winput', 'rotation_Winput'],
                                         ['loan_Winput', 'name_Winput'],
                                         ['periapsis_angle_Winput', 'primary_Winput'],
                                         ['epoch_angle_Winput'],
                                         ['create_body_button']],
                      'length': 68}

    doppler_radar_block = {'doppler_radar_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                                   ['positions_Winput'],
                                                   ['speeds_Winput'],
                                                   ['locations_Winput'],
                                                   ['mass_Winput'],
                                                   ['radius_Winput'],
                                                   ['rotation_Winput'],
                                                   ['name_Winput'],
                                                   ['primary_Winput'],
                                                   ['create_body_button']],
                           'length': 51}

    radar_block = {'radar_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
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
                   'length': 51}

    hohmann_block = {'hohmann_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                       ['semi_latus_rectum_Winput', 'mass_Winput', 'maneuver_date_Winputs'],
                                       ['eccentricity_Winput', 'radius_Winput', 'maneuver_time_Winputs'],
                                       ['inclination_Winput', 'rotation_Winput', 'maneuver_initial_radius_Winput'],
                                       ['loan_Winput', 'name_Winput', 'maneuver_final_radius_Winput'],
                                       ['periapsis_angle_Winput', 'primary_Winput'],
                                       ['epoch_angle_Winput'],
                                       ['create_body_button']],
                     'length': 111}

    bielliptic_block = {'bielliptic_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                             ['semi_latus_rectum_Winput', 'mass_Winput', 'maneuver_date_Winputs'],
                                             ['eccentricity_Winput', 'radius_Winput', 'maneuver_time_Winputs'],
                                             ['inclination_Winput', 'rotation_Winput', 'maneuver_initial_radius_Winput'],
                                             ['loan_Winput', 'name_Winput', 'maneuver_final_radius_Winput'],
                                             ['periapsis_angle_Winput', 'primary_Winput', 'maneuver_transfer_apoapsis_Winput'],
                                             ['epoch_angle_Winput'],
                                             ['create_body_button']],
                        'length': 111}

    general_block = {'general_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                       ['semi_latus_rectum_Winput', 'mass_Winput', 'maneuver_date_Winputs'],
                                       ['eccentricity_Winput', 'radius_Winput', 'maneuver_time_Winputs'],
                                       ['inclination_Winput', 'rotation_Winput', 'maneuver_initial_radius_Winput'],
                                       ['loan_Winput', 'name_Winput', 'maneuver_final_radius_Winput'],
                                       ['periapsis_angle_Winput', 'primary_Winput', 'maneuver_transfer_eccentricity_Winput'],
                                       ['epoch_angle_Winput'],
                                       ['create_body_button']],
                     'length': 111}

    plane_change_block = {'plane_change_block': [['vector_menu_dropdown', 'maneuver_menu_dropdown'],
                                                 ['semi_latus_rectum_Winput', 'mass_Winput', 'maneuver_date_Winputs'],
                                                 ['eccentricity_Winput', 'radius_Winput', 'maneuver_time_Winputs'],
                                                 ['inclination_Winput', 'rotation_Winput', 'maneuver_initial_radius_Winput'],
                                                 ['loan_Winput', 'name_Winput', 'maneuver_inclination_change_Winput'],
                                                 ['periapsis_angle_Winput', 'primary_Winput'],
                                                 ['epoch_angle_Winput'],
                                                 ['create_body_button']],
                          'length': 111}


class Controls(AttributeManager, LocationManager):
    """ Custom controls for interacting with VPython objects.

    Pause/Run: Hit the Pause/Run button on the screen or press 'p'.
    Delete Object: Left Mouse Click while holding either delete or backspace.
    Change camera: Enter the index of the desired sphere into text box and hit enter.
    """

    def __init__(self, scene):
        """
        :param scene: The desired VPython canvas.
        """

        self.scene = scene
        super().__init__()
        self.set_controls()

    def create_title_row(self):
        self.scene.title = ''
        for func in self.title_row:
            getattr(self, func)()

    def create_caption_row(self):
        self.scene.caption = ''
        for func in self.caption_row:
            getattr(self, func)()
        self.scene.append_to_caption('\n' + '\u2501'*(math.floor(self.scene.width/self.pixel_per_space)) + '\n\n')
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
        chars = {'top_l': '\u256d', 'top_r': '\u256e', 'bot_l': '\u2570', 'bot_r': '\u256f',
                 'vert': '\u2502', 'horiz': '\u2500'}

        if isinstance(block, str):
            self.current_blocks = [block]
            block_values = [self.create_box_block(block)]
        else:
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

        block_values.insert(-1, box_block[2])
        block_values.insert(1, box_block[0])
        for i in range(len(block_values)):
            if i != 0 and i != 1 and i != len(block_values)-1 and i != len(block_values)-2:
                block_values[i].insert(0, box_block[1])
                block_values[i].append(box_block[1])
        return block_values




    def save_scenario_button_func(self, b):
        # save as option
        # will need a winput
        return
    def save_scenario_button(self):
        return




    def set_zoom(self, obj_radius, radii_num):
        self.scene.autoscale = False
        self.scene.range = obj_radius+radii_num*obj_radius
        self.scene.autoscale = True

    def pause_button_func(self, b):
        if self.scenario_running:
            self.running = not self.running
            if self.running:
                b.text = '<b>Pause</b>'
            else:
                b.text = '<b> Play  </b>'

    def pause_button(self):
        self.pause = button(text='<b>Pause</b>', pos=self.scene.title_anchor, bind=self.pause_button_func,
                            background=vector(0.7, 0.7, 0.7))

    def reset_button_func(self, b):
        if self.spheres:
            for sph in self.spheres:
                sph.delete()
        self.default_values()
        self.widget_startup()
        self.scene.lights[0].visible = True

    def reset_button(self):
        self.reset = button(text='<b>Reset</b>', pos=self.scene.title_anchor, bind=self.reset_button_func,
                            background=vector(0.7, 0.7, 0.7))

    def camera_follow_func(self, w):
        for sph in self.spheres:
            if sph.name.lower() == w.text.lower():
                self.scene.camera.follow(sph)

    def camera_follow_Winput(self):
        self.follow_text = wtext(text=' <b>Following: </b>', pos=self.scene.title_anchor)
        self.follow_input = Winput(bind=self.camera_follow_func, pos=self.scene.title_anchor,
                                   type='string')

    def dt_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            if self.dt < self.time_rate_seconds:
                self.dt = w.text = w.number
            else:
                self.dt = w.text = self.time_rate_seconds

    def dt_Winput(self):
        self.dt_text = wtext(text='  <b>Time Step (s): </b>', pos=self.scene.title_anchor)
        self.dt_input = Winput(bind=self.dt_Winput_func, text=f'{self.dt}', pos=self.scene.title_anchor, width=50)

    def time_rate_Winput_func(self, w):
        if isinstance(w.number, int):
            self.time_rate = w.number
            self.time_rate_seconds = self.time_rate*self.convert_time_units[self.time_units] # in seconds
            if self.time_rate_seconds > self.dt:
                w.text = self.time_rate # in chosen units
            else:
                self.time_rate_seconds = w.text = self.dt

    def time_rate_Winput(self):
        self.time_rate_text = wtext(text='  <b>Time Rate (unit/time step): </b>', pos=self.scene.title_anchor)
        self.time_rate_input = Winput(bind=self.time_rate_Winput_func, text=f'{self.time_rate}',
                                      pos=self.scene.title_anchor, width=50)

    def time_rate_units_func(self, m):
        self.time_units = m.selected

    def time_rate_units_menu_dropdown(self):
        c = ['s', 'min', 'hr']
        self.scene.append_to_title(' ')
        self.time_rate_units_menu = menu(choices=c, bind=self.time_rate_units_func, pos=self.scene.title_anchor)

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

    def scenario_menu_func(self, m):

        def preset(func, zoom=False, dt=1.0, time_rate=1, time_units ='s', **kwargs):
            self.loading(True)
            self.time_rate_units_menu.selected = self.time_units = time_units
            self.time_rate_input.text = self.time_rate = time_rate
            self.time_rate_seconds = self.time_rate*self.convert_time_units[self.time_units]
            self.dt_input.text = self.dt = dt
            self.spheres = list(func(**kwargs))
            self.primary = self.spheres[0]
            self.scene.camera.follow(self.primary)
            self.follow_input.text = self.primary.name
            if zoom:
                self.set_zoom(self.primary.radius, 5)
            self.create_caption('starting_time_block')
            self.scenario_menu.disabled = True
            self.loading(False)

        if m.selected == 'Choose Scenario...':
            pass

        elif m.selected == 'Create Scenario':
            self.body_menu.disabled = False

        elif m.selected == 'Earth Satellites':
            preset(presets.satellites, zoom=True, dt=30, time_units='hr', rows=2600, show_axes=self.axes)

        elif m.selected == 'Earth Satellites Perturbed':
            preset(presets.satellites_perturbed, zoom=True, dt=100, time_units='hr', rows=2600,
                   body_semi_latus_rectum=30000, body_eccentricity=0.4, show_axes=self.axes)

        elif m.selected == 'Hohmann Transfer':
            preset(presets.hohmann, start_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=10000),
                   inclination=0, show_axes=self.axes)

        elif m.selected == 'Bi-Elliptic Transfer':
            preset(presets.bi_elliptic, start_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=10000),
                   inclination=0, show_axes=self.axes)

        elif m.selected == 'General Transfer':
            preset(presets.general, start_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=5000),
                   inclination=0, show_axes=self.axes)

        elif m.selected == 'Simple Plane Change':
            preset(presets.plane_change, start_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=5000),
                   show_axes=self.axes)

        elif m.selected == 'Earth and Moon':
            preset(presets.earth_moon, show_axes=self.axes)

    def scenario_menu_dropdown(self):
        c = ['Choose Scenario...', 'Create Scenario', 'Earth Satellites', 'Earth Satellites Perturbed',
             'Earth and Moon', *list(self.preset_maneuvers_dict.keys())]
        self.scenario_menu = menu(choices=c, bind=self.scenario_menu_func)

    def start_time_menu_func(self, m):
        choices = {'Present Time': True, 'Custom Time': False}
        self.year_input.disabled = self.month_input.disabled = self.day_input.disabled = \
            self.hour_input.disabled = self.minute_input.disabled = self.second_input.disabled = \
            self.set_time.disabled = choices[m.selected]

    def start_time_menu_dropdown(self):
        if self.current_blocks[0] == 'starting_time_block':
            space_1 = ' '
            space_2 = ''
        else:
            space_1 = ''
            space_2 = ' '*63

        self.scene.append_to_caption(space_1)
        c = ['Present Time', 'Custom Time']
        self.start_time_menu = menu(choices=c, bind=self.start_time_menu_func)
        self.scene.append_to_caption(space_2)

    def start_time_Winput_func(self, w):
        if isinstance(w.number, int):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def date_Winputs(self):
        self.date_text = wtext(text='Date (UTC): ')
        self.year_input = Winput(text='Year', attr='_year', bind=self.start_time_Winput_func)
        self.scene.append_to_caption('-')
        self.month_input = Winput(text='Month', attr='_month', bind=self.start_time_Winput_func)
        self.scene.append_to_caption('-')
        self.day_input = Winput(text='Day', attr='_day', bind=self.start_time_Winput_func)
        self.year_input.disabled = self.month_input.disabled = self.day_input.disabled = True

    def time_Winputs(self):
        self.time_text = wtext(text='Time (UTC): ')
        self.hour_input = Winput(text='Hour', attr='_hour', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(':')
        self.minute_input = Winput(text='Minute', attr='_minute', bind=self.start_time_Winput_func)
        self.scene.append_to_caption(':')
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
        self.scene.append_to_caption(' ')
        self.set_time = button(text='<b>Set Start Time</b>', bind=self.set_time_button_func,
                               background=vector(0.7, 0.7, 0.7))
        self.set_time.disabled = True

    def body_menu_func(self, m):
        if self.spheres:
            if m.selected == 'Choose Body...':
                self.create_caption_row()

            elif m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption(('vectors_block', 'starting_time_block'))
                self.body_menu.selected = m.selected
                self.maneuver_menu.disabled = True

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
                self.maneuver_menu.disabled = True

                if self.scenario_running:
                    self.scene_height_sub = self.canvas_build_height_sub

        else:
            if m.selected == 'Choose Body...':
                self.create_caption_row()

            elif m.selected == 'Custom':
                self.sphere_value_reset()
                self.create_caption(('vectors_block', 'starting_time_block'))
                self.body_menu.selected = m.selected
                self.maneuver_menu.disabled = True
                self.vector_menu.selected = 'Vectors'
            else:
                preset = self.preset_bodies_dict[m.selected]
                self.mass = preset.mass
                self.radius = preset.radius
                self.rotation = preset.angular_rotation
                self.name = str(preset())
                self.texture = preset.texture
                self.create_caption(('vectors_block', 'starting_time_block'))
                self.vector_menu.disabled = self.create_body.disabled = self.maneuver_menu.disabled = True
                self.previous_sphere = self.primary = Sphere(pos=(0, 0, 0), vel=(0, 0, 0), preset=preset,
                                                             show_axes=self.axes)
                self.spheres.append(self.primary)
                if m.selected == 'Sun':
                    self.scene.lights[0].visible = False
                    self.primary.luminous = True
                self.scene.camera.follow(self.primary)
                self.follow_input.text = self.primary.name
                m.selected = 'Choose Body...'

    def body_menu_dropdown(self):
        c = ['Choose Body...', 'Custom', *list(self.preset_bodies_dict.keys())]
        self.body_menu = menu(choices=c, bind=self.body_menu_func)

    def run_scenario_button_func(self, b):
        if self.spheres and not self.loading_message:
            self.scenario_running = not self.scenario_running
            if self.scenario_running:
                self.create_caption_row()
                self.run_scenario.text = '<b>End Scenario</b>'
                self.pause.disabled = self.body_menu.disabled = False
                self.scene_height_sub = self.canvas_simulate_height_sub
                self.follow_input.text = self.primary.name
                self.time_rate_units_menu.selected = self.time_units

            else:
                self.reset_button_func(self.reset_button)
                self.pause.disabled = True
                self.scene_height_sub = self.canvas_build_height_sub

    def run_scenario_button(self):
        self.run_scenario = button(text='<b>Run Scenario</b>', bind=self.run_scenario_button_func,
                                   background=vector(0.7, 0.7, 0.7), pos=self.scene.title_anchor)

    def vector_menu_func(self, m):
        blocks = {'Vectors': 'vectors_block', 'Elements': 'elements_block',
                  'Doppler Radar': 'doppler_radar_block', 'Radar': 'radar_block'}

        # self.sphere_value_reset()
        self.create_caption((blocks[m.selected], 'starting_time_block'))
        self.vector_menu.selected = m.selected
        if m.selected != 'Elements':
            self.maneuver_menu.disabled = True

    def vector_menu_dropdown(self):
        self.scene.append_to_caption(' ')
        c = ['Vectors', 'Elements', 'Doppler Radar', 'Radar']
        self.vector_menu = menu(choices=c, bind=self.vector_menu_func)

    def maneuver_menu_func(self, m):
        vectors = {'Elements': 'elements_block', 'Doppler Radar': 'doppler_radar_block', 'Radar': 'radar_block'}

        maneuvers = {'No Maneuver': (None, None, True),
                     'Hohmann Transfer': ('hohmann_block', Hohmann, False),
                     'Bi-Elliptic Transfer': ('bielliptic_block', BiElliptic, False),
                     'General Transfer': ('general_block', GeneralTransfer, False),
                     'Simple Plane Change': ('plane_change_block', SimplePlaneChange, False)}

        self.maneuver = maneuvers[m.selected][1]
        boolean = maneuvers[m.selected][2]
        vect = self.vector_menu.selected

        if maneuvers[m.selected][0] is not None:
            self.create_caption((maneuvers[m.selected][0], 'starting_time_block'))
        else:
            self.create_caption((vectors[vect], 'starting_time_block'))

        self.vector_menu.selected = vect
        self.maneuver_menu.selected = m.selected

        self.maneuver_year_input.disabled = self.maneuver_month_input.disabled = \
            self.maneuver_day_input.disabled = self.maneuver_hour_input.disabled = \
            self.maneuver_minute_input.disabled = self.maneuver_second_input.disabled = boolean

        self.semi_latus_rectum_input.disabled = self.eccentricity_input.disabled = \
            self.periapsis_angle_input.disabled = not boolean

    def maneuver_menu_dropdown(self):
        spacing = {'vectors_block': ' '*24, 'elements_block': ' '*41,'doppler_radar_block': ' '*24,
                   'radar_block': ' '*24, 'hohmann_block': ' '*84, 'bielliptic_block': ' '*84,
                   'general_block': ' '*84, 'plane_change_block': ' '*84}
        c = ['No Maneuver', *list(self.preset_maneuvers_dict.keys())]
        self.maneuver_menu = menu(choices=c, bind=self.maneuver_menu_func)

        for key in spacing.keys():
            if key in self.current_blocks:
                self.scene.append_to_caption(spacing[key])

    def initial_radius_Winput_func(self, w):
        self.template_Winput_func(w)
        self.semi_latus_rectum_input.text = self.semi_latus_rectum = getattr(self, w.attr)

    def maneuver_initial_radius_Winput(self):
        spacing = {'hohmann_block': ('', ' '*11), 'bielliptic_block': (' '*3, ' '*8),
                   'general_block': (' '*2, ' '*9), 'plane_change_block': (' '*3, ' '*8)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        self.scene.append_to_caption(' '*2)
        self.maneuver_initial_radius_text = wtext(text='Initial Radius (km): ')
        self.scene.append_to_caption(space_1)
        self.maneuver_initial_radius_input = Winput(text='', bind=self.initial_radius_Winput_func,
                                                    attr='initial_radius')
        self.scene.append_to_caption(space_2)

    def maneuver_final_radius_Winput(self):
        spacing = {'hohmann_block': (' '*2, ' '*11), 'bielliptic_block': (' '*5, ' '*8),
                   'general_block': (' '*4, ' '*9)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        self.scene.append_to_caption(' '*2)
        self.maneuver_final_radius_text = wtext(text='Final Radius (km): ')
        self.scene.append_to_caption(space_1)
        self.maneuver_final_radius_input = Winput(text='', bind=self.template_Winput_func, attr='final_radius')
        self.scene.append_to_caption(space_2)

    def maneuver_transfer_apoapsis_Winput(self):
        self.scene.append_to_caption(' '*2)
        self.maneuver_transfer_apoapsis_text = wtext(text='Transfer Apoapsis (km): ')
        self.maneuver_transfer_apoapsis_input = Winput(text='', bind=self.template_Winput_func,
                                                       attr='transfer_apoapsis')
        self.scene.append_to_caption(' '*8)

    def maneuver_transfer_eccentricity_Winput(self):
        self.scene.append_to_caption(' '*2)
        self.maneuver_transfer_eccentricity_text = wtext(text='Transfer Eccentricity: ')
        self.maneuver_transfer_eccentricity_input = Winput(text='', bind=self.template_Winput_func,
                                                           attr='transfer_eccentricity')
        self.scene.append_to_caption(' '*9)

    def maneuver_inclination_change_Winput(self):
        self.scene.append_to_caption(' '*2)
        self.maneuver_inclination_change_text = wtext(text='Inclination Change (\u00b0): ')
        self.maneuver_inclination_change_input = Winput(text='', bind=self.template_Winput_func,
                                                           attr='inclination_change')
        self.scene.append_to_caption(' '*8)

    def maneuver_date_Winputs(self):
        self.scene.append_to_caption(' '*2)
        self.maneuver_date_text = wtext(text='Date (UTC): ')
        self.maneuver_year_input = Winput(text='Year', bind=self.start_time_Winput_func, attr='maneuver_year')
        self.scene.append_to_caption('-')
        self.maneuver_month_input = Winput(text='Month', bind=self.start_time_Winput_func, attr='maneuver_month')
        self.scene.append_to_caption('-')
        self.maneuver_day_input = Winput(text='Day', bind=self.start_time_Winput_func, attr='maneuver_day')
        self.maneuver_year_input.disabled = self.maneuver_month_input.disabled = \
            self.maneuver_day_input.disabled = True

    def maneuver_time_Winputs(self):
        self.scene.append_to_caption(' '*2)
        self.maneuver_time_text = wtext(text='Time (UTC): ')
        self.maneuver_hour_input = Winput(text='Hour', bind=self.start_time_Winput_func, attr='maneuver_hour')
        self.scene.append_to_caption(':')
        self.maneuver_minute_input = Winput(text='Minute', bind=self.start_time_Winput_func, attr='maneuver_minute')
        self.scene.append_to_caption(':')
        self.maneuver_second_input = Winput(text='Second', bind=self.start_time_Winput_func, attr='maneuver_second')
        self.maneuver_hour_input.disabled = self.maneuver_minute_input.disabled = \
            self.maneuver_second_input.disabled = True

    def vector_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            getattr(self, w.attr)[w.index] = w.number

    def position_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'position'}
        text = 'Position (km): '
        self.position_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.position_x_input = Winput(index=0, text=str(self.position[0]), **kwargs)
        self.position_y_input = Winput(index=1, text=str(self.position[1]), **kwargs)
        self.position_z_input = Winput(index=2, text=str(self.position[2]), **kwargs)

    def velocity_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'velocity'}
        text = 'Velocity (km/s): '
        self.velocity_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.velocity_x_input = Winput(index=0, text=str(self.velocity[0]), **kwargs)
        self.velocity_y_input = Winput(index=1, text=str(self.velocity[1]), **kwargs)
        self.velocity_z_input = Winput(index=2, text=str(self.velocity[2]), **kwargs)

    def template_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, w.number)

    def semi_latus_rectum_Winput(self):
        text = 'Semilatus Rectum (km): '
        self.semi_latus_rectum_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Long. of Asc. Node (\u00b0): ')-len(text)))
        self.semi_latus_rectum_input = Winput(bind=self.template_Winput_func, text=str(self.semi_latus_rectum),
                                              attr='semi_latus_rectum')

    def eccentricity_Winput(self):
        text = 'Eccentricity: '
        self.eccentricity_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Long. of Asc. Node (\u00b0): ')-len(text)))
        self.eccentricity_input = Winput(bind=self.template_Winput_func, text=str(self.eccentricity),
                                         attr='eccentricity')

    def inclination_Winput(self):
        text = 'Inclination (\u00b0): '
        self.inclination_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Long. of Asc. Node (\u00b0): ')-len(text)))
        self.inclination_input = Winput(bind=self.template_Winput_func, text=str(self.inclination),
                                        attr='inclination')

    def loan_Winput(self):
        self.loan_text = wtext(text='Long. of Asc. Node (\u00b0): ')
        self.loan_input = Winput(bind=self.template_Winput_func, text=str(self.loan), attr='loan')

    def periapsis_angle_Winput(self):
        text = 'Periapsis Angle (\u00b0): '
        self.periapsis_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Long. of Asc. Node (\u00b0): ')-len(text)))
        self.periapsis_angle_input = Winput(bind=self.template_Winput_func, text=str(self.periapsis_angle),
                                            attr='periapsis_angle')

    def epoch_angle_Winput(self):
        spacing = {'elements_block': ' '*35, 'hohmann_block': ' '*78, 'bielliptic_block': ' '*78,
                   'general_block': ' '*78, 'plane_change_block': ' '*78}

        text = 'Epoch Angle (\u00b0): '
        self.epoch_angle_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Long. of Asc. Node (\u00b0): ')-len(text)))
        self.epoch_angle_input = Winput(bind=self.template_Winput_func, text=str(self.epoch_angle),
                                        attr='epoch_angle')
        for key in spacing.keys():
            if key in self.current_blocks:
                self.scene.append_to_caption(spacing[key])

    def mass_Winput(self):
        spacing = {'vectors_block': ('', ' '*18), 'elements_block': (' '*2, ''), 'hohmann_block': (' ' * 2, ''),
                   'bielliptic_block': (' '*2, ''), 'general_block': (' '*2, ''),  'plane_change_block': (' '*2, ''),
                   'doppler_radar_block': ('', ' '*18), 'radar_block': ('', ' '*18)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        text = 'Mass (kg): '
        self.scene.append_to_caption(space_1)
        self.mass_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.mass_input = Winput(bind=self.template_Winput_func, text=str(self.mass), attr='mass')
        self.scene.append_to_caption(space_2)

    def radius_Winput(self):
        spacing = {'vectors_block': ('', ' '*18),  'elements_block': (' '*2, ''), 'hohmann_block': (' '*2, ''),
                   'bielliptic_block': (' '*2, ''), 'general_block': (' '*2, ''), 'plane_change_block': (' '*2,''),
                   'doppler_radar_block': ('', ' '*18), 'radar_block': ('', ' '*18)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        text = 'Radius (km): '
        self.scene.append_to_caption(space_1)
        self.radius_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.radius_input = Winput(bind=self.template_Winput_func, text=str(self.radius), attr='radius')
        self.scene.append_to_caption(space_2)

    def rotation_Winput_func(self, w):
        if isinstance(w.number, (int, float)):
            w.text = w.number
            setattr(self, w.attr, math.radians(w.number))

    def rotation_Winput(self):
        spacing = {'vectors_block': ('', ' '*18),  'elements_block': (' '*2, ''), 'hohmann_block': (' '*2, ''),
                   'bielliptic_block': (' '*2, ''), 'general_block': (' '*2, ''), 'plane_change_block': (' '*2, ''),
                   'doppler_radar_block': ('', ' '*18), 'radar_block': ('', ' '*18)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        self.scene.append_to_caption(space_1)
        self.rotation_text = wtext(text='Angular Velocity (\u00b0/s): ')
        self.rotation_input = Winput(bind=self.rotation_Winput_func, text=str(self.rotation), attr='rotation')
        self.scene.append_to_caption(space_2)

    def name_Winput_func(self, w):
        if isinstance(w.text, str):
            self.name = w.text.lower()

    def name_Winput(self):
        spacing = {'vectors_block': ('', ' '*18), 'elements_block': (' '*2, ''), 'hohmann_block': (' '*2, ''),
                   'bielliptic_block': (' '*2, ''), 'general_block': (' '*2, ''), 'plane_change_block': (' '*2, ''),
                   'doppler_radar_block': ('', ' '*18), 'radar_block': ('', ' '*18)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        text = 'Name: '
        self.scene.append_to_caption(space_1)
        self.name_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        if not self.name:
            self.name = f'Custom {len(self.spheres)}'
        self.name_input = Winput(bind=self.name_Winput_func, text=self.name, type='string')
        self.scene.append_to_caption(space_2)

    def primary_Winput_func(self, w):
        if isinstance(w.text, str):
            for sph in self.spheres:
                if w.text.lower() == sph.name:
                    self.primary = sph

    def primary_Winput(self):
        spacing = {'vectors_block': ('', ' '*18), 'elements_block': (' '*2, ''), 'hohmann_block': (' '*2, ' '*43),
                   'bielliptic_block': (' '*2, ''), 'general_block': (' '*2, ''), 'plane_change_block': (' '*2, ' '*43),
                   'doppler_radar_block': ('', ' '*18), 'radar_block': ('', ' '*18)}

        for key in spacing.keys():
            if key in self.current_blocks:
                space_1 = spacing[key][0]
                space_2 = spacing[key][1]

        text = 'Primary: '
        self.scene.append_to_caption(space_1)
        self.primary_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        if self.primary:
            in_text = self.primary.name
        else:
            in_text = str(self.primary)
        self.primary_input = Winput(bind=self.primary_Winput_func, text=in_text, type='string')
        self.scene.append_to_caption(space_2)

    def positions_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions'}
        text = 'Position (km, \u00b0, \u00b0): '
        self.positions_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.range_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_input = Winput(index=2, text='Altitude', **kwargs)

    def speeds_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'speeds'}
        text = 'Speed (km/s, \u00b0/s, \u00b0/s): '
        self.speeds_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.range_speed_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_speed_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_speed_input = Winput(index=2, text='Altitude', **kwargs)

    def locations_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'locations'}
        text = 'Location (km, \u00b0, \u00b0): '
        self.locations_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.elevation_input = Winput(index=0, text='Elevation', **kwargs)
        self.latitude_input = Winput(index=1, text='Latitude', **kwargs)
        self.local_sidereal_time_input = Winput(index=2, text='LST', **kwargs)

    def positions_1_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_1'}
        text = 'Position 1 (km, \u00b0, \u00b0): '
        self.positions_1_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.range_1_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_1_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_1_input = Winput(index=2, text='Altitude', **kwargs)

    def positions_2_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_2'}
        text = 'Position 2 (km, \u00b0, \u00b0): '
        self.positions_2_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
        self.range_2_input = Winput(index=0, text='Range', **kwargs)
        self.azimuth_2_input = Winput(index=1, text='Azimuth', **kwargs)
        self.altitude_2_input = Winput(index=2, text='Altitude', **kwargs)

    def positions_3_Winput(self):
        kwargs = {'bind': self.vector_Winput_func, 'attr': 'positions_3'}
        text = 'Position 3 (km, \u00b0, \u00b0): '
        self.positions_3_text = wtext(text=text)
        self.scene.append_to_caption(' '*(len('Angular Velocity (\u00b0/s): ')-len(text)))
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
            vectors = Radar(positions_one=self.positions_1, positions_two=self.positions_2,
                            positions_three=self.positions_3, station_location=self.locations,
                            gravitational_parameter=self.primary.grav_parameter, degrees=True)
            self.previous_sphere = Sphere(pos=vectors.position, vel=vectors.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
            if self.previous_sphere is self.primary:
                self.previous_sphere.toggle_axes()

        elif self.vector_menu.selected == 'Vectors':
            self.previous_sphere = Sphere(pos=self.position, vel=self.velocity, **kwargs)
            self.spheres.append(self.previous_sphere)
            if self.previous_sphere is self.primary:
                self.previous_sphere.toggle_axes()

        self.sphere_value_reset()
        self.create_caption_row()
        if self.scenario_running:
            self.scene_height_sub = self.canvas_simulate_height_sub

    def create_body_button(self):
        self.scene.append_to_caption(' ')
        self.create_body = button(text='<b>Create Body</b>', bind=self.create_body_func,
                                  background=vector(0.7, 0.7, 0.7))

    def space_up(self):
        if 'p' in keysdown():
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
            else:
                if isinstance(self.labelled_sphere, Sphere):
                    self.labelled_sphere.labelled = False
                self.labelled_sphere = obj
                obj.labelled = True
        else:
            if isinstance(self.labelled_sphere, Sphere):
                self.labelled_sphere.labelled = False
            self.labelled_sphere = None

    def set_controls(self):
        self.widget_startup()
        self.scene.bind('keyup', self.space_up)
        self.scene.bind('mousedown', self.mouse_down)
