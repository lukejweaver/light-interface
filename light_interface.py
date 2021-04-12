#!/usr/bin/env python3
# pip3 install git+https://github.com/vroy/python-sengled-client.git#egg=sengled-client

import datetime
import tkinter as tk
import time
import os
import motion_detector
import sengled_interface
from threading import Thread, Lock


# start_hour, end_hour inclusive
def time_between(start_hour, end_hour):
    return start_hour <= datetime.datetime.now().hour <= end_hour


def close():
    os._exit(1)


class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        master['bg'] = '#4a4a4a'
        button = tk.Button(master, text='Close the window', fg='#4a4a4a', command=close)
        button.pack(pady=10)

        self.sengled_api = sengled_interface.SengledInterface()

        self.brightness = self.sengled_api.device_brightness()

        self.master = master
        self.scale_variable = tk.IntVar()
        self.override = tk.IntVar()

        # Checkbutton for manual override
        self.checkbutton = tk.Checkbutton(master, text='Manual Override', variable=self.override, onvalue=1, offvalue=0,
                                          bg='#4a4a4a', pady=20)
        self.checkbutton.place(relx=0.7, rely=0.5)

        # Scale for setting light level (input only matters when manual override set)
        self.scale = tk.Scale(master, variable=self.scale_variable, bd=0, width=width/10, from_=100, to=0, sliderrelief='groove',
                              sliderlength=height/10, length=height, background='#4a4a4a', fg="gray",
                              troughcolor='#a3f6ff')
        self.scale.pack(side=tk.LEFT, anchor='c')

        # For continuous check for motion
        self.begin_sensing_thread()

    def begin_sensing_thread(self):
        scale_thread = Thread(target=self.motion_detection)
        scale_thread.start()

    def is_correct_brightness(self):
        return self.brightness == self.get_brightness()

    def motion_detection(self):
        detector = motion_detector.MotionSensor(PIR_GPIO)
        time_since_last_motion = time.time()
        light_status = self.sengled_api.device_state()

        while True:
            mutex.acquire()
            motion_sensor = detector.sensor_status()
            if time_between(7, 22):
                if motion_sensor == 0:
                    print(time.time() - time_since_last_motion)
                    print(light_status)
                    print((time.time() - time_since_last_motion) > 10 and (light_status == 'on' or light_status == ''))
                    if (time.time() - time_since_last_motion) > 10 and (light_status == 'on' or light_status == ''):
                        self.sengled_api.devices_off()
                        light_status = 'off'
                        print('no motion detected')
                elif motion_sensor == 1:
                    time_since_last_motion = time.time()
                    if light_status == 'off' or light_status == '' or self.is_correct_brightness() is False:
                        light_status = 'on'
                        self.sengled_api.devices_on()
                        print('motion detected friend')
                        self.sengled_api.set_devices_brightness(self.get_brightness())
                        self.brightness = self.get_brightness()
            elif self.override.get() == 1:
                if not self.is_correct_brightness():
                    self.sengled_api.set_devices_brightness(self.get_brightness())
            elif light_status == 'on' or light_status == '':
                self.sengled_api.devices_off()
                light_status = 'off'
            mutex.release()
            time.sleep(0.5)

    def get_brightness(self):
        if self.override.get() == 0:
            if datetime.datetime.now().hour == 22:
                return 10
            else:
                return 100
        else:
            return self.scale_variable.get()


if __name__ == "__main__":
    # execute only if run as a script
    mutex = Lock()
    motion_detector.setmode_bcm()
    PIR_GPIO = 21
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')
    app = App(root)
    root.wm_title("Light interface")
    root.mainloop()
