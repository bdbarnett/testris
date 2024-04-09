"""
Matrix keypad helper for touch displays on MPDisplay

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
from mpdisplay import Events

class Matrix():
    def __init__(self, display_drv, cols=3, rows=3, keys=None):
        self._keys = keys if keys else [i+1 for i in range(cols*rows)]
        self._display_drv = display_drv
        self._cols = cols
        self._rows = rows

    def read(self):
        event = self._display_drv.poll_event()
        if event and event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            col = x // (self._display_drv.width // self._cols)
            row = y // (self._display_drv.height // self._rows)
            key = self._keys[row*self._cols + col]
            return key

        if event and event.type == Events.KEYDOWN:
            key = event.key
            return key

        return None
