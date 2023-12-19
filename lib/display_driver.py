import micropython
import time
from machine import Pin, PWM
from micropython import const

import lcd_bus


micropython.alloc_emergency_exception_buf(256)
# gc.threshold(0x10000) # leave enough room for SPI master TX DMA buffers

# Constants

BYTE_ORDER_RGB = const(0x00)
BYTE_ORDER_BGR = const(0x08)

_RASET = const(0x2B)
_CASET = const(0x2A)
_RAMWR = const(0x2C)
_MADCTL = const(0x36)

_MADCTL_MY = const(0x80)  # 0=Top to Bottom, 1=Bottom to Top
_MADCTL_MX = const(0x40)  # 0=Left to Right, 1=Right to Left
_MADCTL_MV = const(0x20)  # 0=Normal, 1=Row/column exchange
_MADCTL_ML = const(0x10)  # Refresh 0=Top to Bottom, 1=Bottom to Top
_MADCTL_BGR = const(0x08)  # BGR color order
_MADCTL_MH = const(0x04)  # Refresh 0=Left to Right, 1=Right to Left

# MADCTL values for each of the orientation constants for non-st7789 displays.
_ORIENTATION_TABLE = (
    _MADCTL_MX,
    _MADCTL_MV,
    _MADCTL_MY,
    _MADCTL_MY | _MADCTL_MX | _MADCTL_MV
)

# Negative orientation constants indicate the MADCTL value will come from
# the ORIENTATION_TABLE, otherwise the rot value is used as the MADCTL value.
PORTRAIT = const(-1)
LANDSCAPE = const(-2)
REVERSE_PORTRAIT = const(-3)
REVERSE_LANDSCAPE = const(-4)

STATE_HIGH = 1
STATE_LOW = 0
STATE_PWM = -1


