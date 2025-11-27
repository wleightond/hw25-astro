import datetime
import random
import time
from track.utils import DEC, RA, env, move_steps

LONGITUDE = 21.4594

def get_LST(longitude):
    now = datetime.datetime.utcnow()
    YY = now.year
    MM = now.month
    DD = now.day
    hh = now.hour + now.minute/60 + now.second/3600

    JD = (367*YY) - int((7*(YY+int((MM+9)/12)))/4) \
         + int((275*MM)/9) + DD + 1721013.5 + (hh/24)

    GMST = 18.697374558 + 24.06570982441908*(JD - 2451545)
    GMST = GMST % 24

    LST = GMST + longitude/15
    return LST % 24

lst = get_LST(LONGITUDE)


# 18800 steps/h / 3600 sec/h = 5.222... steps/sec; the exact ratio is 47 steps every 9 sec

# 15 degrees is 1h; that is 18800 steps
# 18800 / 15 is 1,253.333...; and we want a whole number,
# so we go for 3 times that; which is 3deg worth of steps
# i.e. 12 minutes of sky
ra_steps_per_3deg = 3760
ra_steps_per_deg = ra_steps_per_3deg / 3

# 45deg on the small wheel is 28800 steps
dec_steps_per_deg = 640 # 28800 // 45

# a full circle is 120 * 3deg
ra_steps_per_day = 120 * ra_steps_per_3deg
seconds_per_day = 24 * 60 * 60
ra_steps_per_second = 47 / 9

def ra_steps_to_deg(steps):
    return 3 * steps / ra_steps_per_3deg

def dec_steps_to_deg(steps):
    return steps / dec_steps_per_deg

original_time = time.time()

def current_baseline(ra_steps=0):
    return int((time.time() - original_time) * ra_steps_per_second) + ra_steps

def move_to_loc(current_ra, current_dec, ra=0, dec=0, verbose=False):
    if verbose or (not (int(time.time())%3) and not (int(time.time()*10)%10)): print(f'move_to_loc current_ra={ra_steps_to_deg(current_ra):.4f} current_dec={dec_steps_to_deg(current_dec):.4f} ra={ra_steps_to_deg(current_baseline(ra)):.4f} dec={dec_steps_to_deg(dec):.4f}')
    dec_diff = dec - current_dec
    if verbose: print(f'    move_steps DEC {dec_diff}')
    move_steps(DEC, abs(dec_diff), dec_diff>0)
    new_dec = current_dec + dec_diff
    ra_diff = current_baseline(ra) - current_ra
    if verbose: print(f'    move_steps RA {ra_diff}')
    move_steps(RA, abs(ra_diff), ra_diff>0)
    new_ra = current_ra + ra_diff
    return new_ra, new_dec

def track_target(ra_deg: float, dec_deg: float):
    dec_steps = int(dec_deg * dec_steps_per_deg)
    ra_steps = int(ra_deg * ra_steps_per_deg)
    with env():
        current_ra, current_dec = current_baseline() + int(ra_steps_per_deg * get_LST(LONGITUDE)), 0

        tmp_ra, tmp_dec = -1, -1
        while tmp_ra != current_ra and tmp_dec != current_dec:
            tmp_ra, tmp_dec = current_ra, current_dec
            current_ra, current_dec = move_to_loc(current_ra, current_dec, ra=ra_steps, dec=dec_steps, verbose=True)
        print('TARGET LOCK')
        print('INIT TRACKING')

        start_baseline = current_ra
        start_time = time.time()

        end_baseline = current_ra
        end_time = time.time()
        try:
            while True:
                current_ra, current_dec = move_to_loc(current_ra, current_dec, ra=ra_steps, dec=dec_steps)
                time.sleep(0.1)
        except:
            pass

    end_baseline = current_ra
    end_time = time.time()
    tdiff = end_time - start_time
    bdiff = end_baseline - start_baseline
    theoretical = int(tdiff * 47 / 9)
    print(f'Averaged {bdiff/tdiff:.2f} steps per second; {tdiff=}; {bdiff=} ({theoretical=}); ')

# print(lst)
track_target(16, 45)