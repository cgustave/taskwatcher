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
     |  Launch(taskid='', db='', name='', info1='', info2='', info3='', feedpath=None, timeout=30, debug=False)
     |  
     |  Launcher from taskwatcher suite
     |  Called with taskid, db
     |  Optional : name, feedpath, timeout
     |  Requirement : a taskid should have been reserved
     |  
     |  Methods defined here:
     |  
     |  __init__(self, taskid='', db='', name='', info1='', info2='', info3='', feedpath=None, timeout=30, debug=False)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  child(self, command='')
     |      Child code after fork
     |  
     |  clear_to_start_task(self)
     |      Returns True if task if clear to be started
     |      This mean taskid has is known in reserve status
     |  
     |  execute(self, command='')
     |      Execute provided command in a child process
     |      If program is expected to feedback, it should have an option --feedback
     |      to provide feedback file name.
     |      If feedback is expected, a reservation is required (so feedback file is
     |      determined for both contol and launched program
     |  
     |  father_check_child_health(self)
     |      Returns True if child is alive
     |      If childs provide feedback, check the heartbeat   
     |      Heartbeat should be checked from feedback file update time
     |  
     |  father_checks_child_feedback_ok(self)
     |      If process is supposed to feedback,
     |      check if it updates feedbackfile in time
     |  
     |  father_checks_child_process_status_ok(self)
     |      Check process pid is known and child is not a zombie
     |  
     |  father_loop(self)
     |      Father code after fork
     |  
     |  updatefile_name(self)
     |      Returns the expected task update file name from taskid and feedpath
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


