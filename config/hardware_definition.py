
from pyControl.utility import *
from devices import *

board = Breakout_dseries_1_6()

# Instantiate Devices.

motionSensor = MotionDetector_2ch(name='MotSen',event='motion',
                                  reset=board.port_1.DIO_C,
                                  CS1=board.port_2.DIO_A,
                                  CS2=board.port_2.DIO_B,
                                  calib_coef=0.8, threshold=1, sampling_rate=100)  

#odourDelivery = ParallelOdourRelease()

#lickometer = Lickometer(port=board.port_6, rising_event_A='lick', falling_event_A='lick_off',
#                        rising_event_B='_lick_2___', falling_event_B='_lick_2_off___', debounce=5)

#rewardSol = lickometer.SOL_1  # has two methods: on() and off()

#speaker = Audio_board(board.port_7)

# camera
#triggerCamera = TriggerCamera(pin=board.port_3.DIO_A, duty_cycle=50, trigger_rate=200)
#triggerCamera = TriggerCamera(trigger_rate=30, pin = board.port_3.DIO_A, timer_ID=4)