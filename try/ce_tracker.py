import datetime
import time
import math
import sys
import select
import RPi.GPIO as GPIO

############################################
# USER SETTINGS
############################################

# Your location (Cape Town example)
LATITUDE  = -33.9249
LONGITUDE = 18.4241   # degrees EAST (use + for East)

# Stepper configuration
STEP_ANGLE = 0.9        # degrees per full step
FULL_STEPS = 360.0 / STEP_ANGLE  # = 400
MICROSTEPS = 16
GEAR_RATIO = 1.0

# Final steps per degree
STEPS_PER_REV   = FULL_STEPS * MICROSTEPS * GEAR_RATIO
STEPS_PER_DEGREE = STEPS_PER_REV / 360.0

print("Steps per degree:", STEPS_PER_DEGREE)

# RA tracking parameters
SIDEREAL_DAY = 86164.0905
SIDEREAL_DEG_PER_SEC = 360.0 / SIDEREAL_DAY
SIDEREAL_STEPS_PER_SEC = STEPS_PER_DEGREE * SIDEREAL_DEG_PER_SEC
print("Sidereal steps/sec:", SIDEREAL_STEPS_PER_SEC)

############################################
# GPIO PINS
############################################

RA_DIR  = 22
RA_STEP = 27
DEC_DIR = 9
DEC_STEP = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(RA_DIR, GPIO.OUT)
GPIO.setup(RA_STEP, GPIO.OUT)
GPIO.setup(DEC_DIR, GPIO.OUT)
GPIO.setup(DEC_STEP, GPIO.OUT)

############################################
# UTILITY FUNCTIONS
############################################

def step(pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.0005)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.0005)

def slew_steps(step_pin, dir_pin, steps):
    if steps == 0:
        return
    GPIO.output(dir_pin, GPIO.HIGH if steps > 0 else GPIO.LOW)
    for _ in range(abs(steps)):
        step(step_pin)

############################################
# ASTRONOMY HELPERS
############################################

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

############################################
# COORDINATE CONVERSION FOR EQUATORIAL MOUNT
############################################

def hour_angle(lst_hours, ra_hours):
    H = (lst_hours - ra_hours) % 24
    return H * 15.0  # degrees

############################################
# MAIN
############################################

RA_in  = float(input("Enter RA (hours): "))
DEC_in = float(input("Enter DEC (degrees): "))

# Initial positioning: convert DEC (straightforward)
dec_target_deg = DEC_in
dec_target_steps = int(dec_target_deg * STEPS_PER_DEGREE)

print("Slewing DEC...")
slew_steps(DEC_STEP, DEC_DIR, dec_target_steps)
print("DEC positioned.")

############################################
# RA SLEW TO TARGET
############################################

LST = get_LST(LONGITUDE)
H_deg = hour_angle(LST, RA_in)   # Hour angle in degrees

# RA 0° = meridian; east is positive direction
ra_target_steps = int(H_deg * STEPS_PER_DEGREE)

print("Slewing RA to starting position...")
slew_steps(RA_STEP, RA_DIR, ra_target_steps)
print("RA positioned.")

############################################
# TRACKING LOOP
############################################

print("Tracking started. Press Ctrl+C to exit.")

try:
    accumulator = 0.0
    while True:
        accumulator += SIDEREAL_STEPS_PER_SEC
        if accumulator >= 1.0:
            step(RA_STEP)
            accumulator -= 1.0
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopping tracking.")
    GPIO.cleanup()