# testris
A MicroPython game to test display drivers

I needed a concrete example of how generic display drivers in MicroPython might be used.  This game uses 10 buffers to hold the graphics representation of 10 color blocks and 1 buffer to hold the text banner showing the score and lines.

The `display_config.py`, `st7796.py` and `ft6x36.py`files in `lib` are specific to the WT32-SC01-Plus, but may be modified to support other displays and touchscreens.  `backlight.py` accompanies the `mpdisplay` drivers.  `touchpad.py` is a simple support class that takes in a touchscreen driver and outputs a number from 1 to 9 when read by dividing the screen into a 3 x 3 grid.

![splash](screenshots/splash.png)
![screenshot](screenshots/screenshot.png)
