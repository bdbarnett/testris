"""
Matrix keypad helper for touch displays in MPDisplay

Divides the display into a grid of rows and columns.
Returns the position of the touched cell, starting from 1
at the top left, or None if no cell is touched.

Usage:
from touch_matrix import Matrix
from board_config import display_drv

matrix = Matrix(display_drv, cols=3, rows=3)
while True:
    if pos := matrix.read():
        print(pos)

"""
class Matrix():
    def __init__(self, display_drv, cols=3, rows=3):
        self._display_drv = display_drv
        self.cols = cols
        self.rows = rows

    def read(self):
        try:
            point = self._display_drv.get_touched()
        except OSError:
            # Not ready to read yet
            return None
        if point:
            x, y = point
            col = x // (self._display_drv.width // self.cols)
            row = y // (self._display_drv.height // self.rows)
            return row * self.cols + col + 1
        return None
