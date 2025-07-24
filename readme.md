# LEDMatrix Effects!

This is a fun screensaver-and-clock device built from a RP2350 Feather, a 32x32 LED Matrix, a NeoKey 1x4 for user interaction, and a PCF8523 real-time clock.

At one point it also included a second Feather to handle 'comms', with an attached IR Remote Receiver and AirLift board.  Eventually things got too complicated to quickly connect the display to my laptop and start coding from the couch, so I simplified the project down to what it looks like today.

- When possible, all effects have been coded to work on other resolution screens (ex. 64x64), although I do not currently have the ability to test this.
- The real-time clock is optional and can be commented out in device.py. Any time the clock would be displayed, 00:00:00 will be displayed instead.
- The NeoKeys are technically optional and can be commented out in device.py. Boot.py must be removed if not using NeoKeys.
- If another microprocessor is used, the effect framerates may need to be adjusted (search for calls to limitStep within each effect's play loop)


**Credits & Dependencies**
- Tested with CircuitPython 9.2.3
- All included libraries courtesy Adafruit CircuitPython, available here: https://circuitpython.org/libraries
- Included font converted from OpenType font 04B03
- Easing functions in device.py courtesy Easings.net
- All other code by Paul Gallo (pgallo@gmail.com)