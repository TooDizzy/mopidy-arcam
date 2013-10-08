import logging
import pykka
import time

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
        print "Starting loop."
        while self._device.inWaiting():
            print "inWaiting: ", self._device.inWaiting()
            result = self._device.read(self._device.inWaiting())
            print "Result (reader): ", result
        
            if result != None:
                self._messages.append(result)
            # Sleep for a little while -> Should be handled more elegantly
            time.sleep(0.5)
        print "End of loop"
        
    def on_start(self):
        print "starting reader thread."
        # Start to listen on the serial port
        self._listen_rx()
    
    def on_receive(self, message):
        print "message (reader): ", message
        return self.get_answer()
    
    def get_answer(self):
        # Return the oldest command
        answer = self._messages.pop(0)
        print "Answer (reader): ", answer
        return answer
    
    