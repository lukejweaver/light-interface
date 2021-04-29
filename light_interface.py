#!/usr/bin/env python3
# pip3 install git+https://github.com/vroy/python-sengled-client.git#egg=sengled-client

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
    QUIET_HOURS = [[22, 7]]

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        master['bg'] = '#4a4a4a'

        self.sengled_api = sengled_interface.SengledInterface()

        self.brightness = self.sengled_api.device_brightness()

        self.master = master
        self.scale_variable = tk.IntVar()
        self.override = tk.IntVar()

        self.new_frame = tk.Frame(master, bg='#4a4a4a')

        # Checkbutton for manual override
        self.checkbutton = tk.Checkbutton(self.new_frame, text='Manual Override', variable=self.override, onvalue=1, offvalue=0,
                                          bg='#4a4a4a', pady=20, highlightthickness=0, bd=0)
        self.checkbutton.grid(row=1)

        # Button to end the program
        button = tk.Button(self.new_frame, text='End Program', fg='#4a4a4a', command=close, bd=0)
        button.grid(row=2)

        self.new_frame.pack(side=tk.RIGHT, padx=50)

        # Scale for setting light level (input only matters when manual override set)
        self.scale = tk.Scale(master, variable=self.scale_variable, bd=0, width=width/4, from_=100, to=0, sliderrelief='groove',
                              sliderlength=height/10, length=height, background='#4a4a4a', fg="gray",
                              troughcolor='#a3f6ff', highlightthickness=0)
        self.scale.pack(side=tk.LEFT, anchor='c', pady=10, padx=10)

        self.detector = motion_detector.MotionSensor(PIR_GPIO)
        self.time_since_last_motion = int(time.time())
        self.light_status = self.sengled_api.device_state()

        # For continuous check for motion
        self.begin_sensing_thread()

    def begin_sensing_thread(self):
        scale_thread = Thread(target=self.motion_detection)
        scale_thread.start()

    def is_correct_brightness(self):
        return self.brightness == self.get_brightness()

    def motion_detection(self):
        while True:
            motion_sensor = self.detector.sensor_status()
            if self.override.get() == 1:
                if not self.is_correct_brightness():
                    self.sengled_api.set_devices_brightness(self.get_brightness())
                    self.brightness = self.get_brightness()
                    self.light_status = 'on'
            elif time_between(7, 22):
                if motion_sensor == 0:
                    if (int(time.time()) - self.time_since_last_motion) > 300 and self.light_status == 'on':
                        self.sengled_api.devices_off()
                        self.light_status = 'off'
                elif motion_sensor == 1:
                    self.time_since_last_motion = int(time.time())
                    if self.light_status == 'off' or self.is_correct_brightness() is False:
                        self.light_status = 'on'
                        self.sengled_api.devices_on()
                        self.sengled_api.set_devices_brightness(self.get_brightness())
                        self.brightness = self.get_brightness()
            elif self.light_status == 'on':
                self.sengled_api.devices_off()
                self.light_status = 'off'
            time.sleep(1)

    def get_brightness(self):
        if self.override.get() == 0:
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
    app = App(root)
    root.wm_title("Light interface")
    root.mainloop()
