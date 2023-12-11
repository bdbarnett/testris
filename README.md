# testris
A MicroPython game to test display drivers

I needed a concrete example of how generic display drivers in MicroPython might be used.  This game uses 10 buffers to hold the graphics representation of 10 color blocks and 1 buffer to hold the text banner showing the score and lines.

The files in `lib` are specific to the WT32-SC01-Plus, but may be modified to support other displays and touchscreens.
