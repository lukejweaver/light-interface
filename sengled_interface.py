import sengled

class SengledInterface:
    def __init__(self):
        self.api = sengled.api(
            username="lukejweaver01@gmail.com",
            password="TheFlash14!",
            session_path="/tmp/sengled.pickle",
            debug=False,
            retry=True
        )

    def light_api(self):
        return self.api

    def devices(self):
        return self.api.get_device_details()

    def devices_off(self):
        self.api.set_off(self.devices())

    def devices_on(self):
        self.api.set_on(self.devices())

    def set_devices_brightness(self, brightness):
        self.api.set_brightness(self.devices(), brightness)

    def device_state(self):
        return 'on' if self.devices()[0].onoff is True else 'off'

    def device_brightness(self):
        return self.devices()[0].brightness
