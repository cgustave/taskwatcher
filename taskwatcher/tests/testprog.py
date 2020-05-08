#!/usr/bin/python3
# simple testing program opening a feedback file

import argparse
import time
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
            log.error("scenario required")
            raise SystemExit
        elif self.scenario == "sleeping":
            self.sleeping()
        elif self.scenario == "feedbacking":
            self.feedbacking()
        else:
            log.error("Unknown scenario {}".format(self.scenario))
            raise SystemExit

        log.debug("End of testprog scenario {}".format(self.scenario))
        raise SystemExit


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
            log.error("feedback file expected")
            raise SystemExit

        if not self.textfile:
            log.error("textfile required")
            raise SystemExit

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

        except:
            log.debug("could not open textfile {}".format(self.texfile))
            raise SystemExit

        try:
            f = open(self.feedback,"w")
            for line in self._FSRC:
                log.debug("writing feedback line: {}".format(line))
                f.write(line)
                #f.write("\n")
                f.flush()
                time.sleep(delay)
            f.close
        except:
            log.debug("could not write feedback file {}".format(self.feedback))
            raise SystemExit

if __name__ == '__main__': #pragma: no cover
    parser = argparse.ArgumentParser(description='Test program from taskwatcher suite.')
    parser.add_argument('--feedback', help="feedback file")
    parser.add_argument('--scenario', help="test behavior", choices=['sleeping', 'feedbacking'], required=True)
    parser.add_argument('--textfile', help="file to use as feedback" )

    parser.add_argument('--sleep', help="sleep time")
    parser.add_argument('--delay', help="delay in scenario")
    parser.add_argument('--debug', help="debugging messages on", action="store_true")
    args = parser.parse_args()

    tpg = Testprog(scenario=args.scenario, feedback=args.feedback,
                   textfile=args.textfile, sleep=args.sleep,
                   delay=args.delay, debug=args.debug)
    tpg.run()
