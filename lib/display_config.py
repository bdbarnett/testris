""" WT32-SC01 Plus 320x480 ST7796 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

from lcd_bus import I80Bus
from st7796 import ST7796, STATE_HIGH, STATE_LOW, STATE_PWM, PORTRAIT, LANDSCAPE, BYTE_ORDER_BGR, BYTE_ORDER_RGB
from machine import Pin

# The WT32-SC01 Plus has the reset pins of the display IC and the touch IC both
# tied to pin 4.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is not common.  If they aren't tied 
# together on your board, define reset in ST7796 instead, like:
#    ST7796(reset=4)
# Also do this for the display power pin if your board has one.  Most don't.
reset=Pin(4, Pin.OUT, value=1)

bus = I80Bus(
    dc=0,
    wr=47,
    cs=6,
    data0=9,
    data1=46,
    data2=3,
    data3=8,
    data4=18,
    data5=17,
    data6=16,
    data7=15,
    max_transfer_bytes=1048576,
    freq=20000000,
    dc_idle_level=0,
    dc_cmd_level=0,
    dc_dummy_level=0,
    dc_data_level=1,
    cmd_bits=8,
    param_bits=8,
    cs_active_high=False,
    reverse_color_bits=False,
    swap_color_bytes=True,
    pclk_active_neg=False,
    pclk_idle_low=False,
)

display_drv = ST7796(
    bus,
    display_width=320,
    display_height=480,
    reset_pin=None,
    reset_state=STATE_HIGH,
    power_pin=None,
    power_on_state=STATE_HIGH,
    backlight_pin=45,
    backlight_on_state=STATE_HIGH,
    offset_x=0,
    offset_y=0,
    color_byte_order=BYTE_ORDER_BGR,
    orientation=PORTRAIT,
    color_space=None,
    rgb565_byte_swap=False,
    bpp=16,
)

display_drv.init()
