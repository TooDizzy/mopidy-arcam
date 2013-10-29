'''
Created on 29/10/2013

@author: tue
'''


import logging
import pykka

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
    
    def _calculate_volume(self, volume):
        return volume-self._arcam_talker.ARCAM_VOLUME_OFFSET.get()
        
    def on_start(self):
        # Let's start reading
        while (True):
            _response_word = self._arcam_talker.read_word().get()
            print "Destruct? ", self._arcam_talker.destruct().get()
            if _response_word != None:
                if len(_response_word) > 0:
                    # We have data -> one command
                    if self._commandresponse_map.get(_response_word[:4]) == "Main.Volume":
                        # Have the volume been updated?
                        self._arcam_talker.update_volume(self._calculate_volume(ord(_response_word[6])))
            if self._arcam_talker.destruct().get() == True:
                break

    