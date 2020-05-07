Help on module control:

NAME
    control

DESCRIPTION
    Created on May 7th, 2020
    @author: cgustave
    
    controller from the taskwatcher suite

CLASSES
    builtins.object
        Control
    
    class Control(builtins.object)
     |  Control(db='', debug=False)
     |  
     |  Controller from the taskwatcher suite
     |  Called with db
     |  
     |  Methods defined here:
     |  
     |  __init__(self, db='', debug=False)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  initialize(self)
     |      Initializes a database
     |  
     |  print_tasks(self)
     |      Prints a human formatted listing of the current tasks
     |  
     |  reserve(self)
     |      Reserve a free taskid and return it
     |      Should be called before a task can be created
     |  
     |  return_tasks(self)
     |      Returns a dictionary listing the current tasks
     |  
     |  update(self)
     |      Update database timing information like tasks duration
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FILE
    /home/cgustave/github/python/packages/taskwatcher/taskwatcher/control.py


