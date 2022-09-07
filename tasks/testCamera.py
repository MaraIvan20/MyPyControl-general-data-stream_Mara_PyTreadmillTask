# Camera test

from pyControl.utility import *
import hardware_definition as hw

# -------------------------------------------------------------------------
# States and events.
# -------------------------------------------------------------------------

states = ['intertrial']

events = ['session_timer']

initial_state = 'intertrial'

# -------------------------------------------------------------------------
# Variables.
# -------------------------------------------------------------------------

# session params
v.session_duration = 100 * second

#-------------------------------------------------------------------------        
# State machine code.
#-------------------------------------------------------------------------

# Run start and stop behaviour.
def run_start():
    # Code here is executed when the framework starts running.
    set_timer('session_timer', v.session_duration, True)
    hw.triggerCamera.start()
    print('starting test')

def run_end():
    # Code here is executed when the framework stops running.
    # Turn off all hardware outputs.
    hw.off()

# State behaviour functions.
def intertrial(event):
    pass

# State independent behaviour.
def all_states(event):
    # Code here will be executed when any event occurs,
    # irrespective of the state the machine is in.
    if event == 'session_timer':
        hw.triggerCamera.off()
        stop_framework()