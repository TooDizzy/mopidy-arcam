import logging
import pykka
import serial

logger = logging.getLogger('mopidy_arcam')


class ArcamReader(pykka.ThreadingActor):
    """
    Independent thread which is responsible for reading.
    
    """
    
    _messages = []
    _device = None
    
    def __init__(self, device):
        super(ArcamReader, self).__init__()
        self._device = device
        
        
    def _listen_rx(self):
        # Continuously listen on the serial line for any messages from the Arcam amp.
        
        # Do not trigger action when write was triggered by talker.
        # Just store the result unless it should be igonred.
        result = None
        
        while self._device.inWaiting():
            print "inWaiting: ", self._device.inWaiting()
            result = self._device.read(self._device.inWaiting())
            print "Result: ", result
        
        if result != None:
            self._messages.append(result)
        
    def on_start(self):
        print "starting reader thread."
        # Start to listen on the serial port
        self._listen_rx()
    
    def get_answer(self):
        # Return the oldest command
        return self._messages.pop(0);