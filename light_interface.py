#!/usr/bin/env python3
# pip3 install git+https://github.com/vroy/python-sengled-client.git#egg=sengled-client

import datetime
import tkinter as tk
import time
import os
import motion_detector
import sengled_interface
import light_controller
import screen_controller
import time_helper
import data_helper
from threading import Thread


# start_hour, end_hour inclusive
def time_between(start_hour, end_hour):
    return start_hour <= datetime.datetime.now().hour <= end_hour


def close():
    os._exit(1)


class App(tk.Frame):
    def __init__(self, sengled_api, master=None):
        tk.Frame.__init__(self, master)
        master['bg'] = '#4a4a4a'
        master.bind('<Button-1>', self.reset_frame_focus_timer)

        self.is_display_on = True

        self.sengled_api = sengled_api

        self.brightness = self.sengled_api.device_brightness()

        self.master = master
        self.scale_variable = tk.IntVar()
        self.brightness_override = tk.IntVar()
        self.timer_override = tk.IntVar()
        self.lights_out = tk.IntVar()

        self.new_frame = tk.Frame(master, bg='#4a4a4a')

        # Checkbutton for manual override
        self.brightness_override_checkbox = tk.Checkbutton(self.new_frame, text='Brightness Override', variable=self.brightness_override, onvalue=1, offvalue=0,
                                                           bg='#4a4a4a', pady=20, highlightthickness=0, bd=0, command=self.set_update_required)
        self.brightness_override_checkbox.grid(row=1)

        # Checkbutton for timer override
        self.timer_override_checkbox = tk.Checkbutton(self.new_frame, text='Timer Override', variable=self.timer_override, onvalue=1, offvalue=0,
                                                      bg='#4a4a4a', pady=20, highlightthickness=0, bd=0, command=self.set_update_required)
        self.timer_override_checkbox.grid(row=2)

        # Checkbutton for lights off override
        self.timer_override_checkbox = tk.Checkbutton(self.new_frame, text='Lights Out', variable=self.lights_out, onvalue=1, offvalue=0,
                                                      bg='#4a4a4a', pady=20, highlightthickness=0, bd=0, command=self.set_update_required)
        self.timer_override_checkbox.grid(row=3)

        # Button to end the program
        button = tk.Button(self.new_frame, text='End Program', fg='#4a4a4a', command=close, bd=0)
        button.grid(row=4)

        self.new_frame.pack(side=tk.RIGHT, padx=50)

        # Scale for setting light level (input only matters when manual override set)
        self.scale = tk.Scale(master, variable=self.scale_variable, bd=0, width=width/4, from_=100, to=0, sliderrelief='groove',
                              sliderlength=height/10, length=height, background='#4a4a4a', fg="gray",
                              troughcolor='#a3f6ff', highlightthickness=0, command=self.set_update_required)
        self.scale.pack(side=tk.LEFT, anchor='c', pady=10, padx=10)

        self.detector = motion_detector.MotionSensor(PIR_GPIO)
        self.time_since_last_motion = int(time.time())
        self.are_lights_on = self.sengled_api.device_state()

        # For continuous check for motion
        self.individual_sensed = False
        self.update_required = False
        self.frame_focus_timer = int(time.time())
        self.previous_hour = 0
        self.observers = []
        self.begin_sensing_thread()

    def reset_frame_focus_timer(self, *args):
        self.frame_focus_timer = int(time.time())
        self.set_update_required()

    def begin_sensing_thread(self):
        scale_thread = Thread(target=self.motion_detection)
        scale_thread.start()

    def set_update_required(self, *args):
        self.update_required = True

    def add_observer(self, observer):
        self.observers.append(observer)

    def check_motion_detection(self):
        motion_detected = self.detector.individual_sensed()
        if motion_detected:
            self.time_since_last_motion = int(time.time())

        return motion_detected

    def update_observers(self):
        for observer in self.observers:
            observer.update(
                updated_brightness=self.scale_variable.get(),
                is_brightness_overridden=data_helper.checkbox_value(self.brightness_override.get()),
                is_lights_out=data_helper.checkbox_value(self.lights_out.get()),
                is_timer_overridden=data_helper.checkbox_value(self.timer_override.get()),
                time_since_last_motion=self.time_since_last_motion,
                frame_focus_timer=self.frame_focus_timer
            )
        self.update_required = False

    def motion_detection(self):
        while True:
            # When do we want updates?
            # - five minute increments (up to 15 minutes) :check:
            # - Any settings are changed :check:
            # - On the hour change :check:
            # - When motion detected :check:
            #  WE DON'T FUCKING CARE ABOUT THE OBSERVERS DUDE

            current_hour = datetime.datetime.now().hour

            # Has side effect of setting time_since_last_motion
            self.individual_sensed = self.check_motion_detection()
            if (
                time_helper.is_time_minute_increment(
                    starting_time=self.time_since_last_motion,
                    upper_limit=15,
                    multiple=5
                ) or
                time_helper.is_time_minute_increment(
                    starting_time=self.frame_focus_timer,
                    upper_limit=3,
                    multiple=1
                ) or
                self.individual_sensed or
                self.previous_hour != current_hour or
                self.update_required
            ):
                self.update_observers()
                self.previous_hour = current_hour

            # Resets lights_out value at 12 (midnight)
            if datetime.datetime.now().hour == 0:
                self.lights_out.set(0)

            time.sleep(1)


if __name__ == "__main__":
    # execute only if run as a script
    motion_detector.setmode_bcm()
    PIR_GPIO = 21
    SCR_GPIO = 20
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')
    root.attributes('-fullscreen', True)
    sengled_interface = sengled_interface.SengledInterface()
    app = App(sengled_interface, root)
    light_controller.LightController(sengled_interface, app)
    screen_controller.ScreenController(app, SCR_GPIO)
    root.wm_title("Light interface")
    root.mainloop()
