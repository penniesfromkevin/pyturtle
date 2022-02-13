#!/usr/bin/env python
"""A simple test of PyTurtle with multiple turtles
"""
import pyturtle


def main():
    """The test program.
    """
    tom = pyturtle.Turtle()
    sam = pyturtle.Turtle(tom.board, tom.page)
#    sam.color = 'blue'
    sam.about_face()

    pyturtle.help()
    for _ in range(len(pyturtle.COLORS)):
        tom.move(15)
        sam.move(15)
        tom.right(25)
        sam.right(25)
        tom.cycle_pen_color()
        sam.cycle_pen_color()
        tom.cycle_bg_color()
        sam.cycle_bg_color()

    pyturtle.add_color('this', (-1, 1000, 345))
    tom.color = 'this'
    sam.color = 'this'
    tom.star()
    sam.star()
    tom.ngon(72)
    sam.ngon(72)
    sam.help()

    pyturtle.sleep(10)
    return 0


if __name__ == '__main__':
    pyturtle.start()
    EXIT_CODE = main()
    pyturtle.end(EXIT_CODE)
