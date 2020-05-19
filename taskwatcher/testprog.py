#!/usr/bin/python3
# simple testing program opening a feedback file

import argparse
import time
import sys
import logging as log

class Testprog(object):

    def __init__(self, scenario=None, feedback=None, textfile=None, sleep=None, delay=None, debug=False):
        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-\
            10.10s.%(funcName)-20.20s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        log.info("Constructor with scenario={} feedback={} textfile={} sleep={} delay={} debug={}". 
            format(scenario, feedback, textfile, sleep, delay, debug))

        # Set debug level first
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')
        else:
            self.debug = False
            log.basicConfig(level='ERROR')

        # Attributes
        self.scenario = scenario
        self.feedback = feedback
        self.textfile = textfile
        self.sleep = sleep
        self.delay = delay

        # Private attributes
        self._FSRC = []


    def run(self):
        """
        Starting a scenario
        Required : scenario
        """
        log.info("Enter")

        if not self.scenario:
            sys.exit("scenario required")
        elif self.scenario == "sleeping":
            self.sleeping()
        elif self.scenario == "feedbacking":
            self.feedbacking()
        elif self.scenario == "progressing" :
            self.progressing()
        else:
            sys.exit("Unknown scenario {}".format(self.scenario))

        log.debug("End of testprog scenario {}".format(self.scenario))
        sys.exit()


    def sleeping(self):
        """
        Testing scenario where program sleeps for the given time 
        """
        log.info("Enter")

        sleeptime = 30
        if self.sleep:
            sleeptime = self.sleep

        log.debug("Starting sleeping for {} seconds".format(sleeptime))
        time.sleep(int(sleeptime))
        log.debug("Woke up from sleep")


    def feedbacking(self):
        """
        Testing scenario where program writes feedback :
        - line by line with delay set with delay attribut
        - feedback file used is given by attribut textfile 

        Requires: 
        - delay (1 seconds default)
        - textfile 
        - feedback
        """
        log.info("Enter")
 
        # Sanity
        if not self.feedback:
            sys.exit("--feedback required")

        if not self.textfile:
            sys.exit("--textfile required")

        delay = 1
        if self.delay:
            delay = self.delay

        # Suckin textfile in memory
        self._FSRC = []
        try: 
            fsrc = open(self.textfile,"r")
            for line in fsrc:
                self._FSRC.append(line)
            fsrc.close()
            log.debug("file in memory")
        except:
            sys.exit("could not open textfile {}".format(self.texfile))

            log.debug("open file {}".format(self.feedback))
        try:
            f = open(self.feedback,"w")
        except:
            sys.exit("could not write feedback file {}".format(self.feedback))

        for line in self._FSRC:
            log.debug("writing feedback line: {}".format(line))
            f.write(line)
            f.flush()
            time.sleep(float(delay))

        f.close
        sys.exit()

    def progressing(self):
        """
        Simulation of 2 progress bars : [testcase] and [progress]
        """
        log.info("Enter")

        # Sanity
        if not self.feedback:
            sys.exit("--feedback required")

        delay = 1
        if self.delay:
            delay = self.delay

        try:
            f = open(self.feedback,"w")
        except:
            sys.exit("could not write feedback file {}".format(self.feedback))

        f.write("[playbook]testprogr\n")    
        f.write("[start_time]{}\n".format(int(time.time())))  
        f.write("[run]1\n")
        for ov in range(1,11):
            f.write("[progress]{}\n".format(ov*10))
            f.write("[testcase_id]{}0\n".format(ov))
            f.write("[testcase_name]testcase_nb_0{}\n".format(ov))
            for tc in range(1,101):
                f.write("[testcase_progress]{}\n".format(tc))
                f.flush()
                time.sleep(float(delay))
        f.write("[progress]100\n")
        f.write("[end_time]{}\n".format(int(time.time())))
        f.close
        sys.exit()


    


if __name__ == '__main__': #pragma: no cover
    parser = argparse.ArgumentParser(description='Test program from taskwatcher suite.')
    parser.add_argument('--feedback', help="feedback file")
    parser.add_argument('--scenario', help="test behavior", choices=['sleeping', 'feedbacking', 'progressing'], required=True)
    parser.add_argument('--textfile', help="file to use as feedback" )

    parser.add_argument('--sleep', help="sleep time")
    parser.add_argument('--delay', help="delay in scenario")
    parser.add_argument('--debug', help="debugging messages on", action="store_true")
    args = parser.parse_args()

    tpg = Testprog(scenario=args.scenario, feedback=args.feedback,
                   textfile=args.textfile, sleep=args.sleep,
                   delay=args.delay, debug=args.debug)
    tpg.run()
