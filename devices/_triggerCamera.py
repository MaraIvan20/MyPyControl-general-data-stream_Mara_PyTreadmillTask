import pyb, machine, time
import pyControl.hardware as _h

class TriggerCamera(_h.Digital_output):
    
    def __init__(self, pin, duty_cycle, trigger_rate):
        super().__init__(pin, pulse_enabled=True)
        self.duty_cycle = duty_cycle
        self.trigger_rate = trigger_rate
    
    def start(self):    
        self.pulse(freq=self.trigger_rate, duty_cycle=self.duty_cycle)
