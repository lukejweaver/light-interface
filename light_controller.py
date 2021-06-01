#  Update when:                Relevant information to send:
#  - Setting is changed        - Each setting state
#  - Brightness has changed    - Brightness and current brightness
#  - Hours change in a         - Time since last motion
#     meaningful way           - Motion detected
#  - Time changes in a 
#     meaningful way
#  - Motion is sensed
import datetime
import time_helper


class LightController:
    def __init__(self, sengled_api, application):
        self.sengled_api = sengled_api
        self.current_brightness = self.sengled_api.device_brightness()
        self.are_lights_on = self.sengled_api.device_state()
        self.is_display_on = True
        application.add_observer(self)

    def update(self, updated_brightness, is_brightness_overridden, is_lights_out, is_timer_overridden,
               time_since_last_motion, frame_focus_timer):
        should_turn_lights_off = (
            time_helper.is_time_elapsed_greater_than(minutes=5, starting_time=time_since_last_motion,
                                                     is_timer_overridden=is_timer_overridden) or
            self.is_quiet_hours(is_brightness_overridden=is_brightness_overridden) or
            is_lights_out
        )

        if should_turn_lights_off and self.are_lights_on:
            self.lights_off()
        elif not self.are_lights_on and not should_turn_lights_off:
            self.lights_on()

        if not self.is_correct_brightness(updated_brightness=updated_brightness, is_brightness_overridden=is_brightness_overridden) and not should_turn_lights_off:
            self.update_brightness(self.get_brightness(updated_brightness=updated_brightness, is_brightness_overridden=is_brightness_overridden))

    def is_quiet_hours(self, is_brightness_overridden):
        if is_brightness_overridden:
            return False
        else:
            return time_helper.quiet_hours()

    def get_brightness(self, updated_brightness, is_brightness_overridden):
        if not is_brightness_overridden:
            if datetime.datetime.now().hour == 22:
                return 10
            else:
                return 100
        else:
            return updated_brightness

    def update_brightness(self, new_brightness):
        self.sengled_api.set_devices_brightness(new_brightness)
        self.current_brightness = new_brightness

    def is_correct_brightness(self, updated_brightness, is_brightness_overridden):
        return self.get_brightness(updated_brightness=updated_brightness,
                                   is_brightness_overridden=is_brightness_overridden) == self.current_brightness

    def lights_off(self):
        self.are_lights_on = False
        self.sengled_api.devices_off()

    def lights_on(self):
        self.are_lights_on = True
        self.sengled_api.devices_on()
