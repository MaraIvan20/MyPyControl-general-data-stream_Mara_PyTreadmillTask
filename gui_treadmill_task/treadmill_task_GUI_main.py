from pyqtgraph.Qt import QtGui

from gui.utility import detachableTabWidget
from gui_treadmill_task.realtime_data_tab import Realtime_data_tab



# --------------------------------------------------------------------------------
# TreadmillTask_GUI_main
# --------------------------------------------------------------------------------


class TreadmillTask_GUI_main(QtGui.QMainWindow):  #class for the treadmill GUI main window that opens from the Run task tab, when pressing 'Start'

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Treadmill Task Behavioural GUI')
        self.setGeometry(720,30,700,800)  #Left, top, width, height

        #Widgets
        self.tab_widget=QtGui.QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        self.realtime_data_tab=Realtime_data_tab(self)
        self.tab_widget.addTab(self.realtime_data_tab,'Real time data')

    def process_data(self,new_data):
        self.realtime_data_tab.process_data(new_data)

    def set_state_machine(self,sm_info):
        self.realtime_data_tab.set_state_machine(sm_info)

    def run_start(self, recording):
        self.realtime_data_tab.run_start(recording)

    def run_stop(self):
        self.realtime_data_tab.run_stop()

    def update(self):
        self.realtime_data_tab.update()






class TreadmillTask_GUI_main_experiment(QtGui.QMainWindow): #class for the treadmill GUI main window that opens from the Run experiment tab, when pressing 'Show plots'
    #similar to the class Experiment_plot from gui/plotting.py
    '''Window for plotting data during experiment run where each subjects plots are displayed in a separate tab.'''

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        self.setWindowTitle('Treadmill Task Experiment Behavioural GUI')
        self.setGeometry(1420,30,500,800)  #Left, top, width, height
        self.subject_tabs = detachableTabWidget(self)
        self.setCentralWidget(self.subject_tabs)
        self.subject_plots = []
        self.active_plots = []

    def setup_experiment(self, experiment):
        '''Create task plotters in separate tabs for each subject.'''
        subject_dict = experiment['subjects']
        subjects = list(experiment['subjects'].keys())
        subjects.sort(key=lambda s: experiment['subjects'][s]['setup'])
        for subject in subjects:
            self.subject_plots.append(Realtime_data_tab(self))
            self.subject_tabs.addTab(self.subject_plots[-1],
                '{} : {}'.format(subject_dict[subject]['setup'], subject))

    def set_state_machine(self, sm_info):
        '''Provide the task plotters with the state machine info.'''
        for subject_plot in self.subject_plots:
            subject_plot.set_state_machine(sm_info)

    def start_experiment(self,rig):
        self.subject_plots[rig].run_start(False)
        self.active_plots.append(rig)

    def close_experiment(self):
        '''Remove and delete all subject plot tabs.'''
        while len(self.subject_plots) > 0:
            subject_plot = self.subject_plots.pop() 
            subject_plot.setParent(None)
            subject_plot.deleteLater()
        self.close()
        
    def update(self):
        '''Update the plots of the active tab.'''
        for i,subject_plot in enumerate(self.subject_plots):
            if not subject_plot.visibleRegion().isEmpty() and i in self.active_plots:
                subject_plot.update()


    
