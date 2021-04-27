# import RPi.GPIO as GPIO


def setmode_bcm():
    1
    # GPIO.setmode(GPIO.BCM)


class MotionSensor:
    def __init__(self, gpio=None):
        self.gpio = gpio
        # GPIO.setup(self.gpio, GPIO.IN)

    def sensor_status(self):
        return 0
        # return GPIO.input(self.gpio)
