"""
A simple Game using the kivy framework.
"""
import sys
import random

from kivy.config import Config

# Config.set('graphics', 'width', '1366')
# Config.set('graphics', 'fullscreen', 'auto')
# Config.set('graphics', 'window_state', 'maximized')
# Config.set('graphics', 'height', '768')
Config.set('kivy', 'window_icon', 'images/bg1.jpeg')

from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
from kivy.graphics.context import Clock
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

Builder.load_file('menu.kv')


class GameWidget(RelativeLayout):
    """A class to hold all the game functionalities."""
    from keyboard_actions import keyboard_closed, key_pressed, key_released, \
        on_touch_down, on_touch_up
    from transformation import transform, transformation_in_2D, \
        converging_point_transformation

    menu_widget = ObjectProperty()
    converging_point_x = NumericProperty()
    converging_point_y = NumericProperty()
    vertical_lines = []
    number_of_vertical_lines = 10
    vertical_spacing = .4
    current_offset_x = 0
    SPEED_X = 3
    speed_x = 0

    horizontal_lines = []
    number_of_horizontal_lines = 15
    horizontal_spacing = .2
    current_offset_y = 0
    SPEED_Y = 1.0

    number_of_tiles = 9
    tiles = []
    tile_coordinates = []
    y_loop = 0

    ship = None
    ship_height = 0.035
    ship_width = 0.1
    ship_base_height = 0.04
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    volume = .5

    game_over = False
    active = False

    game_title = StringProperty('G      A       L       A       X       Y')
    play_button = StringProperty('PLAY')
    scores = StringProperty()
    level = StringProperty()
    levels = list(range(0, 100000, 50))
    level_offset = 1
    pause_button = StringProperty("PAUSE")
    exit_button = StringProperty("EXIT")
    f_size = dp(30)
    # set_score = 0

    sound_begin = None
    sound_galaxy = None
    sound_game_over_impact = None
    sound_game_over_voice = None
    sound_music = None
    sound_restart = None
    pause = False
    music_one = None

    platforms = None

    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.initiate_audio()
        self.set_audio_volume()
        self.initiate_vertical_lines()
        self.initiate_horizontal_lines()
        self.initiate_tiles()
        self.initiate_ship()
        self.reset()
        self.sound_galaxy.play()

        if self.desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.key_pressed)
            self.keyboard.bind(on_key_up=self.key_released)
        Clock.schedule_interval(self.update, 1.0 / 60)

    def desktop(self):
        """
        Enable the keyboard on desktops only.
        """
        self.platforms = ('linux', 'win', 'windows', 'macosx')
        if platform in self.platforms:
            return True
        return False

    def initiate_vertical_lines(self):
        """
        Create vertical lines along the screen.
        And store them in a list
        """
        with self.canvas:
            # Give the lines a color.
            Color(1, 1, 1)
            for i in range(0, self.number_of_vertical_lines):
                self.vertical_lines.append(Line())

    def initiate_horizontal_lines(self):
        """
        Create horizontal lines across the screen.
        And store them in a list
        """
        with self.canvas:
            # Give the lines a color.
            Color(1, 1, 1)
            for i in range(0, self.number_of_horizontal_lines):
                self.horizontal_lines.append(Line())

    def get_line_x(self, index):
        """Get the x coordinates."""
        center_x = self.converging_point_x
        x_offset = index - 0.5
        spacing = self.vertical_spacing * self.width
        x_point = center_x + x_offset * spacing + self.current_offset_x
        return x_point

    def update_vertical_lines(self):
        """
        Assign points to all lines.
        Automatically adjust the points depending on the screen size.
        """
        start_point = -int(self.number_of_vertical_lines / 2) + 1
        for i in range(start_point, start_point + self.number_of_vertical_lines):
            x_point = self.get_line_x(i)
            x1, y1 = self.transform(x_point, 0)
            x2, y2 = self.transform(x_point, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def get_line_y(self, index):
        """Get the y coordinates."""
        y_spacing = self.horizontal_spacing * self.height
        y_point = index * y_spacing - self.current_offset_y
        return y_point

    def update_horizontal_lines(self):
        """
        Assign points to all lines.
        Automatically adjust the points depending on the screen size.
        """
        start_point = -int(self.number_of_vertical_lines / 2) + 1
        end_point = start_point + self.number_of_vertical_lines - 1

        # The starting point of the horizontal line.
        # Which is the furthest vertical line to the left.
        x_min = self.get_line_x(start_point)
        # The end point of the horizontal line.
        # Which is the furthest vertical line to the right.
        x_max = self.get_line_x(end_point)
        for i in range(0, self.number_of_horizontal_lines):
            y_point = self.get_line_y(i)
            x1, y1 = self.transform(x_min, y_point)
            x2, y2 = self.transform(x_max, y_point)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def initiate_tiles(self):
        """
        Create tiles in a quad shape.
        Append them in a list.
        """
        with self.canvas:
            Color(0, 1, 1)
            for i in range(0, self.number_of_tiles):
                self.tiles.append(Quad())

    def prefill_tiles(self):
        """Add the first ten tiles in a straight line."""
        for i in range(0, 10):
            self.tile_coordinates.append((0, i))

    def generate_coordinates(self):
        """
        Continuously generate tile coordinates.
        Delete coordinates that are out of the screen.
        """
        last_point_y = 0
        last_point_x = 0
        for i in range(len(self.tile_coordinates) - 1, -1, -1):
            if self.tile_coordinates[i][1] < self.y_loop:
                del self.tile_coordinates[i]

            if len(self.tile_coordinates) > 0:
                last_coordinates = self.tile_coordinates[-1]
                last_point_x = last_coordinates[0]
                last_point_y = last_coordinates[1] + 1

        for i in range(len(self.tile_coordinates), self.number_of_tiles):
            # Random generate tiles to the left and right side.
            random_x = random.randint(0, 2)
            start_point = -int(self.number_of_vertical_lines / 2) + 1
            end_point = start_point + self.number_of_vertical_lines - 1

            if last_point_x <= start_point:
                # Restrict generation of tiles past the furthest x point on the left.
                random_x = 1
            elif last_point_x >= end_point - 1:
                # Restrict generation of tiles past the furthest x point on the right.
                random_x = 2

            self.tile_coordinates.append((last_point_x, last_point_y))
            if random_x == 1:
                last_point_x += 1
                self.tile_coordinates.append((last_point_x, last_point_y))
                last_point_y += 1
                self.tile_coordinates.append((last_point_x, last_point_y))
            elif random_x == 2:
                last_point_x -= 1
                self.tile_coordinates.append((last_point_x, last_point_y))
                last_point_y += 1
                self.tile_coordinates.append((last_point_x, last_point_y))

            last_point_y += 1

    def get_tile_coordinates(self, t_x, t_y):
        t_y = t_y - self.y_loop
        x = self.get_line_x(t_x)
        y = self.get_line_y(t_y)
        return x, y

    def update_tiles(self):
        """Update the position of the tiles on the screen."""
        for i in range(0, self.number_of_tiles):
            tile = self.tiles[i]
            tiles_coordinates = self.tile_coordinates[i]
            x_min, y_min = self.get_tile_coordinates(tiles_coordinates[0], tiles_coordinates[1])
            x_max, y_max = self.get_tile_coordinates(tiles_coordinates[0] + 1, tiles_coordinates[1] + 1)
            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def initiate_ship(self):
        """Create a ship in a triangle shape."""
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        """Constantly update the ship position."""
        center_x = self.converging_point_x
        half_ship_width = self.ship_width * self.width / 2
        base_y = self.ship_base_height * self.height
        ship_height = self.ship_height * self.height

        self.ship_coordinates[0] = (center_x - half_ship_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + half_ship_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_tile_ship_collusion(self, t_x, t_y):
        x_min, y_min = self.get_tile_coordinates(t_x, t_y)
        x_max, y_max = self.get_tile_coordinates(t_x + 1, t_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def check_ship_collision(self):
        for i in range(0, len(self.tile_coordinates)):
            t_x, t_y = self.tile_coordinates[i]
            if t_y > self.y_loop + 1:
                return False
            if self.check_tile_ship_collusion(t_x, t_y):
                return True
        return False

    def update(self, dt):
        """
        Update the screen 60 times in a second.
        """
        dt = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.game_over and self.active:
            speed = self.SPEED_Y * self.height / 100
            self.current_offset_y += speed * dt
            y_spacing = self.horizontal_spacing * self.height
            while self.current_offset_y >= y_spacing:
                self.current_offset_y -= y_spacing
                self.y_loop += 1
                # self.set_score += 5
                self.scores = 'SCORE : ' + str(self.y_loop)

                if self.y_loop in self.levels:
                    self.level_offset += 1
                    self.level = 'LEVEL : ' + str(self.level_offset)
                    self.SPEED_Y += .1

                self.generate_coordinates()
            speed = self.speed_x * self.width / 100
            self.current_offset_x += speed * dt
        self.game_over_actions()
        self.check_screen_width()

    def check_screen_width(self):
        if self.width <= 200:
            self.opacity = 0
            self.sound_music.stop()
            # self.music_one.stop()
        else:
            self.opacity = 1

        if self.width <= 390:
            if self.game_over:
                self.game_title = "GAME OVER"
                self.f_size = dp(10)
            else:
                self.game_title = "GALAXY"
        else:
            if self.game_over:
                self.game_title = "G        A       M       E       O       V       E       R"
                self.f_size = dp(10)
            else:
                self.game_title = "G        A       L       A       X       Y"

    def game_over_actions(self):
        """End the game."""
        if not self.check_ship_collision() and not self.game_over:
            self.game_over = True
            self.menu_widget.opacity = 1
            self.game_title = "G        A       M       E       O       V       E       R"
            self.sound_game_over_impact.play()
            self.sound_music.stop()
            # self.music_one.stop()
            Clock.schedule_once(self.play_game_over_sound, 2)

    def play_game_over_sound(self, dt):
        if self.game_over:
            self.sound_game_over_voice.play()

    def play_button_pressed(self, *args):
        if self.game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music.play()
        # self.music_one.play()
        self.reset()
        self.active = True
        self.menu_widget.opacity = 0

    def reset(self):
        self.current_offset_y = 0
        self.y_loop = 0
        self.SPEED_Y = 1.0
        self.speed_x = 0
        self.current_offset_x = 0
        self.tile_coordinates = []
        self.prefill_tiles()
        self.generate_coordinates()
        self.game_over = False
        self.level_offset = 1
        self.scores = 'SCORE : ' + str(self.y_loop)
        self.level = 'LEVEL : ' + str(self.level_offset)

    def initiate_audio(self):
        self.sound_begin = SoundLoader.load('audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('audio/galaxy.wav')
        self.sound_game_over_impact = SoundLoader.load('audio/game_over_impact.wav')
        self.sound_game_over_voice = SoundLoader.load('audio/game_over_voice.wav')
        self.sound_music = SoundLoader.load('audio/music.wav')
        self.sound_restart = SoundLoader.load('audio/restart.wav')
        self.music_one = SoundLoader.load('audio/Mike Perry - ONE LIFE (Neversea Festival 2019 Official Anthem).mp3')

    def set_audio_volume(self):
        sounds = [
            self.sound_begin,
            self.sound_restart,
            self.sound_music,
            self.sound_game_over_voice,
            self.sound_game_over_impact,
            self.sound_galaxy,
            self.music_one
        ]
        for sound in sounds:
            sound.volume = self.volume

    def pause_game(self):
        if self.active:
            self.active = False
            self.pause = True
            self.sound_music.stop()
            # self.music_one.stop()

    def resume_game(self):
        self.game_over = False
        self.pause = False
        self.active = True
        self.sound_music.play()
        # self.music_one.play()

    def pause_resume_control(self):
        if self.menu_widget.opacity == 0:
            if self.pause:
                self.pause_button = "PAUSE"
                self.resume_game()
                self.pause = False

            else:
                self.pause_game()
                self.pause_button = "RESUME"
                self.pause = True

    def exit(self):
        self.game_over = True
        sys.exit()


class GameApp(App):
    """A class to call the GameWidget class."""

    pass


if __name__ == '__main__':
    Window.fullscreen = 'auto'
    GameApp().run()
