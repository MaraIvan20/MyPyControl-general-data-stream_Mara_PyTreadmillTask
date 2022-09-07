from pyqtgraph.Qt import QtGui

from gui_treadmill_task.treadmill_plotting import TreadmillTask_plot
from gui_treadmill_task.treadmill_barchart import TreadmillTask_barchart


class Realtime_data_tab(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)

        #Variables
        self.treadmilltask_plot=TreadmillTask_plot()
        self.treadmilltask_barchart=TreadmillTask_barchart()

        #Main layout
        self.vertical_layout=QtGui.QVBoxLayout()
        self.vertical_layout.addWidget(self.treadmilltask_plot,60)
        self.vertical_layout.addWidget(self.treadmilltask_barchart,40)
        self.setLayout(self.vertical_layout)

    def process_data(self, new_data):
        self.treadmilltask_plot.process_data(new_data)
        self.treadmilltask_barchart.process_data(new_data) 

    def set_state_machine(self,sm_info):
        self.treadmilltask_plot.set_state_machine(sm_info)
        self.treadmilltask_barchart.set_state_machine(sm_info)

    def run_start(self, recording):
        self.treadmilltask_plot.run_start(recording)
        self.treadmilltask_barchart.run_start()

    def run_stop(self):
        self.treadmilltask_plot.run_stop()
        self.treadmilltask_barchart.run_stop()


    def update(self):
        self.treadmilltask_plot.update()
        self.treadmilltask_barchart.update()
        
    
