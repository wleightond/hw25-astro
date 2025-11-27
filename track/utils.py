import RPi.GPIO as GPIO
import contextlib
import time

RA = 'RA'
DEC = 'DEC'

# GPIO pins
XDIR = 22      # Direction pin
ZDIR = 9
XSTEP =  27    # Step pin
ZSTEP = 10

PINS = {
    DEC: (XSTEP, XDIR),
    RA: (ZSTEP, ZDIR),
}

def setup():
    print('setup init')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(XDIR, GPIO.OUT)
    GPIO.setup(XSTEP, GPIO.OUT)
    GPIO.setup(ZDIR, GPIO.OUT)
    GPIO.setup(ZSTEP, GPIO.OUT)
    print('setup complete')

def move_steps(
    axis: str,
    num_steps: int,
    direction: int = 1,
    step_delay: float = 0.0001  # 1ms per step ≈ 1000 steps/sec
):
    step_pin, dir_pin = PINS[axis]
    """Move the motor by num_steps in given direction (1 = fwd, 0 = back)."""
    if num_steps:
        # print(f'Moving {axis=} {num_steps=} in {direction=} with {step_delay=}')
        GPIO.output(dir_pin, GPIO.HIGH if direction == 1 else GPIO.LOW)

        for _ in range(num_steps):
            GPIO.output(step_pin, GPIO.HIGH)
            time.sleep(step_delay)
            GPIO.output(step_pin, GPIO.LOW)
            time.sleep(step_delay)
        # print('')

def teardown():
    GPIO.cleanup()

@contextlib.contextmanager
def env():
    setup()
    try:
        yield
    finally:
        teardown()