import RPi.GPIO as GPIO
import contextlib
import time



# GPIO pins
XDIR = 22      # Direction pin
ZDIR = 9
XSTEP =  27    # Step pin
ZSTEP = 10

def setup():
    print('setup init')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(XDIR, GPIO.OUT)
    GPIO.setup(XSTEP, GPIO.OUT)
    GPIO.setup(ZDIR, GPIO.OUT)
    GPIO.setup(ZSTEP, GPIO.OUT)
    print('setup complete')

def move_steps(
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
    print('')

def teardown():
    GPIO.cleanup()

@contextlib.contextmanager
def env():
    setup()
    try:
        yield
    finally:
        teardown()