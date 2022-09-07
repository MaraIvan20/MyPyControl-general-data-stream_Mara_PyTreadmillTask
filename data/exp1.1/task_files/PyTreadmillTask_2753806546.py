# PyTreadmillTask

from pyControl.utility import *
import hardware_definition as hw
from devices import *
import math
import uarray

# -------------------------------------------------------------------------
# States and events.
# -------------------------------------------------------------------------

states = ['intertrial',
          'trial_start',
          'odour_release',
          'reward',
          'penalty']

events = ['motion',
          'lick',
          'lick_off',
          'session_timer',
          'IT_timer',
          'odour_timer',
          'reward_timer'
          ]

initial_state = 'intertrial'

# -------------------------------------------------------------------------
# Variables.
# -------------------------------------------------------------------------

# general parameters
v.target_angle___ = {0: 5 * math.pi / 6,
                     1: 2 * math.pi / 3,
                     2: math.pi / 2,
                     3: math.pi / 3,
                     4: math.pi / 6}

v.audio_f_range___ = (10000, 20000)  # between 10kHz and 20kHz, loosely based on Heffner & Heffner 2007

v.CPI_x=hw.motionSensor.sensor_x.CPI  #NEW! used to convert to cm in the trajectory plot
v.CPI_y=hw.motionSensor.sensor_y.CPI   #NEW! used to convert to sm in the trajectory plot

# session params
v.session_duration = 1 * hour
v.reward_duration = 100 * ms
v.penalty_duration = 10 * second
v.trial_number = 0

# intertrial params
v.min_IT_movement = 10  # cm - must be a multiple of 5
v.min_IT_duration = 1 * second
v.IT_duration_done___ = False
v.IT_distance_done___ = False
v.x___ = 0
v.y___ = 0

# trial params
v.max_odour_time = 10 * second
v.distance_to_target = 20  # cm - must be a multiple of 5
v.target_angle_tolerance = math.pi / 18  # deg_rad
v.odourant_direction = -1
v.air_off_duration = 100 * ms

# -------------------------------------------------------------------------
# State-independent Code
# -------------------------------------------------------------------------


def release_single_odourant_random(odourDevice: ParallelOdourRelease):
    """
    Releases 1 odourant at a random direction
    """
    stimDir = randint(0, odourDevice.Ndirections - 1)
    odourDevice.all_off()
    odourDevice.odour_release(stimDir)

    print('{}, odourant_direction'.format(stimDir))

    return stimDir


def arrived_to_target(dX: float, dY: float,
                      odourant_direction: int,
                      target_angle_tolerance: float):
    """
    checks the motion critereon
    MUST have 5 odour directions
    """
    assert odourant_direction < 5, 'wrong direction value'

    move_angle = math.atan2(dY, dX)
    if abs(move_angle - v.target_angle___[odourant_direction]) < target_angle_tolerance:
        return True
    else:
        return False


def audio_mapping(d_a: float) -> float:
    """
    freq = (-10kHz/300)d_a + 15kHz
    """
    return mean(v.audio_f_range___) - (v.audio_f_range___[0] * d_a / v.target_angle___[0] * 2)


def audio_feedback(speaker,
                   dX: float, dY: float,
                   odourant_direction: int):
    angle = math.atan2(dY, dX)
    audio_freq = audio_mapping(angle - v.target_angle___[odourant_direction])
    speaker.sine(audio_freq)


# -------------------------------------------------------------------------
# Define behaviour.
# -------------------------------------------------------------------------


# Run start and stop behaviour.
def run_start():
    # Code here is executed when the framework starts running.
    set_timer('session_timer', v.session_duration, True)
    hw.motionSensor.power_up()
    hw.speaker.set_volume(90)
    hw.speaker.off()
    hw.odourDelivery.clean_air_on()


def run_end():
    # Code here is executed when the framework stops running.
    # Turn off all hardware outputs.
    hw.odourDelivery.all_off()
    hw.rewardSol.off()
    hw.speaker.off()
    hw.motionSensor.shut_down()
    hw.off()


# State behaviour functions.
def intertrial(event):
    if event == 'entry':
        # coded so that at this point, there is clean air coming from every direction
        set_timer('IT_timer', v.min_IT_duration)
        v.IT_duration_done___ = False
        v.IT_distance_done___ = False
        hw.motionSensor.threshold = v.min_IT_movement
    elif event == 'exit':
        disarm_timer('IT_timer')
    elif event == 'IT_timer':
        v.IT_duration_done___ = True
        if v.IT_distance_done___:
            goto_state('trial_start')
    elif event == 'motion':
        v.IT_distance_done___ = True
        if v.IT_duration_done___:
            goto_state('trial_start')


def trial_start(event):
    if event == 'entry':
        v.trial_number += 1
        print('{}, trial_number'.format(v.trial_number))
        hw.odourDelivery.all_off()
        timed_goto_state('odour_release', v.air_off_duration)


def odour_release(event):
    if event == 'entry':
        set_timer('odour_timer', v.max_odour_time)
        v.odourant_direction = release_single_odourant_random(hw.odourDelivery)
        hw.motionSensor.threshold = v.distance_to_target
    elif event == 'exit':
        disarm_timer('odour_timer')
        hw.speaker.off()
    elif event == 'motion':
        arrived = arrived_to_target(v.x___, v.y___,
                                    v.odourant_direction,
                                    v.target_angle_tolerance)

        audio_feedback(hw.speaker, v.x___, v.y___, v.odourant_direction)

        if arrived is True:
            goto_state('reward')
        elif arrived is False:
            goto_state('penalty')
    elif event == 'odour_timer':
        goto_state('penalty')


def reward(event):
    if event == 'entry':
        hw.odourDelivery.clean_air_on()
        set_timer('reward_timer', v.reward_duration, False)
        hw.rewardSol.on()
        print('{}, reward_on'.format(get_current_time()))
    elif event == 'exit':
        disarm_timer('reward_timer')
    elif event == 'reward_timer':
        hw.rewardSol.off()
        goto_state('intertrial')


def penalty(event):
    if event == 'entry':
        hw.odourDelivery.clean_air_on()
        print('{}, penalty_on'.format(get_current_time()))
        timed_goto_state('intertrial', v.penalty_duration)


# State independent behaviour.
def all_states(event):
    # Code here will be executed when any event occurs,
    # irrespective of the state the machine is in.
    if event == 'motion':
        # read the motion registers and and append the variables
        v.x___ = hw.motionSensor.x / hw.motionSensor.sensor.CPI * 2.54
        v.y___ = hw.motionSensor.y / hw.motionSensor.sensor.CPI * 2.54
        print('{},{}, dM'.format(v.x___, v.y___))
    elif event == 'lick':
        # TODO: handle the lick data better
        pass
    elif event == 'session_timer':
        hw.motionSensor.stop()
        stop_framework()
