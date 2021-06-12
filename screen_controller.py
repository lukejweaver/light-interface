import RPi.GPIO as GPIO
import time_helper


class ScreenController:
    def __init__(self, application, pin):
        self.gpio_pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.is_display_on = False
        application.add_observer(self)

    def update(self, updated_brightness, is_brightness_overridden, is_lights_out, is_timer_overridden,
               time_since_last_motion, frame_focus_timer):
        if time_helper.is_time_elapsed_greater_than(minutes=1, starting_time=frame_focus_timer,
                                                    is_timer_overridden=False):
            self.screen_off()
        else:
            self.screen_on()

    def screen_off(self):
        if self.is_display_on:
            GPIO.output(self.gpio_pin, 0)
            self.is_display_on = False

    def screen_on(self):
        if not self.is_display_on:
            GPIO.output(self.gpio_pin, 1)
            self.is_display_on = True
