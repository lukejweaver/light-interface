import RPi.GPIO as GPIO
import data_helper

def setmode_bcm():
    GPIO.setmode(GPIO.BCM)


class MotionSensor:
    def __init__(self, gpio=None):
        self.gpio = gpio
        GPIO.setup(self.gpio, GPIO.IN)

    def sensor_status(self):
        return GPIO.input(self.gpio)

    def individual_sensed(self):
        return data_helper.checkbox_value(self.sensor_status())
