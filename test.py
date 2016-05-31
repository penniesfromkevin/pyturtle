#!/usr/bin/env python
"""A simple test of PyTurtle.
"""
import pyturtle


def main():
    """The test program.
    """
    tom = pyturtle.Turtle()
    tom.pen_down()

    for _ in range(8):
        tom.move(20)
        tom.right(45)
        tom.change_color()
        tom.change_bg()

    pyturtle.add_color('this', (-1, 1000, 345))
    tom.color = 'this'
    tom.star()

    pyturtle.sleep(10)
    return 0


if __name__ == '__main__':
    pyturtle.start()
    EXIT_CODE = main()
    pyturtle.end(EXIT_CODE)
