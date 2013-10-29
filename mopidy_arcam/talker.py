import logging
import pykka
import serial
import time

import mopidy.core

logger = logging.getLogger('mopidy_arcam')


class ArcamTalker(pykka.ThreadingActor):
    """
    Independent thread which does the communication with the Arcam amplifier.
    
    """

    # Serial link config
    BAUDRATE = 38400
    BYTESIZE = 8
    PARITY = 'N'
    STOPBITS = 1

    # Timeout in seconds used for read/write operations.
    # If you set the timeout too low, the reads will never get complete
    # confirmations and calibration will decrease volume forever. If you set
    # the timeout too high, stuff takes more time. 0.2s seems like a good value
    # for NAD C 355BEE.
    TIMEOUT = 0.2

    # Number of volume levels the amplifier supports.
    # 100 for the Arcam AVR300 amplifier.
    VOLUME_LEVELS = 100
    
    # Translation map (commands and actions) for Arcam specific commands
    # The key is the taken from the NAD fork and then a Arcam translation is stored in the corresponding value.
    ARCAM_ZONE          = "1";
    ARCAM_ACTION_ASK    = "9";
    ARCAM_ACTION_ON     = "1";
    ARCAM_ACTION_OFF    = "0";
    ARCAM_ACTION_PREFIX_LENGTH = 6
    ARCAM_VOLUME_OFFSET = 48
    
    ASK_DEVICE_KEY      = 'Ask'
    
    commandRequestMap = {"Main.Power" :"PC_*",
                         "Main.Volume": "PC_/",
                         "Main.Mute"  : "PC_.",
                         "Main.Source": "PC_1"}
    commandResponseMap = {"AV_*" : "Main.Power",
                          "AV_/" : "Main.Volume",
                          "AV_." : "Main.Mute",
                          "AV_1" : "Main.Source"}
    actionRequestMap           = {"On"  : ARCAM_ACTION_ON,
                                  "Off" : ARCAM_ACTION_OFF,
                                  "+"   : ARCAM_ACTION_ON,
                                  "-"   : ARCAM_ACTION_OFF,
                                  ASK_DEVICE_KEY : ARCAM_ACTION_ASK}
    actionResponseMap   = {"1": "On",
                           "0": "Off"}
    sourceRequestMap    = {"DVD"  : "0",
                           "SAT"  : "1",
                           "AV"   : "2",
                           "PVR"  : "3",
                           "VCR"  : "4",
                           "CD"   : "5",
                           "FM"   : "6",
                           "AM"   : "7",
                           "DVDA" : "8"}
    sourceResponseMap   = {"0" : "DVD",
                           "1" : "SAT",
                           "2" : "AV",
                           "3" : "PVR",
                           "4" : "VCR",
                           "5" : "CD",
                           "6" : "FM",
                           "7" : "AM",
                           "8" : "DVDA"}
    
    def buildRequestString(self, commandCode, zone, action):
        if self.getRequestAction(action) != None:
            resultString = str(self.commandRequestMap.get(commandCode)) + str(zone) + str(self.getRequestAction(action))
        else:
            resultString = str(self.commandRequestMap.get(commandCode)) + str(zone) + str(action)
        return resultString
        
    
    def getRequestAction(self, action):
        return self.actionRequestMap.get(action)


    def __init__(self, port, source, speakers_a, speakers_b):
        super(ArcamTalker, self).__init__()

        self.port = port
        self.source = source
        # Need to be changed to zones
        self.speakers_a = speakers_a
        self.speakers_b = speakers_b
        self._arcam_volume = None
        self._device = None

    def on_start(self):
        self._open_connection()
        self._set_device_to_known_state()

    def _open_connection(self):
        logger.debug('Arcam amplifier: Connecting through "%s"', self.port)
        self._device = serial.Serial(
            port=self.port,
            baudrate=self.BAUDRATE,
            bytesize=self.BYTESIZE,
            parity=self.PARITY,
            stopbits=self.STOPBITS,
            timeout=self.TIMEOUT)
        self._get_device_model()

    def _set_device_to_known_state(self):
        self._power_device_on() # Starting main zone per default.
        #self._select_speakers() 
        self._select_input_source()
        self.mute(False)
        #self.calibrate_volume() #We can simply just ask for the volume
        self.get_volume()
        

    def _get_device_model(self):
        # Can't get this information from the Arcam receiver, so it's hardcoded
        return "Arcam AVR300"

    def _power_device_on(self):
        self._check_and_set('Main.Power', 'On')
        time.sleep(5) # Wait for the amp to actually start up and be ready for more input.

    def _select_speakers(self):
        if self.speakers_a is not None:
            self._check_and_set('Main.SpeakerA', self.speakers_a.title())
        if self.speakers_b is not None:
            self._check_and_set('Main.SpeakerB', self.speakers_b.title())

    def _select_input_source(self):
        if self.source is not None:
            self._check_and_set('Main.Source', self.sourceRequestMap.get(self.source), self.sourceResponseMap)

    def mute(self, mute):
        if mute:
            self._check_and_set('Main.Mute', 'Off') # turn Mute off
        else:
            self._check_and_set('Main.Mute', 'On') # turn Mute on

    def get_volume(self):
        logger.info("Getting volume.")
        rawVolume = ord(self._ask_device("Main.Volume"))
        self._arcam_volume = rawVolume - self.ARCAM_VOLUME_OFFSET;
        logger.info("Volume is now: ", self._arcam_volume)
        return self._arcam_volume

    def set_volume(self, volume):
        # Increase or decrease the amplifier volume until it matches the given
        # target volume.
        logger.debug('Setting volume to %d' % volume)
        target_nad_volume = int(round(volume * self.VOLUME_LEVELS / 100.0))
        if self._arcam_volume is None:
            return  # Calibration needed
        while target_nad_volume > self._arcam_volume:
            self._increase_volume()
            self._arcam_volume += 1
        while target_nad_volume < self._arcam_volume:
            self._decrease_volume()
            self._arcam_volume -= 1
        
    def _calc_volume_char(self, volume):
        return chr(volume+self.ARCAM_VOLUME_OFFSET)
    
    def _calc_volume_int(self, volume):
        return ord(volume-self.ARCAM_VOLUME_OFFSET)

    def _increase_volume(self):
        # Increase volume. Returns :class:`True` if confirmed by device.
        self._command_device("Main.Volume", "+")

    def _decrease_volume(self):
        # Decrease volume. Returns :class:`True` if confirmed by device.
        self._command_device("Main.Volume", "-")

    def _check_and_set(self, key, value, responseMap=None):
        for attempt in range(1, 4):
            if self._ask_device(key, responseMap) == value:
                return
            logger.info('Arcam amplifier: Setting "%s" to "%s" (attempt %d/3)', key, value, attempt)
            if self._command_device(key, value) == value:
                return
        if self._ask_device(key, responseMap) != value:
            logger.info(
                'Arcam amplifier: Gave up on setting "%s" to "%s"',
                key, value)

    def _ask_device(self, key, responseMap=None):
        self._write(self.buildRequestString(key, self.ARCAM_ZONE, self.ASK_DEVICE_KEY))
        resultString = self.readline()
        
        if len(resultString) > 0:
            if responseMap != None:
                resultString = responseMap.get(resultString[self.ARCAM_ACTION_PREFIX_LENGTH])
            elif self.actionResponseMap.get(resultString[self.ARCAM_ACTION_PREFIX_LENGTH]) != None:
                resultString = self.actionResponseMap.get(resultString[self.ARCAM_ACTION_PREFIX_LENGTH])
            else:
                # When no referenced action is found, return RAW type/data
                resultString = resultString[self.ARCAM_ACTION_PREFIX_LENGTH]
        return resultString

    def _command_device(self, key, value):
        #if type(value) == unicode:
        #    value = value.encode('utf-8')
        #self._write('%s=%s' % (key, value))
        self._write(self.buildRequestString(key, self.ARCAM_ZONE, value))
        resultString = self.readline()
        if len(resultString) > 0:
            if self.actionResponseMap.get(resultString[self.ARCAM_ACTION_PREFIX_LENGTH]) != None:
                resultString = self.actionResponseMap.get(resultString[self.ARCAM_ACTION_PREFIX_LENGTH])
            else:
                resultString = resultString[self.ARCAM_ACTION_PREFIX_LENGTH]
        return resultString

    def _write(self, data):
        # Write data to device. Prepends and appends a newline to the data, as
        # recommended by the NAD documentation.
        if not self._device.isOpen():
            self._device.open()
        logger.debug('Trying to write: %s', data)
        self._device.write('%s\r\n' % data)

    def readline(self):
        # Read line from device. The result is stripped for leading and
        # trailing whitespace.
        if not self._device.isOpen():
            self._device.open()
        return self._device.readline().strip()
