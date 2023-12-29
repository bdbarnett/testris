_DEFAULT_TOUCH_ROTATION_TABLE = (0b000, 0b101, 0b110, 0b011)

class Touchpad():
    LEFT = 1
    DOWN = 2
    RIGHT = 3
    CW = 4
    UP = 5
    CCW = 6
    START = 7
    UNUSED = 8
    PAUSE = 9
    
    def __init__(self, touch_read_func, width, height, touch_rotation, rotation_table=None):
        self._touch_read_func = touch_read_func
        self.width = width
        self.height = height
        self._touch_rotation_table = rotation_table if rotation_table else _DEFAULT_TOUCH_ROTATION_TABLE
        self.set_touch_rotation(touch_rotation)

    def get_touched(self):
        # touch_read_func should return None, a point as a tuple (x, y), a point as a list [x, y] or 
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, x2], [y1, y2]].  If it doesn't, create a wrapper around your driver's read function
        # and set touch_read_func to that wrapper, or subclass TouchDriver and override .get_touched()
        # with your own logic.
        touched = self._touch_read_func()
        if touched:
            # If it looks like a point, use it, otherwise get the first point out of the list / tuple
            (x, y) = touched if isinstance(touched[0], int) else touched[0]
            if self._touch_swap_xy:
                x, y = y, x
            if self._touch_invert_x:
                x = self._touch_max_x - x
            if self._touch_invert_y:
                y = self._touch_max_y - y
            return x, y
        return None

    def set_touch_rotation(self, rotation):
        index = (rotation // 90) % len(self._touch_rotation_table)
        mask = self._touch_rotation_table[index]
        print(f"Looking up touch rotation {rotation} degrees (index: {index})")
        self.set_touch_rotation_mask(mask)

    def set_touch_rotation_mask(self, mask):
        # mask is an integer from 0 to 7 (or 0b001 to 0b111, 3 bits)
        # Currently, bit 2 = invert_y, bit 1 is invert_x and bit 0 is swap_xy, but that may change.
        # Your display driver should have a way to set rotation, but your touch driver may not have a way to set
        # its rotation.  You can call this function any time after you've created devices to change the rotation.
        print(f"Setting rotation mask to 0b{mask:>03b} (decimal {mask})\n")
        mask = mask & 0b111
        self._touch_invert_y = True if mask >> 2 & 1 else False
        self._touch_invert_x = True if mask >> 1 & 1 else False
        self._touch_swap_xy =  True if mask >> 0 & 1 else False
        self._touch_max_x = self.width - 1
        self._touch_max_y = self.height - 1

    def read(self):
        try:
            point = self.get_touched()
        except OSError as error:
            # Not ready to read yet
            return None
        if point:
            x, y = point
            if x < self.width // 3:
                if y < self.height // 3:
                    return 7
                elif y > self.height * 2 // 3:
                    return 1
                else:
                    return 4
            elif x > self.width * 2 // 3:
                if y < self.height // 3:
                    return 9
                elif y > self.height * 2 // 3:
                    return 3
                else:
                    return 6
            else:
                if y < self.height // 3:
                    return 8
                elif y > self.height * 2 // 3:
                    return 2
                else:
                    return 5
        return None

if __name__ == "__main__":
    from machine import I2C, Pin
    from ft6x36 import FT6x36
    
    i2c = I2C(0, sda=Pin(6), scl=Pin(5), freq=100000)
    touch_drv = FT6x36(i2c)
    keypad = Touchpad(touch_drv.get_positions, width=320, height=480, touch_rotation=0)
    print(f"Type `keypad.read()` to get current position.")
