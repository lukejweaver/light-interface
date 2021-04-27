import RPi.GPIO as GPIO


def setmode_bcm():
    GPIO.setmode(GPIO.BCM)


class MotionSensor:
    def __init__(self, gpio=None):
        self.gpio = gpio
        GPIO.setup(self.gpio, GPIO.IN)

    def sensor_status(self):
        return GPIO.input(self.gpio)
