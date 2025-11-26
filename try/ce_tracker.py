# Programme written by Nigel Quayle
# NOTE: This program cannot be run from IDLE, it must be run from the command line
# NOTE: The Arduino monitor must NOT be open when starting this program

# Ensure Sellarium is set to "Use decimal degrees" under Tools
# Select object and dispay RA/DEC coorindinates on screen
# Calculate ALT AZ coordinates from RA and DEC
# Convert RA and DEC to steps for stepper motor controller
# Ensure the timeout routine is installed: pip3 install inputimeout
# Ensure pyserial is installed: pip3 install pyserial

import datetime, time, math, sys, select, serial
import RPi.GPIO as GPIO


XDIR = 22      # Direction pin
ZDIR = 9
XSTEP =  27    # Step pin
ZSTEP = 10

LAT = -16.8233 
LONG = 145.6881

STEPS_PER_DEGREE = 35.6 # ??

# RA = Right Ascension = the BIG outer ring
def move_steps_ALT(
    num_steps,
    direction=1,
    step_delay=0.001  # 1ms per step ≈ 1000 steps/sec
):
    """Move the motor by num_steps in given direction (1 = fwd, 0 = back)."""
    print(f'Moving {num_steps=} in {direction=} with {step_delay=}')
    GPIO.output(XDIR, GPIO.HIGH if direction == 1 else GPIO.LOW)

    for _ in range(num_steps):
        GPIO.output(XSTEP, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(XSTEP, GPIO.LOW)
        time.sleep(step_delay)

# DEC = Declination = the SMALL inner ring / camera platform
def move_steps_AZ(
    num_steps,
    direction=1,
    step_delay=0.001  # 1ms per step ≈ 1000 steps/sec
):
    """Move the motor by num_steps in given direction (1 = fwd, 0 = back)."""
    print(f'Moving {num_steps=} in {direction=} with {step_delay=}')
    GPIO.output(ZDIR, GPIO.HIGH if direction == 1 else GPIO.LOW)

    for _ in range(num_steps):
        GPIO.output(ZSTEP, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(ZSTEP, GPIO.LOW)
        time.sleep(step_delay)

# Monitor keyboard interrupt to halt tracking and return to home position
def monitor():
    i, o, e = select.select( [sys.stdin], [], [], 5 )
    if (i):
        r = sys.stdin.readline().strip()
        if r == 'c':
            loop = 0
            RTZ (RTZ_ALTsteps, RTZ_AZsteps)
            sys.exit()

# Define function to return stepper motors to home position
def RTZ (RTZ_ALTsteps, RTZ_AZsteps):
    print ('Interrupt...Returning to Home position')
    # Convert total number of Alt steps to  negative numbers
    RTZ_ALTsteps = -RTZ_ALTsteps
    RTZ_AZsteps = -RTZ_AZsteps

    # Convert to strings for communication - add "A" for alt or "Z" for az and add LF for Arduino + "\n"
    ALTsteps = "A" + str(RTZ_ALTsteps)[0:6]+ "\n"
    AZsteps = "Z" + str(RTZ_AZsteps)[0:6]+ "\n"
    # Encode and send data via USB serial communications
    # ser.write(str(ALTsteps).encode('ascii'))
    # ser.write(str(AZsteps).encode('ascii'))
    move_steps_ALT(abs(RTZ_ALTsteps), 1 if RTZ_ALTsteps > 0 else 0)
    move_steps_AZ(abs(RTZ_AZsteps), 1 if RTZ_AZsteps > 0 else 0)
    print(ALTsteps, AZsteps)

# Enter Stellarium RA/DEC
RAinput = input('Enter RA: ')
DECinput = input('Enter DEC: ')
print ()
print ('Tracking Initiated:')
print ()
print ('Enter c to cancel tracking and return to home position')

# Set initial stepper motors positioning to 0 - pointing North at 0 degrees elevation
InitALTsteps = 0
InitAZsteps = 0

# Set Alt and Az position to zero for return to zero position
RTZ_ALTsteps = 0
RTZ_AZsteps = 0

# Set E/W hemisphere parameter
hemi = ''

# Generate and update Alt and Az
loop=1
while loop>=1:
    RA = float(RAinput)
    DEC = float(DECinput)

    # Get current date and local time
    dt = datetime.datetime.today()

    # Split TD into individual variables for month, day, etc. and convert to floats:
    MM = float(dt.month)
    DD = float(dt.day)
    YY = float(dt.year)
    hh = float(dt.hour)
    mm = float(dt.minute)
    ss = float(dt.second)
    # Convert mm to fractional time:
    mm = mm/60 + ss/3600
    # Calculate UTC time as fractional hours:
    LocalTime = hh+mm
    UT = LocalTime-10
    if UT < 0:
        UT = UT+24
        DD = DD-1

    # Calculate the Julian date:
    JD = (367*YY) - int((7*(YY+int((MM+9)/12)))/4) + int((275*MM)/9) + DD + 1721013.5 + (UT/24)
    # Calculate the Greenwhich mean sidereal time:
    GMST = 18.697374558 + 24.06570982441908*(JD - 2451545)
    GMST = GMST % 24    # Use modulo operator to convert to 24 hours
    # Convert to the local sidereal time by adding the longitude (in hours) to the GMST.
    # Convert longitude to hours
    LONG = LONG/15
    LST = GMST+LONG     # If negative we want to add 24...
    if LST < 0:
        LST = LST +24
    LSTmm = (LST - int(LST))*60
    LSTss = (LSTmm - int(LSTmm))*60
    LSThh = int(LST)
    LSTmm = int(LSTmm)
    LSTss = int(LSTss)
    #print ('Local Sidereal Time: ', LSThh, LSTmm, LSTss)

    # Calculate Local Siderial Time in Degrees
    LST = LST*15
    while LST >= 360:
        LST = LST - 360

    # Calculate Hour Angle
    HA = LST - RA
    if HA <0 :
        HA = HA+360

    # HA and DEC to ALT and AZ
    # Convert degrees to radians for maths library
    HA  =  math.radians(HA)
    DEC =  math.radians(DEC)
    LAT =  math.radians(LAT)

    SALT = (math.sin(DEC)*math.sin(LAT))+(math.cos(DEC)*math.cos(LAT)*math.cos(HA))
    ALT = math.asin(SALT)

    CAZ = (math.sin(DEC) - (math.sin(ALT)*math.sin(LAT)))/(math.cos(ALT)*math.cos(LAT))
    AZ = math.acos(CAZ)

    ALT = math.degrees(ALT)
    AZ = math.degrees(AZ)
    if math.sin(HA) >0:
        AZ = 360 - AZ

    # Correct for crossing the zero azimuth
    if AZ <=180:
        hemi = 'E'
    if hemi == 'E' and AZ >180:
        AZ = AZ-360

    print ('Az : Alt : ', AZ, ALT)

    # Stepper motors are driving a 60:1 worm gear, so calculate steps/revolution of the gear
    # Convert degrees to integer steps for stepper motor - 1 degree = 33.3 steps or 12000/360
    # This is the absolute number of steps from zero
    newALTsteps = int(round(ALT*STEPS_PER_DEGREE))
    newAZsteps = int(round(AZ*STEPS_PER_DEGREE))

    # Arduino stepper motor controller uses the AccelStepper library for absolute positioning
    # Only calculate the differential number of steps between iterations to reposition the stepper motors
    ALTsteps = newALTsteps - InitALTsteps
    AZsteps = newAZsteps - InitAZsteps

    # Remember all steps for return to zero position
    RTZ_ALTsteps = RTZ_ALTsteps + ALTsteps
    RTZ_AZsteps = RTZ_AZsteps + AZsteps

    # Save current absolute position for next iteration to calcualte the differential steps
    InitALTsteps = newALTsteps
    InitAZsteps = newAZsteps

    # Convert to strings for communication - add "A" for alt or "Z" for az and add LF for Arduino + "\n"
    # ALTsteps = "A" + str(ALTsteps)[0:6]+ "\n"
    # AZsteps = "Z" + str(AZsteps)[0:6]+ "\n"

    # Encode and send data via USB serial communications
    # ser.write(str(ALTsteps).encode('ascii'))
    # ser.write(str(AZsteps).encode('ascii'))
    move_steps_ALT(abs(ALTsteps), 1 if ALTsteps > 0 else 0)
    move_steps_AZ(abs(AZsteps), 1 if AZsteps > 0 else 0)
    time.sleep(0.1)
    # Monitor interrupt to halt tracking and return to home position 
    monitor()

    # If altitude reaches 0 degrees return stepper motors to home position and halt program
    if ALT <= 0:
        loop = 0
        RTZ (RTZ_ALTsteps, RTZ_AZsteps)
        sys.exit('Altitude = 0 degrees - Horizon reached...')

