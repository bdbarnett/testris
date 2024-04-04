
class Matrix():
    LEFT = 1
    DOWN = 2
    RIGHT = 3
    CW = 4
    UP = 5
    CCW = 6
    START = 7
    UNUSED = 8
    PAUSE = 9
    
    def __init__(self, display_drv):
        self._display_drv = display_drv

    def read(self):
        try:
            point = self._display_drv.get_touched()
        except OSError as error:
            # Not ready to read yet
            return None
        if point:
            x, y = point
            if x < self._display_drv.width // 3:
                if y < self._display_drv.height // 3:
                    return 7
                elif y > self._display_drv.height * 2 // 3:
                    return 1
                else:
                    return 4
            elif x > self._display_drv.width * 2 // 3:
                if y < self._display_drv.height // 3:
                    return 9
                elif y > self._display_drv.height * 2 // 3:
                    return 3
                else:
                    return 6
            else:
                if y < self._display_drv.height // 3:
                    return 8
                elif y > self._display_drv.height * 2 // 3:
                    return 2
                else:
                    return 5
        return None