class Display:

    display_name = 'Display'

    # Default values of "power" and "backlight" are reversed logic! 0 means ON.
    # You can change this by setting backlight_on and power_on arguments.

    def __init__(
        self,
        data_bus,
        display_width,
        display_height,
        reset_pin=None,
        reset_state=STATE_HIGH,
        power_pin=None,
        power_on_state=STATE_HIGH,
        backlight_pin=None,
        backlight_on_state=STATE_HIGH,
        offset_x=0,
        offset_y=0,
        color_byte_order=BYTE_ORDER_RGB,
        orientation=PORTRAIT,
        color_space=None,
        rgb565_byte_swap=False,
        bpp=None,
    ):

        if power_on_state not in (STATE_HIGH, STATE_LOW):
            raise RuntimeError(
                'power on state must be either STATE_HIGH or STATE_LOW'
            )

        if reset_state not in (STATE_HIGH, STATE_LOW):
            raise RuntimeError(
                'reset state must be either STATE_HIGH or STATE_LOW'
            )

        if backlight_on_state not in (STATE_HIGH, STATE_LOW, STATE_PWM):
            raise RuntimeError(
                'backlight on state must be either '
                'STATE_HIGH, STATE_LOW or STATE_PWM'
            )

        self.display_width = display_width
        self.display_height = display_height
        if reset_pin is None:
            self._reset_pin = None
        else:
            self._reset_pin = Pin(reset_pin, Pin.OUT)
            self._reset_pin.value(not reset_state)

        self._reset_state = reset_state

        if power_pin is None:
            self._power_pin = None
        else:
            self._power_pin = Pin(power_pin, Pin.OUT)
            self._power_pin.value(not power_on_state)

        self._power_on_state = power_on_state

        if backlight_pin is None:
            self._backlight_pin = None
        elif backlight_on_state == STATE_PWM:
            pin = Pin(backlight_pin, Pin.OUT)
            self._backlight_pin = PWM(pin, freq=38000)
        else:
            self._backlight_pin = Pin(backlight_pin, Pin.OUT)
            self._backlight_pin.value(not backlight_on_state)

        self._backlight_on_state = backlight_on_state

        self._offset_x = offset_x
        self._offset_y = offset_y
        self._data_bus = data_bus

        self._param_buf = bytearray(4)
        self._param_mv = memoryview(self._param_buf)

        self._orientation = orientation
        self._initilized = False

        self._color_byte_order = color_byte_order
        self._color_space = color_space
        self._bpp = bpp # if bpp else lv.color_format_get_size(color_space) * 8
        self._color_size = self._bpp // 8

        data_bus.init(display_width, display_height, self._bpp, rgb565_byte_swap=False)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value

        if self._initilized:
            self._param_buf[0] = (
                self._madctl(self._color_byte_order, value, _ORIENTATION_TABLE)
            )
            self._data_bus.tx_param(_MADCTL, self._param_mv[:1])

    def init(self):
        self._initilized = True
        self.orientation = self._orientation
        self.backlight = 100

    def set_params(self, cmd, params=None):
        self._data_bus.tx_param(cmd, params)

    def get_params(self, cmd, params):
        self._data_bus.rx_param(cmd, params)

    @property
    def power(self):
        if self._power_pin is None:
            return -1

        state = self._power_pin.value()
        if self._power_on_state:
            return state

        return not state

    @power.setter
    def power(self, value):
        if self._power_pin is None:
            return

        if self._power_on_state:
            self._power_pin.value(value)
        else:
            self._power_pin.value(not value)

    def reset(self):
        if self._reset_pin is None:
            return

        self._reset_pin.value(self._reset_state)
        time.sleep_ms(120)
        self._reset_pin.value(not self._reset_state)

    @property
    def backlight(self):
        if self._backlight_pin is None:
            return -1

        if self._backlight_on_state == STATE_PWM:
            value = self._backlight_pin.duty_u16()  # NOQA
            return round(value / 65535 * 100.0)

        value = self._backlight_pin.value()

        if self._power_on_state:
            return value

        return not value

    @backlight.setter
    def backlight(self, value):
        if self._backlight_pin is None:
            return

        if self._backlight_on_state == STATE_PWM:
            self._backlight_pin.duty_u16(value / 100 * 65535)  # NOQA
        elif self._power_on_state:
            self._backlight_pin.value(int(bool(value)))
        else:
            self._backlight_pin.value(not int(bool(value)))

    @staticmethod
    def _madctl(colormode, rotation, rotations):
        # if rotation is 0 or positive use the value as is.
        if rotation >= 0:
            return rotation | colormode

        # otherwise use abs(rotation)-1 as index to
        # retrieve value from rotations set

        index = abs(rotation) - 1
        if index > len(rotations):
            RuntimeError('Invalid display orientation value specified')

        return rotations[index] | colormode

    def blit(self, x, y, width, height, buf):
        # Column addresses
        x1 = x + self._offset_x
        x2 = x + self._offset_x + width - 1

        self._param_buf[0] = (x1 >> 8) & 0xFF
        self._param_buf[1] = x1 & 0xFF
        self._param_buf[2] = (x2 >> 8) & 0xFF
        self._param_buf[3] = x2 & 0xFF

        self._data_bus.tx_param(_CASET, self._param_mv[:4])

        # Page addresses
        y1 = y + self._offset_y
        y2 = y + self._offset_y + height - 1

        self._param_buf[0] = (y1 >> 8) & 0xFF
        self._param_buf[1] = y1 & 0xFF
        self._param_buf[2] = (y2 >> 8) & 0xFF
        self._param_buf[3] = y2 & 0xFF

        self._data_bus.tx_param(_RASET, self._param_mv[:4])

        self._data_bus.tx_color(_RAMWR, buf, x1, y1, x2, y2)


class DisplayDriver(Display):

    display_name = 'DisplayDriver'

    def __init__(self, *args, frame_buffer1, frame_buffer2=None, **kwargs):
        super().__init__()
        try:
            import lvgl as lv
        except ImportError:
            raise RuntimeError('lvgl not found')

        if not lv.is_initialized():
            lv.init()

        self._disp_drv = lv.display_create(self.display_width, self.display_height)
        self._disp_drv.set_color_format(self._color_space)

        self._disp_drv.set_flush_cb(self._flush_cb)

        if isinstance(self._data_bus, lcd_bus.RGBBus):
            self._disp_drv.set_draw_buffers(
                frame_buffer1,
                frame_buffer2,
                len(frame_buffer1),
                lv.DISP_RENDER_MODE.FULL
            )
        else:
            self._disp_drv.set_draw_buffers(
                frame_buffer1,
                frame_buffer2,
                len(frame_buffer1),
                lv.DISP_RENDER_MODE.PARTIAL
            )

        self._data_bus.register_callback(self._flush_ready_cb, self._disp_drv)

    def _flush_cb(self, disp_drv, area, color_p):
        # we have to use the __dereference__ method because this method is
        # what converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        self.blit(area.x1, area.y1, w:=(area.x2-area.x1+1), h:=(area.y2-area.y1+1), color_p.__dereference__(w*h*self._color_size))

    # we always register this callback no matter what. This is what tells LVGL
    # that the buffer is able to be written to. If this callback doesn't get
    # registered then the flush function is going to block until the buffer
    # gets emptied. Everything is handeled internally in the bus driver if
    # using DMA and double buffer.
    def _flush_ready_cb(self, disp_drv):
        disp_drv.flush_ready()
