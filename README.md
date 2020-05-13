## taskwatcher

#### DESCRIPTION

**'taskwatcher'** is a set of libraries/commands to turn scripts/programs into **tasks** :

- **launch.py**  : Starts a new task under taskwatcher monitoring
- **control.py** : General control commands
- **parse.py**   : Feedback file parser, returns a json string from the feedback file

An **history** of the terminated tasks is kept.  
A **status** of the currently running tasks is available.

Tasks are **monitored** by checking if pid is still in process list.
Optionally, if feedback is provided by the launched program, program is expected to provide *heartbeat* by updating the feedback file.  

An optional **task timeout** may terminated the task if no hearbeat was received during the allowed 'timeout' period.  

There are conditions applies so a task can start, multiple scenario :

1) Task does not provide feedack, can run multiple time:
- no control need, a call to lauch would be enough, task would be automatically reserved and launched

2) Task does not provide feeback but only one of this kind should work at a given timer:
- a reservation with a task name and option --unique set should be done befor calling launch. A taskid would be returned, use this task id in call to lauch.

3) Task provides feeback.
- Reservation is required prior calling launch.  
- If task should only run once, use --unique option during reservation.  

Prior to any launch call to start a new task, a taskid (number) should have been reserved with a call control.py --reserve.

A feedback file is a simple text file with key/value pairs. It can be parsed with parse.py to return a json formated string.


###### Limitations

- Currently only supports mono-process program (track a single pid)


#### Design

Choice was made to avoid complex sockets operations.
Simple design with feedback files also allows simple state recovery, simplicity and versatility of the feedback parameters.
A basic file-based sqlite database is used to store running tasks data and keep track of historical tasks, instead of implementing a daemon.


#### Configuration

- Currently no configuration file is implemented. All options should be provided using cli options.
- No centralized daemon: 
	- a launcher is started with the program to run
	- getting feeback from the running task can be done by calling control.py with command 'feedback'
	- history and current status of running tasks are located in sqlite db


#### Expectation from the launched command

A command may be ran without specific requirement, however to benefit from additional features, the run command may provide feedback via a text file.  
The suggestion is to add to programs launched with taskwatcher a command line option (--feedback) to generate the **feedback** file.  
The feedback file is expected to be named based on the taskid : feedback_TASKID.log
Example :  

- Call without taskwatcher :  
	`checkitbaby.py --playbook myPlaybook --playlist myPlaylist --run 1 --dryrun`

- Same call with taskwatcher :  
	- Get a taskid : `control.py --reserve`  ==> Got 1
	- Launch task using taskid 1 :  
	`launch.py --taskid 1 --name 'Runner' --feedpath /fortipoc/playbooks/myPlaybook/run/1 --db /fortipoc/taskwatch/sqlite.db --timeout 30 -- checkitbaby.py --playbook myPlaybook --playlist myPlaylist --run 1 --dryrun --feedback feedback_1.log`

	Notes : 
	- the command to run is located after the --
	- called program is informed with --feedback feedback_1.log that it should write a feedback file named feedback_1.log


##### Running task status

- **without feedback :**
	- **running**    : pid of the task is seen

- **with feedback :** 

	- **running**    : pid of the task is seen,  
		               last feedback file update was done in less than 25% of timeout timer
	
	- **silent**     : pid of the task is seen,  
		               last feedback file update was done in less than 50% of timeout timer
 
	- **stalled**    : pid of the task is seen,  
	                   last feedback file update was done in less than 75% of timeout timer

###### Feedback file syntax

The feedback file is named 'feedback.log', it should be generated by the launched program.
Any kind of usefull information could be delivered as long as :
- it is key/value pair
- line starts with a keywork emcompassed with [] to specify the information keyword.
- keyword should have no spaces and should not start with a digit
- value provided should immediately follow the [keyword] without spaces
- line starting with # are considered comments/debug and will be ignored
- empty lignes will be ignored
- a keyword without any value on a line clears the keyword and value information from the feedback
- [] (without keyword) clears all key/value pairs collected up to this point.
  Note : this could be usefull to end the task with a clear followed by a report.


###### Feedback file processing

- launch.py does not parse feedback file. It only checks the file update from the file update time for the task timeout fonction.
- control.py processed feedback file to provide output.  
  The last read value for a keyword updates any precedent values.  
- use parse.py to parse and retrieve json from the feedback file.  

- Example of a feedback.log
~~~
[info]Starting test
[playbook]myPlaybook
[info]
[heartbeat]
[testcase_id]001
[testcase_name]Initialization
[progress]12
[progress]15
[testcase_id]002
[testcase_name]Setting up topology
[progress]10
~~~

- If processed until this point, the above output would provide information like:
```json
{ 
  "playbook"      : "myPlaybook",
  "testcase_id"   : "002",
  "testcase_name" : "Setting up topology",
  "progress"      : "10"
}
```
Notes :  
- 'info' is not provided because it was cleared by the '[info]' line in line 3
- 'heartbeat' has no information, it would only reset the 'timeout' counter


