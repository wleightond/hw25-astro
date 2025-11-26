import random
import time
from track.utils import env, move_steps

# 18800 steps/h / 3600 sec/h = 5.222... steps/sec; the exact ratio is 47 steps every 9 sec

# 15 degrees is 1h; that is 18800 steps
# 18800 / 15 is 1,253.333...; and we want a whole number,
# so we go for 3 times that; which is 3deg worth of steps
# i.e. 12 minutes of sky
steps_per_3deg = 3760

# a full circle is 120 * 3deg
steps_per_day = 120 * steps_per_3deg
seconds_per_day = 24 * 60 * 60
steps_per_second = 47 / 9

original_time = time.time()

def current_baseline(offset=0):
    return int((time.time() - original_time) * steps_per_second)


def update_to_offset(current_location, offset=0):
    print(f'update_to_offset {current_location=} {offset=}')
    diff = max(0, current_baseline(offset) - current_location)
    print(diff)
    move_steps(diff)
    return diff


def track_target(location: float):
    offset = int(location * steps_per_3deg / 3)
    with env():
        current_location = current_baseline()
        current_location += update_to_offset(current_location, offset)
        start_baseline = current_location
        start_time = time.time()

        try:
            while True:
                current_location += update_to_offset(current_location, offset)
                time.sleep(random.uniform(0, 1))
        except:
            pass

    end_baseline = current_location
    end_time = time.time()

    tdiff = end_time - start_time
    bdiff = end_baseline - start_baseline
    theoretical = int(tdiff * 47 / 9)
    print(f'Averaged {bdiff/tdiff:.2f} steps per second; {tdiff=}; {bdiff=} ({theoretical=}); ')

track_target(0)