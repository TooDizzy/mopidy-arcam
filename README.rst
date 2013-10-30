************
Mopidy-Arcam
************

`Mopidy <http://www.mopidy.com/>`_ extension for controlling volume using an
external Arcam amplifier. Developed and tested with an Arcam AVR-300.

Installation
============

Install by running::

    sudo pip install Mopidy-Arcam

Or install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

The Mopidy-Arcam extension is enabled by default. To disable it, add the
following to ``mopidy.conf``::

    [arcam]
    enabled = true

The Arcam amplifier must be connected to the machine running Mopidy using a
serial cable.

To use the Arcam amplifier ot control volume, set the ``audio/mixer`` config
value in ``mopidy.conf`` to ``arcammixer``. You probably also needs to add some
properties to the ``audio/mixer`` config value.

Supported properties includes:

``port``:
    The serial device to use, defaults to ``/dev/ttyUSB0``. This must be
    set correctly for the mixer to work.

``source``:
    The source that should be selected on the amplifier, like ``DVD``, ``PVR``,
    ``VCR``, ``CD``, ``FM``, ``AM``, ``SAT``, ``DVDA``, etc. Leave unset if you don't want the
    mixer to change it for you.

``speakers-a``:
    Set to ``on`` or ``off`` if you want the mixer to make sure that
    speaker set A is turned on or off. Leave unset if you don't want the
    mixer to change it for you.

``speakers-b``:
    See ``speakers-a``.

Configuration examples::

    # Minimum configuration, if the amplifier is available at /dev/ttyUSB0
    [audio]
    mixer = arcammixer

    # Minimum configuration, if the amplifier is available elsewhere
    [audio]
    mixer = arcammixer port=/dev/ttyAMA0

    # Full configuration
    [audio]
    mixer = arcammixer port=/dev/ttyAMA0 source=aux


Project resources
=================

- `Source code <https://github.com/TooDizzy/mopidy-arcam>`_
- `Issue tracker <https://github.com/TooDizzy/mopidy-arcam/issues>`_
- `Download development snapshot <https://github.com/TooDizzy/mopidy-arcam/tarball/develop#egg=Mopidy-Arcam-dev>`_


Changelog
=========

v0.1 (2013-10-05)
-----------------

- Initial version for the Arcam receiver; based on a fork from the NAD mixer.

v0.2 (2013-10-29)
-----------------
- Now Mopidy will also handle if the volume of the amplifier is changed outside Mopidy. The volume is updated more or less instanyly and any client will get the updated volume when asking for the volume.
