from __future__ import unicode_literals

import pygst
pygst.require('0.10')
import gst
import gobject

from mopidy import exceptions, ext


__version__ = '0.1'

default_config = b"""
[arcam]
enabled = true
"""


class Extension(ext.Extension):
    dist_name = 'Mopidy-Arcam'
    ext_name = 'arcam'
    version = __version__

    def get_default_config(self):
        return default_config

    def validate_environment(self):
        try:
            import serial  # noqa
        except ImportError as e:
            raise exceptions.ExtensionError('pyserial library not found', e)

    def register_gstreamer_elements(self):
        from .mixer import ArcamMixer
        gobject.type_register(ArcamMixer)
        gst.element_register(ArcamMixer, 'arcammixer', gst.RANK_MARGINAL)
