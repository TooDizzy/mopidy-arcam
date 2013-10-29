'''
Created on 29/10/2013

@author: tue
'''


import logging
import pykka
import time

logger = logging.getLogger('mopidy_arcam')


class ArcamReader(pykka.ThreadingActor):
    """
    Independent reader thread which does the communication with the Arcam amplifier.
    
    """
    _read_lines = ""
    
    def __init__(self):
        super(ArcamReader, self).__init__()
        
    def on_start(self, talker):
        self._arcam_talker = talker
        
        # Let's start reading
        while (True):
            logger.info("Starting to read.")
            self._read_lines = self._arcam_talker.readline()
            if (len(self._read_lines) > 0):
                print "Read: ", self._read_lines
            else:
                print "Nothing yet."
                time.sleep(5)