"""Mixer that controls volume using a NAD amplifier."""

from __future__ import unicode_literals

import logging

import pygst
pygst.require('0.10')
import gobject
import gst

try:
    import serial
except ImportError:
    serial = None  # noqa

from mopidy_arcam import talker
from mopidy_arcam import reader


logger = logging.getLogger('mopidy_arcam')


class ArcamMixer(gst.Element, gst.ImplementsInterface, gst.interfaces.Mixer):
    __gstdetails__ = (
        'ArcamMixer',
        'Mixer',
        'Mixer to control Arcam amplifiers using a serial link',
        'Mopidy')

    port = gobject.property(type=str, default='/dev/ttyUSB0')
    source = gobject.property(type=str)
    speakers_a = gobject.property(type=str)
    speakers_b = gobject.property(type=str)

    _volume_cache = 0
    _arcam_talker = None

    def list_tracks(self):
        track = create_track(
            label='Master',
            initial_volume=0,
            min_volume=0,
            max_volume=100,
            num_channels=1,
            flags=(
                gst.interfaces.MIXER_TRACK_MASTER |
                gst.interfaces.MIXER_TRACK_OUTPUT))
        return [track]

    def get_volume(self, track):
        return [self._volume_cache]

    def set_volume(self, track, volumes):
        if len(volumes):
            volume = volumes[0]
            self._volume_cache = volume
            self._arcam_talker.set_volume(volume)

    def set_mute(self, track, mute):
        self._arcam_talker.mute(mute)

    def do_change_state(self, transition):
        if transition == gst.STATE_CHANGE_NULL_TO_READY:
            if serial is None:
                logger.warning('arcammixer dependency pyserial not found')
                return gst.STATE_CHANGE_FAILURE
            self._start_arcam_talker()
        return gst.STATE_CHANGE_SUCCESS

    def _start_arcam_talker(self):
        self._arcam_talker = talker.ArcamTalker.start(
            port=self.port,
            source=self.source or None,
            # Need to be changed to zones
            speakers_a=self.speakers_a or None,
            speakers_b=self.speakers_b or None
        ).proxy()
        # Ask for the volume of the Arcam receiver
        future = self._arcam_talker.get_volume()
        self._volume_cache = future.get()
        
        # Start listening on the serial port
        # for handling i.e. manual volume change
        print "Starting the reader..."
        future = self._arcam_talker.get_connection_device()
        self._arcam_reader = reader.ArcamReader.start(self._arcam_talker)


def create_track(label, initial_volume, min_volume, max_volume,
                 num_channels, flags):

    class Track(gst.interfaces.MixerTrack):
        def __init__(self):
            super(Track, self).__init__()
            self.volumes = (initial_volume,) * self.num_channels

        @gobject.property
        def label(self):
            return label

        @gobject.property
        def min_volume(self):
            return min_volume

        @gobject.property
        def max_volume(self):
            return max_volume

        @gobject.property
        def num_channels(self):
            return num_channels

        @gobject.property
        def flags(self):
            return flags

    return Track()
