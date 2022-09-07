import time
from datetime import timedelta
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from PyQt5.QtCore import Qt
import numpy as np
import math




class TreadmillTask_plot(QtGui.QWidget): #similar to class Task_plot from gui/plotting.py
    '''Widget for plotting real time data '''

    def __init__(self,parent=None):
        super(QtGui.QWidget,self).__init__(parent)

        #Create widgets
        self.position_plot=Position_plot(self) 
        self.run_clock=Treadmill_run_clock(self.position_plot.axis)

        #Setup plots
        self.pause_button=QtGui.QPushButton('Pause plot and run clock')
        self.pause_button.setEnabled(False)
        self.pause_button.setCheckable(True)

        #create layout
        self.vertical_layout=QtGui.QGridLayout()
        self.vertical_layout.addWidget(self.position_plot.axis,0,0,1,1)
        self.vertical_layout.addWidget(self.pause_button,1,0,1,1,Qt.AlignCenter)
        self.setLayout(self.vertical_layout)



    def set_state_machine(self,sm_info):

        #used to reset the plot and the run clock at the beginning of every trial and intertrial state:
        self.state_IDs = list(sm_info['states'].values()) #used to clear the plot for every trial_start state in process_data below
        self.trial_start_ID=sm_info['states']['trial_start']
        self.intertrial_ID=sm_info['states']['intertrial']

        #Initialise plots with state machine information
        self.position_plot.set_state_machine(sm_info)



    def run_start(self, recording):
        self.pause_button.setChecked(False)
        self.pause_button.setEnabled(True)
        self.start_time=time.time()
        self.position_plot.run_start()
        if recording:
            self.run_clock.recording()

        #used to reset the plot and run clock every trial and intertrial
        self.n_trial=0
        self.n_intertrial=0
        self.trial=False
        self.intertrial=True


    def run_stop(self):
        self.pause_button.setEnabled(False)
        self.run_clock.run_stop()
            

    def process_data(self,new_data):
        '''Store new data from board'''
        self.new_states = [nd for nd in new_data if nd[0] == 'D' and nd[2] in self.state_IDs]
        if self.new_states:
            for ns in self.new_states:
                if ns[2]==self.trial_start_ID:
                    self.position_plot.clear_plot()
                    self.trial_start_time=time.time()
                    self.n_trial+=1
                    self.trial=True
                    self.intertrial=False
                elif ns[2]==self.intertrial_ID:
                    self.position_plot.clear_plot()
                    self.intertrial_start_time=time.time()
                    self.n_intertrial+=1
                    self.trial=False
                    self.intertrial=True

        self.position_plot.process_data(new_data)



    def update(self):
        '''Update plots'''
        if not self.pause_button.isChecked():
            run_time=time.time()-self.start_time

            if self.trial: 
                if self.n_trial==0:
                    self.run_clock.update_trial_clock(run_time,0,0)
                else:
                    trial_time=time.time()-self.trial_start_time
                    self.position_plot.update()
                    self.run_clock.update_trial_clock(run_time, trial_time, self.n_trial)  

            elif self.intertrial:
                if self.n_intertrial==0:
                    self.run_clock.update_intertrial_clock(run_time,0,0)
                else:
                    intertrial_time=time.time()-self.intertrial_start_time
                    self.position_plot.update()
                    self.run_clock.update_intertrial_clock(run_time, intertrial_time, self.n_intertrial)





