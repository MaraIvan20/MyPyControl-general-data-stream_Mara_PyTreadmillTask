from pyControl.utility import *
import hardware_definition as hw
from devices import *
import math
import uarray


board = Breakout_dseries_1_6()

# Instantiate Devices.

motionSensor = MotionDetector_2ch(name='MotSen', event='motion',
                                  reset=board.port_1.DIO_C,
                                  CS1=board.port_2.DIO_A,
                                  CS2=board.port_2.DIO_B,
                                  calib_coef=0.8, threshold=1, sampling_rate=100)

# -------------------------------------------------------------------------
# States and events.
# -------------------------------------------------------------------------

states = ['intertrial']

events = ['motion',
          'session_timer']

initial_state = 'intertrial'

# -------------------------------------------------------------------------
# Variables.
# -------------------------------------------------------------------------

# session params
v.session_duration = 1 * minute
v.c = 0

# Run start and stop behaviour.
def run_start():
    # Code here is executed when the framework starts running.
    set_timer('session_timer', v.session_duration, True)
    motionSensor.record()
    
    print('internal th={}'.format(motionSensor._threshold))
    print('external th={}'.format(motionSensor.threshold))
    print('CPI={}'.format(motionSensor.sensor_x.CPI))


def run_end():
    # Code here is executed when the framework stops running.
    # Turn off all hardware outputs.
    motionSensor.off()
    


# State behaviour functions.
def intertrial(event):
    pass


# State independent behaviour.
def all_states(event):
    # Code here will be executed when any event occurs,
    # irrespective of the state the machine is in.
    if event == 'motion':
        # read the motion registers and and append the variables
        v.c += 1
        print(v.c)
        #print('dX={}'.format(hw.motionSensor.x / hw.motionSensor.sensor_x.CPI * 2.54,))

    elif event == 'session_timer':
        motionSensor.stop()
        stop_framework()
