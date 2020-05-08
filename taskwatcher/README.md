Help on module launch:

NAME
    launch

DESCRIPTION
    Created on May 6th, 2020
    @author: cgustave
    
    launcher from the taskwatcher suite

CLASSES
    builtins.object
        Launch
    
    class Launch(builtins.object)
     |  Launch(taskid='', db='', name='', feedpath=None, timeout=30, debug=False)
     |  
     |  Launcher from taskwatcher suite
     |  Called with taskid, db
     |  Optional : name, feedpath, timeout
     |  Requirement : a taskid should have been reserved
     |  
     |  Methods defined here:
     |  
     |  __init__(self, taskid='', db='', name='', feedpath=None, timeout=30, debug=False)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  execute(self, command='')
     |      Execute provided command in a child process
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
    /home/cgustave/github/python/packages/taskwatcher/taskwatcher/launch.py