#### launch.py

```tex
Roles : 
   - launches command
   - monitor the command checking its pid in process list
   - monitor activity of the feedback file (by its update timing information)
   - kills command if not updating feedback file within the timeout 
   - update the running task db about process state, duration and timer status
   - manage task termination : archive task on database, delete feedback file

Pre-requisite :
A unique taskid should have been reserved from a call to control.py to avoid duplicates.
If no reservation was made, the task won't start

Usage : launch.py --db <database> --taskid <taskid> --command '<process or script with all its options>'

Parameters :
--db       <database>     : sqlite database file
--taskid   <taskid>       : task identifier (could be a number or a generated random string (8 chars max)    

Optional parameters :  
--name     <name>         : Name for the task. Use command name if not provided
--feedpath <path>         : Feedback path where feedback.log is expected
--timeout  <seconds>      : a value in second after which the command is considered timeout
				            and should be kill (any update in feedback.log resets the timer)
```

#### control.py

```tex
Roles :
   - Provide list of all running tasks with their latests status
   - Provide history of terminated tasks
   - Provide all latests feedback information from the task
   - Manage history
   - Kill task (and cleanup feedback file if necessary)
   - Initialise (or re-initialize db)
   - Set a reservation for a task id
   
Usage : control.py --db <database> <command>

Options :
--db <database>      : sqlite database file

List of available commands :

--initialize         : Create or recreates a task database (all info is lost)

--update             : Update database time informations (task duration)

--list               : Provides a table displaying the list of the currently running tasks with : 
                       [ taskid, name, pid, status, starttime, duration(s), feedback(yes/no), timer(s), timeout(s) ]

--reserve            : Returns a unique taskid, reserved for future call of the launcher

--feedback <taskid>  : Returns a json formatted output of the feedback values for the given task
                     : Only available if the command provides feedback (feedback=yes in list)

--history            : Dump all historical tasks completed
--clear              : Clear all tasks history

--kill <taskid>      : Request to terminate a specific task
--killall <taskname> : Request to terminate all tasks named <taskname>

```

#### parse.py

```tex
usage: parse.py [-h] [--debug] --feedback filename

Task controller

optional arguments:
  -h, --help           show this help message and exit
  --debug, -d          turn on debug
  --feedback filename  selects feedback file to process


Example: 
 ./parse.py --feedback tests/textfile_progress.txt
 {\"progress\": \"100\"}
```


### sqlite database

An sqlite database is used for 3 purposes :

- keep track of the current running tasks :  
  Launcher.py updates tasks status but does not process feedback

- keep track of the latest feedback from the launched command  
  control.py called with --feedback parses command feedback file, stores information and returns a json object

- keep an history of the previously completed tasks  
  control.py called with --history


**Table format**

```tex
* Table tasks:
  Keeps track of running tasks status
  ------------------------------------------------------------------------------------------------------------------------------------------
  |       id(#1)        |  name |    pid   |   status   |   feedback    |  reservetime |   starttime   | duration |  lastupdate  | timeout |
  | INTEGER PRIMARY KEY |  TEXT |  INTEGER |  TEXT(#2)  |  INTEGER(#3)  |  INTEGER(#4) |   INTEGER(#4) | INTEGER  |  INTEGER(#4) | INTEGER |
  ------------------------------------------------------------------------------------------------------------------------------------------

  Note : 
    #1 : should be automatic (use null during insert)
    #2 : RESERVED|RUNNING|SILENT|STALLED
    #3 : 0 if no feedback provided ; 1 if feedback provided
    #4 : unix date format

  taskid reservation consists of inserting a new task with all field empty, except status=RESERVED and reservetime set

* Table feedbacks:
  Keeps track of data feebacks from the run command, stored as json key/value pairs
  ---------------------------------------
  |    id   | feedback  |   lastupdate  |
  | INTEGER |  BLOB(#1) |   INTEGER(#2) |
  ---------------------------------------

  Note :
  #1 : json format expected
  #2 : unix date format


* Table history:
  Keeps track of the completed tasks
  Final state of json feedback is stored (this allows to store json reports before the command terminates)
  -------------------------------------------------------------------------------------------------------------------------------
  |       id(#0)        |  taskid(#1)  | taskname | termsignal | termerror |   starttime   |   endtime   | duration | feedback  | 
  | INTEGER PRIMARY KEY |   INTEGER    |   TEXT   |  TEXT(#1)  |  TEXT(#2) |   INTEGER(#3) | INTEGER(#3) | INTEGER  |  BLOB(#4) |
  -------------------------------------------------------------------------------------------------------------------------------

  Notes :
  #1 : keeps track of the type of termination signal
  #2 : keeps track of the terminaison error message if any
  #3 : unix date format
  #4 : json format expected

```



