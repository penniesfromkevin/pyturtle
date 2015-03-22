#!/usr/bin/env python
import time

import pyturtle

if __name__ == '__main__':
    pyturtle.init()
    tom = pyturtle.Turtle()
    tom.pen_down()

    for _ in range(8):
        tom.move(20)
        tom.right(45)
        tom.change_color()
        tom.change_bg()

    time.sleep(10)
    pyturtle.quit()
