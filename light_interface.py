#!/usr/bin/env python3
# pip3 install git+https://github.com/vroy/python-sengled-client.git#egg=sengled-client

from subprocess import run
import datetime
import tkinter as tk
import time
import os
import motion_detector
import sengled_interface
from threading import Thread


# start_hour, end_hour inclusive
def time_between(start_hour, end_hour):
    return start_hour <= datetime.datetime.now().hour <= end_hour


def close():
    os._exit(1)


class App(tk.Frame):
    QUIET_HOURS = [[23, 8]]

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        master['bg'] = '#4a4a4a'

        self.is_display_on = True

        self.sengled_api = sengled_interface.SengledInterface()

        self.brightness = self.sengled_api.device_brightness()

        self.master = master
        self.scale_variable = tk.IntVar()
        self.brightness_override = tk.IntVar()
        self.timer_override = tk.IntVar()
        self.lights_out = tk.IntVar()

        self.new_frame = tk.Frame(master, bg='#4a4a4a')

        # Checkbutton for manual override
        self.brightness_override_checkbox = tk.Checkbutton(self.new_frame, text='Manual Override', variable=self.brightness_override, onvalue=1, offvalue=0,
                                                           bg='#4a4a4a', pady=20, highlightthickness=0, bd=0)
        self.brightness_override_checkbox.grid(row=1)

        # Checkbutton for timer override
        self.timer_override_checkbox = tk.Checkbutton(self.new_frame, text='Timer Override', variable=self.timer_override, onvalue=1, offvalue=0,
                                                      bg='#4a4a4a', pady=20, highlightthickness=0, bd=0)
        self.timer_override_checkbox.grid(row=2)

        # Checkbutton for lights off override
        self.timer_override_checkbox = tk.Checkbutton(self.new_frame, text='Lights Out', variable=self.lights_out, onvalue=1, offvalue=0,
                                                      bg='#4a4a4a', pady=20, highlightthickness=0, bd=0)
        self.timer_override_checkbox.grid(row=3)

        # Button to end the program
        button = tk.Button(self.new_frame, text='End Program', fg='#4a4a4a', command=close, bd=0)
        button.grid(row=4)

        self.new_frame.pack(side=tk.RIGHT, padx=50)

        # Scale for setting light level (input only matters when manual override set)
        self.scale = tk.Scale(master, variable=self.scale_variable, bd=0, width=width/4, from_=100, to=0, sliderrelief='groove',
                              sliderlength=height/10, length=height, background='#4a4a4a', fg="gray",
                              troughcolor='#a3f6ff', highlightthickness=0)
        self.scale.pack(side=tk.LEFT, anchor='c', pady=10, padx=10)

        self.detector = motion_detector.MotionSensor(PIR_GPIO)
        self.time_since_last_motion = int(time.time())
        self.are_lights_on = self.sengled_api.device_state()

        # For continuous check for motion
        self.begin_sensing_thread()

    def begin_sensing_thread(self):
        scale_thread = Thread(target=self.motion_detection)
        scale_thread.start()

    def is_correct_brightness(self):
        return self.brightness == self.get_brightness()

    def peripherals_off(self):
        self.are_lights_on = False
        self.sengled_api.devices_off()
        if self.is_display_on:
            run('vcgencmd display_power 0', shell=True)
            self.is_display_on = False

    def peripherals_on(self):
        self.are_lights_on = True
        self.sengled_api.devices_on()
        self.update_brightness()
        if not self.is_display_on:
            run('vcgencmd display_power 1', shell=True)
            self.is_display_on = True

    def update_brightness(self):
        if not self.is_correct_brightness():
            self.sengled_api.set_devices_brightness(self.get_brightness())
            self.brightness = self.get_brightness()

    def is_timer_up(self):
        time_now = int(time.time())
        return (time_now - self.time_since_last_motion) > 300

    def should_turn_lights_off(self):
        if self.timer_override.get() == 1:
            return False
        if self.brightness_override.get() == 1 and not self.is_timer_up():
            return False
        # If it is lights out or quiet hours and lights are on, turn the lights off
        elif (self.lights_out.get() == 1 or self.quiet_hours()) and self.are_lights_on:
            return True
        else:
            # Make sure no motion detected, the timer is up, and the lights are on
            return not self.motion_detected() and self.is_timer_up() and self.are_lights_on

    def should_turn_lights_on(self):
        if not self.is_correct_brightness() and self.brightness_override.get() == 1:
            return True
        elif self.lights_out.get() == 1:
            return False
        elif self.timer_override.get() == 1 and not self.are_lights_on:
            return True
        else:
            return self.motion_detected() and not self.are_lights_on and not self.quiet_hours() or not self.is_correct_brightness()

    def motion_detected(self):
        motion_detected = self.detector.individual_sensed()
        if motion_detected:
            self.time_since_last_motion = int(time.time())

        return motion_detected

    def motion_detection(self):
        while True:
            # If timer off ignore the time_since_last_motion and motion sensor
            # If manual override is true ignore the quiet hours
            # If turn off until tomorrow then ensure lights are off, if so do nothing (reset at hour == 0)

            if self.should_turn_lights_off():
                self.peripherals_off()
            elif self.should_turn_lights_on():
                self.peripherals_on()

            if datetime.datetime.now().hour == 0:
                self.lights_out.set(0)

            time.sleep(1)

    def get_brightness(self):
        if self.brightness_override.get() == 0:
            if datetime.datetime.now().hour == 22:
                return 10
            else:
                return 100
        else:
            return self.scale_variable.get()

    # hour ranges for the quiet hours are inclusive
    def quiet_hours(self):
        for hour_range in App.QUIET_HOURS:
            beginning_hour = hour_range[0]
            ending_hour = hour_range[1]
            current_hour = datetime.datetime.now().hour
            # 22 - 7 (positive)
            if (beginning_hour - ending_hour) >= 0:
                return (beginning_hour <= current_hour <= 23) or (0 <= current_hour <= ending_hour)
            # 7 - 22 (negative)
            else:
                return beginning_hour <= current_hour <= ending_hour


if __name__ == "__main__":
    # execute only if run as a script
    motion_detector.setmode_bcm()
    PIR_GPIO = 21
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')
    root.attributes('-fullscreen', True)
    app = App(root)
    root.wm_title("Light interface")
    root.mainloop()
