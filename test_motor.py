import RPi.GPIO as GPIO
import time

# GPIO pins
XDIR = 22      # Direction pin
ZDIR = 9
XSTEP =  27    # Step pin
ZSTEP = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(XDIR, GPIO.OUT)
GPIO.setup(XSTEP, GPIO.OUT)
GPIO.setup(ZDIR, GPIO.OUT)
GPIO.setup(ZSTEP, GPIO.OUT)


# Tune this for speed (seconds)
step_delay = 0.001  # 1ms per step ≈ 1000 steps/sec


def move_steps(num_steps, direction=1):
    """Move the motor by num_steps in given direction (1 = fwd, 0 = back)."""
    GPIO.output(XDIR, GPIO.HIGH if direction == 1 else GPIO.LOW)

    for _ in range(num_steps):
        GPIO.output(XSTEP, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(XSTEP, GPIO.LOW)
        time.sleep(step_delay)


try:
    print("Forward 200 steps")
    move_steps(200, direction=1)
    time.sleep(1)

    print("Backward 200 steps")
    move_steps(200, direction=0)
    time.sleep(1)

finally:
    GPIO.cleanup()