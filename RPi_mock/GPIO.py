import sys

XDIR = 22      # Direction pin
ZDIR = 9
XSTEP =  27    # Step pin
ZSTEP = 10

OUT = 'OUT'
BCM = 'BCM'
LOW = 'LOW'
HIGH = 'HIGH'

def setup(pin, io_dir):
    print(f'GPIO setup {pin=} {io_dir=}')

def setmode(mode):
    print(f'GPIO setmode {mode}')

def output(pin, value):
    if pin in [XSTEP, ZSTEP]:
        # sys.stdout.flush()
        # char = {HIGH: '-', LOW:'_'}[value]
        # sys.stdout.write(char)
        # sys.stdout.flush()
        pass
    # print(f'GPIO output {pin=} {value=}')

def cleanup():
    print(f'\n\ncleanup')



