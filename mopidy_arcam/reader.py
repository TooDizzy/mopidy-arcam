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
    
    def __init__(self, talker):
        super(ArcamReader, self).__init__()
        
        self._arcam_talker = talker
        self._commandresponse_map = self._arcam_talker.commandResponseMap.get()
        
    def on_start(self):
        # Let's start reading
        logger.info("Starting to read.")
        while (True):
            _response_word = self._arcam_talker.read_word().get()
            if _response_word != None:
                if len(_response_word) > 0:
                    # We have data -> one command
                    print "Read: ", _response_word
                    print "command: ", _response_word[:4]
                    print "action: ", _response_word[5:8]
                    print "Map conversion: ", self._commandresponse_map.get(_response_word[:4])
                    
                    if self._commandresponse_map.get(_response_word[:4]) == "Main.Volume":
                        # Have the volume been updated?
                        print "Main.Volume have been updated to: ", self._arcam_talker.calc_volume_int(_response_word[7].get())
            else:
                print "Nothing yet."
            time.sleep(2)