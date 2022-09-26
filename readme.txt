From the original pyControl interface:

pyControl is a system of software and hardware for controlling behavioural experiments based around the Micropython microcontroller.

For more information please see the Docs: http://pycontrol.readthedocs.io/

Repository contents:

gui              : Graphical user interface (adapted such that we can run the treadmill task gui from the original gui)
gui_treadmilltask: Graphical user interface specific for the treadmill task (my work)
com              : Serial communication and data logging
config           : Configuration files edited by user
data             : Behavioural data.
experiments      : Experiment definition files.
devices          : pyControl hardware classes (uploaded to pyboard).
pyControl        : pyControl framework        (uploaded to pyboard).
tasks            : Task definition files
tools            : Tools for importing and visualising pycontrol data
pyControl_GUI.py : Python script to launch the GUI.

Version: v1.6.2
---------------



My work:

I adapted the original pyControl GUI to be able to show the trajectory plot and a reward/penalty barchart for the PyTreadmillTask.py;
In the treadmill task a mouse will be placed on a spherical treadmill and will be trained to execute a series of locomotion tasks while we deliver perturbations to the treadmill (behavioural component); mouse's brain activity will be recorded during the task to correlate behaviour with neurons firing patterns with the final goal of improving brain-computer interfaces; 
The goal of the treamill task gui is to display meaningful real-time data related to the behavioural part of the experiment;
What I added can be found in the gui_treadmilltask folder; 
Additionally, some files in the gui folder and the PyTreadmillTask.py were modified, see comments #NEW!.