class Position_plot():  #similar to States_plot(), Events_plot() and Analog_plot() from gui/plotting.py 
    
    def __init__(self,parent=None): 
        self.axis=pg.PlotWidget(title='Trajectory of the mouse (per trial/intertrial)')
        self.axis.showGrid(x=True, y=True)
        self.x=0 #x coordinate
        self.y=0  #y coordinate

        self.axis.setXRange(-30,30) # TO TEST: replace these 2 lines by the 2 lines commented under set_state_machine to set the range based on the distance to target
        self.axis.setYRange(-30,30)

        self.plot1=self.axis.plot(pen=None, symbol='x', symbolSize=20, symbolPen=None, symbolBrush=pg.intColor(0))
        self.axis.addItem(self.plot1)
       

        


    def set_state_machine(self,sm_info):
        self.inputs=sm_info['analog_inputs']
        if not self.inputs: return
        self.axis.clear()
        self.axis.getAxis('bottom').setLabel('X coordinate (cm)')  
        self.axis.getAxis('left').setLabel('Y coordinate (cm)')

        self.ID_x=self.inputs['MotSen-X']['ID']
        self.ID_y=self.inputs['MotSen-Y']['ID']

        self.CPI_x=sm_info['variables']['CPI_x']
        self.CPI_y=sm_info['variables']['CPI_y']
        
        #self.axis.setXRange(-int(sm_info['variables']['distance_to_target']),int(sm_info['variables']['distance_to_target']))  #TO TEST using CPI_x instead of distance_to_target (should be 100)
        #self.axis.setYRange(-int(sm_info['variables']['distance_to_target']),int(sm_info['variables']['distance_to_target']))  #TO TEST 

        

    def run_start(self): 
        if not self.inputs: return
        self.axis.clear()

        
    def process_data(self,new_data):  
        '''Store new data from the board'''
        if not self.inputs:return
        new_analog=[nd for nd in new_data if nd[0]=='A']  #same as in gui/plotting.py, class Analog_plot()
        self.data_x_dict={}  #dictionary:{timestamp: list of x coordinates}
        self.data_y_dict={}  #dictionary:{timestamp: list of y coordinates}

        for na in new_analog:
            ID, sampling_rate, timestamp, data_array = na[1:]
            
            if ID==self.ID_x:
                self.x_list=[]
                for i in data_array:
                    self.x+=i/float(self.CPI_x)*2.54 #conversion to cm
                    self.x_list.append(self.x)  #create a list of incrementally increasing x coordinates
                self.data_x_dict[timestamp]=self.x_list
                
            elif ID==self.ID_y:
                self.y_list=[]
                for i in data_array:
                    self.y+=i/float(self.CPI_y)*2.54 #conversion to cm
                    self.y_list.append(self.y)
                self.data_y_dict[timestamp]=self.y_list


    def clear_plot(self):  
        '''Clear and reset the plot'''
        if not self.inputs:return
        self.axis.clear()

        self.x=0  
        self.y=0

        #used to join the plot as a continuous line:
        self.last_x_point=0  #added for continuous plot
        self.last_y_point=0  #added for continuous plot

        
    def update(self):   
        '''Update plot'''
        if not self.inputs:return
        
        for t in self.data_x_dict.keys():
            for w in self.data_y_dict.keys():
                if t==w:  #search for x and y coordinates with the same timestamp
        
                    if len(self.data_x_dict[t])!=len(self.data_y_dict[t]):
                        #if not already, make sure the x and y coordinates lists corresponding to the same timestamp have the same length
                        #the new length will be the least common multiple of the original lengths of x and y coordinates lists
                        len_x=len(self.data_x_dict[t])
                        len_y=len(self.data_y_dict[t])
                        lcm_xy=math.lcm(len_x,len_y)
                        self.data_x_updated=[]
                        self.data_y_updated=[]
                        for x in self.data_x_dict[t]:
                            self.data_x_updated=self.data_x_updated+[x]*int(lcm_xy/len_x) #create the updated coordinates lists containing repeated coordinates from the old lists to achieve lists of the same length
                        for y in self.data_y_dict[t]:
                            self.data_y_updated=self.data_y_updated+[y]*int(lcm_xy/len_y)

                        #last_x_point and last_y_point used for the continuous line aspect of the plot, by starting the new segment with the last point from the previous segment:
                        self.axis.plot([self.last_x_point]+self.data_x_updated,[self.last_y_point]+self.data_y_updated, pen = pg.mkPen(color=(0, 150, 255), width=3)) #modified for continuous plot
                        #do we also want to show the exact points? use: self.axis.plot([self.last_x_point]+self.data_x_updated,[self.last_y_point]+self.data_y_updated,pen=None, symbol='x', symbolSize=8, symbolPen=None, symbolBrush=pg.intColor(5))
                    else:
                        self.axis.plot([self.last_x_point]+self.data_x_dict[t],[self.last_y_point]+self.data_y_dict[t],  pen = pg.mkPen(color=(0, 150, 255), width=3))  #modified for continuous plot
                        #do we also want to show the exact points? use: self.axis.plot([self.last_x_point]+self.data_x_dict[t],[self.last_y_point]+self.data_y_dict[t],pen=None, symbol='x', symbolSize=8, symbolPen=None, symbolBrush=pg.intColor(5))
                    

                    #needed to join the plot as a continuous line: 
                    self.last_x_point=self.data_x_dict[t][len(self.data_x_dict[t])-1]  #added for continuous plot
                    self.last_y_point=self.data_y_dict[t][len(self.data_y_dict[t])-1]  #added for continuous plot
                    

                    #to update current position of the mouse
                    self.axis.removeItem(self.plot1)
                    self.axis.addItem(self.plot1)
                    self.plot1.setData([self.last_x_point],[self.last_y_point])
        
        




class Treadmill_run_clock(): 
    '''Class for displaying the session time, the trial/intertrial number and the trial/intertrial time'''


    def __init__(self,axis):
        self.clock_text=pg.TextItem(text='')
        self.clock_text.setFont(QtGui.QFont('arial',11,QtGui.QFont.Bold))
        axis.getViewBox().addItem(self.clock_text, ignoreBounds=True)
        self.clock_text.setParentItem(axis.getViewBox())
        self.clock_text.setPos(10,30)  
        self.recording_text=pg.TextItem(text='',color=(255,0,0))
        self.recording_text.setFont(QtGui.QFont('arial',12,QtGui.QFont.Bold))
        axis.getViewBox().addItem(self.recording_text, ignoreBounds=True)
        self.recording_text.setParentItem(axis.getViewBox())
        self.recording_text.setPos(80,-5)

    def update_trial_clock(self, run_time, trial_time, n_trial):  
        self.clock_text.setText('Session time: {}\nTrial number: {}\nTrial time: {}'.format(str(timedelta(seconds=run_time))[:7],n_trial,str(timedelta(seconds=trial_time))[:7])) 

    def update_intertrial_clock(self, run_time, intertrial_time, n_intertrial):
        self.clock_text.setText('Session time: {}\nIntertrial number: {}\nIntertrial time: {}'.format(str(timedelta(seconds=run_time))[:7],n_intertrial,str(timedelta(seconds=intertrial_time))[:7]))

    def recording(self):
        self.recording_text.setText('Recording')

    def run_stop(self):
        self.clock_text.setText('')
        self.recording_text.setText('')
        




    
