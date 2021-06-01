import time
import datetime
import math
QUIET_HOURS = [[23, 6]]


def is_time_elapsed_greater_than(minutes, starting_time, is_timer_overridden):
    if is_timer_overridden:
        return False
    else:
        return (int(time.time()) - starting_time) > (minutes * 60)


def is_time_minute_increment(starting_time, upper_limit, multiple):
    time_elapsed = math.floor((time.time() - starting_time) / 60)
    if time_elapsed > upper_limit or time_elapsed == 0:
        return False
    else:
        return (time_elapsed % multiple) == 0
    # return False if time_elapsed > upper_limit else (time_elapsed % multiple) == 0


# hour ranges for the quiet hours are inclusive
def quiet_hours():
    # Important to note that indexing for hours is fucking weird:
    #   0: 12 (midnight)
    #   1: 1
    #   2: 2, etc...
    for hour_range in QUIET_HOURS:
        beginning_hour = hour_range[0]
        ending_hour = hour_range[1]
        current_hour = datetime.datetime.now().hour
        # 23 - 6 (positive)
        if (beginning_hour - ending_hour) >= 0:
            return (beginning_hour <= current_hour <= 23) or (0 <= current_hour <= ending_hour)
        # 6 - 23 (negative)
        else:
            return beginning_hour <= current_hour <= ending_hour
