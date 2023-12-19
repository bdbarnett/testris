# testris
A MicroPython game to test display drivers

I needed a concrete example of how generic display drivers in MicroPython might be used.  `display_simpletest.py` does that, but I wanted something more practical.  This game uses 10 buffers to hold the graphics representation of 10 color blocks and 1 buffer that is reused to show the text at the bottom of the splash screen and a banner at the top of the play screen showing score and messages.

The `display_config.py`, `st7796.py` and `ft6x36.py`files in `lib` are required by the WT32-SC01-Plus, but may be modified to support other displays and touchscreens.  `display_driver.py` is a modified version of kdschlosser's display driver and works with his lcd_bus drivers.  `touchpad.py` is a simple support class that takes in a touchscreen driver and outputs a number from 1 to 9 when read by dividing the screen into a 3 x 3 grid.

![splash](screenshots/splash.png)
![screenshot](screenshots/screenshot.png)
