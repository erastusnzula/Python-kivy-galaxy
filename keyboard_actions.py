from kivy.uix.relativelayout import RelativeLayout


def key_pressed(self, keyboard, keycode, text, modifier):
    """
    Facilitate left and right movement using the keyboard keys.
    """
    if keycode[1] == 'left':
        self.speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.speed_x = -self.SPEED_X
    elif keycode[1] == 'enter':
        self.play_button_pressed()
    elif keycode[1] == 'spacebar':
        self.pause_resume_control()
    elif keycode[1] == 'q' or 'esc':
        self.exit()

    return True


def key_released(self, keyboard, keycode):
    """
    Stop left and right movement.
    """
    self.speed_x = 0
    return True


def keyboard_closed(self):
    """
    Unbind key presses on a closed keyboard.
    """
    self.keyboard.unbind(on_key_down=self.key_pressed)
    self.keyboard.unbind(on_key_up=self.key_released)
    self.keyboard = None


def on_touch_down(self, touch):
    """
    Enable mobile and mouse screen touch down functions.
    To facilitate right and left movements.
    """
    if not self.game_over and self.active:
        if touch.x < self.width / 2:
            self.speed_x = self.SPEED_X
        else:
            self.speed_x = -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    """
    Enable mobile and mouse screen touch up functions.
    Stop right and left movements.
    """
    self.speed_x = 0
