# testris
A MicroPython game to test display drivers

I needed a concrete example of how [MPDisplay](https://github.com/bdbarnett/mpdisplay) might be used without add-on libraries.  This game uses 10 buffers to hold the graphics representation of 10 color blocks and 1 buffer that is reused to show the text at the bottom of the splash screen and a banner at the top of the play screen showing score and messages.

![splash](screenshots/splash.png)
![screenshot](screenshots/screenshot.png)
