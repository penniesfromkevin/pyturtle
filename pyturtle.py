#!/usr/bin/env python3
"""A simple turtle implementation in Python.

This is intended for both interactive sessions and keyboard control.
It came about when I was preparing a Python class and wanted to try a
few things.

There are three ways PyTurtle can be used:
1. Interactively using the cursor keys to move the turtle.
   From the command line, simply call pyturtle as an application:
   $ python3 pyturtle.py
2. As a library so that the turtle can be programmed using Python.
   Here are the commands that should be run when used as a library:
     import pyturtle
     pyturtle.start()
     my_turtle = pyturtle.Turtle()
     my_turtle.move(10)
     pyturtle.end()
   The .start() and .end() methods are required to manage turtles.
3. Interactively using IDLE or a Python interactive session.
   From inside IDLE (the Python interactive shell):
     >>> import pyturtle
     >>> pyturtle.start()
     >>> my_turtle = pyturtle.Turtle()
   At this point you can continue to control the turtle using Python.
   To end the turtle session:
     >>> pyturtle.end()
   Because an event handler needs to be called every so often so that
   PyGame knows that the application is alive, using PyTurtle in IDLE
   will occasionally give you a you a warning such as:
       "" is not responding.
   In that case, simply ignore it or send another turtle command.
"""
__author__ = 'Kevin (penniesfromkevin@)'
__copyright__ = 'Copyright (c) 2014-2022, Kevin'

import argparse
import logging
import math
import sys

# http://www.pygame.org
import pygame


LOG_LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')
DEFAULT_LOG_LEVEL = LOG_LEVELS[3]
LOGGER = logging.getLogger(__name__)

HELP_INTERACTIVE = '''Interactive keys:
  <cursor_left>: Rotate left.
  <cursor_right>: Rotate right.
  <cursor_up>: Move forward.
  <backquote>: Set turtle angle to 0.
  <comma>: Rotate left 90 degrees
  <period>: Rotate right 90 degrees

  <space>: Hide/show turtle graphic.
  <cursor_down>: Toggle pen up/down.
  <minus>: Reduce pen thickness.
  <plus/equals>: Increase pen thickness.

  <escape>: Quit.
  <backspace>: Clear board.
  p: Pause (whatever that means).
  z: Cycle pen color.
  a: Cycle background color.
  r: Reset turtle position to center of screen, facing up.
  3 through 9: n-gon.
  0: Circle.
  s: Star.

  Also try <turtle_object>.help()
'''
HELP_TURTLE = '''Turtle object methods:
  .clear(bg_color=None): Clear the board by filling with bg_color
  .left(degrees=DEFAULT_ANGLE): Rotate left
  .right(degrees=DEFAULT_ANGLE): Rotate right
  .forward(units=1): Move forward (same as .move())
  .move(units=1): Move forward
  .backward(units=1): Move backward
  .about_face(): Turn 180 degrees
  .move_to(x_new, y_new): Move to an absolute position on the board
  .pen_down(): Lower the pen so that the turtle can draw
  .pen_up(): Lift the pen so that the turtle stops drawing
  .show_turtle(): Show the turtle graphic on screen
  .hide_turtle(): Hide the turtle graphic.
  .reset(): Move turtle back to starting position (center, facing up)
  .cycle_bg_color(): Change the background color to the next color
  .cycle_pen_color(): Change the pen color to the next color
  .cycle_color(color=None): Return the color after the given color
  .toggle_pen(): Toggle pen position (up becomes down, down becomes up)
  .ngon(sides=MIN_SIDES, length=None): Draw an n-gon
  .star(length=DEFAULT_LENGTH): Draw a star
  .repeat(times, angle=144, length=DEFAULT_LENGTH): Repeat rotate and move
  .help(): Get this help text

Turtle object attributes:
  .pen: Boolean; whether pen is down (True) and can draw, or not (False)
  .pen_size: Integer line thickness (1 to 20)
  .visible: Boolean: whether the turtle is displayed on screen (True) or not
  .angle: Integer degrees; orientation of the turtle object.
  .bg_color: Background (board) color (see Colors, below)
  .color: Pen color (see Colors, below)
  .speed: Integer Turtle speed (how many pixels turtle moves in 1 unit)

Colors (strings!):
  'red': (255, 0, 0)
  'brown': (205, 205, 0)
  'orange': (255, 205, 0)
  'yellow': (255, 255, 0)
  'green': (0, 255, 0)
  'cyan': (0, 255, 255)
  'blue': (0, 0, 255)
  'purple': (204, 0, 255)
  'magenta': (255, 0, 255)
  'pink': (255, 205, 205)
  'white': (255, 255, 255)
  'black': (0, 0, 0)
'''

FRAME_RATE = 20
BOARD_SIZE = (640, 480)
DEFAULT_SPEED = 4
DEFAULT_ANGLE = 5
DEFAULT_IMAGE = 'turtle.png'
DEFAULT_LENGTH = 72
MAX_SIDES = 72
MIN_SIDES = 3
THICKNESS_MAX = 20
DEG_TO_RAD = 0.017453293  # Converts degrees to radians.
# uh-oh; these below are not actually CONSTANT...
COLORS = {
    'red': (255, 0, 0),
    'brown': (205, 205, 0),
    'orange': (255, 205, 0),
    'yellow': (255, 255, 0),
    'green': (0, 255, 0),
    'cyan': (0, 255, 255),
    'blue': (0, 0, 255),
    'purple': (204, 0, 255),
    'magenta': (255, 0, 255),
    'pink': (255, 205, 205),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    }


class Turtle(pygame.sprite.Sprite):
    """Controllable turtle.
    """
    turtles = {}  # Keeps track of turtles (because there can be more than one)

    def __init__(self, board=None, page=None, speed=DEFAULT_SPEED):
        """Initialize the turtle.

        Args:
            board: Optional display surface; created if not provided
            page: Optional page for drawing; created if not provided
            speed: Integer speed.  Movement multiplier.
        """
        pygame.sprite.Sprite.__init__(self)
        self._keys = []

        self.angle = 0
        self.color = 'red'
        self.bg_color = 'black'
        self.speed = speed
        self.pen = False
        self.pen_size = 3
        self.visible = True
        self.x_pos = 0
        self.y_pos = 0

        # Everything blits onto board
        self.board = board if board else pygame.display.set_mode(BOARD_SIZE)
        # Page is a surface for drawing, which also blits onto board
        self.page = page if page else pygame.Surface(self.board.get_size())

        try:
            image_object = pygame.image.load(DEFAULT_IMAGE).convert_alpha()
        except (pygame.error, FileNotFoundError, NameError) as exc:
            # If the image was not found, use an image made from text.
            # This allows PyTurtle to be self-contained in a single file
            LOGGER.error('Turtle: Image %s (%s)', DEFAULT_IMAGE, exc)
            font = pygame.font.SysFont('Sans', 18)
            image_object = font.render('A', True, COLORS['green'])

        self._image = self.image = image_object
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()

        if self.board in Turtle.turtles:
            Turtle.turtles[self.board].append(self)
            self.update()
        else:
            Turtle.turtles[self.board] = [self]
            self.clear()
        self.reset()
        self.pen = True

    def update(self):
        """Update sprite, board, and page.
        """
        pygame.event.pump()  # This needs to be called every so often
        self.board.fill(get_color(self.bg_color))
        self.board.blit(self.page, (0, 0))
        for turtle in Turtle.turtles[self.board]:
            self.update_turtle(turtle)
        pygame.display.flip()

    def update_turtle(self, turtle):
        """Update sprite only.
        """
        while turtle.angle > 360:
            turtle.angle -= 360
        while turtle.angle < 0:
            turtle.angle += 360

        turtle.image = pygame.transform.rotate(turtle._image, -turtle.angle)
        turtle.width, turtle.height = turtle.image.get_size()
        turtle.rect = turtle.image.get_rect()
        turtle.rect.center = turtle.x_pos, turtle.y_pos

        x_off = turtle.x_pos - turtle.width // 2
        y_off = turtle.y_pos - turtle.height // 2
        if turtle.visible:
            turtle.board.blit(turtle.image, (x_off, y_off))

    def clear(self, bg_color=None):
        """Clear the draw page with the specified color.

        Uses turtle's background color if bg_color is not specified.

        Args:
            bg_color: Name of a supported color to use as background.
        """
        if not bg_color:
            bg_color = self.bg_color
        rgb_color = get_color(bg_color)
        self.page.set_colorkey(rgb_color)
        self.page.fill(rgb_color)
        self.update()

    def left(self, degrees=DEFAULT_ANGLE):
        """Rotates turtle counter-clockwise.

        Args:
            degrees: Integer degrees.
        """
        self.right(-degrees)

    def right(self, degrees=DEFAULT_ANGLE):
        """Rotates turtle clockwise.

        Args:
            degrees: Integer degrees.
        """
        self.angle += degrees
        self.update()

    def forward(self, units=1):
        """Move forward in direction faced.

        Args:
            units: How many units.
        """
        distance = units * self.speed
        x_new = self.x_pos + distance * math.sin(self.angle * DEG_TO_RAD)
        y_new = self.y_pos - distance * math.cos(self.angle * DEG_TO_RAD)
        self.move_to(x_new, y_new)

    def move(self, units=1):
        """Move forward in direction faced.

        Alias for forward().

        Args:
            units: How many units.
        """
        self.forward(units)

    def backward(self, units=1):
        """Move backward.

        Args:
            units: How many units.
        """
        self.forward(-units)

    def about_face(self):
        """Turn 180 degrees (turn around in place).
        """
        self.right(180)

    def move_to(self, x_new, y_new):
        """Move from current (x, y) to new (x, y).

        Args:
            x_new: New X coordinate.
            y_new: New Y coordinate.
        """
        if self.pen:
            color = get_color(self.color)
            pygame.draw.line(self.page, color, (self.x_pos, self.y_pos),
                             (x_new, y_new), self.pen_size)
        self.x_pos = x_new
        self.y_pos = y_new
        self.update()

    def pen_down(self):
        """Put pen down on page; movement will cause drawing.
        """
        self.pen = True

    def pen_up(self):
        """Remove pen from page; movement will no longer cause drawing.
        """
        self.pen = False

    def toggle_pen(self):
        """Toggle pen state.
        """
        self.pen = not self.pen
        LOGGER.debug('toggle_pen: pen=%s', self.pen)

    def show_turtle(self):
        """Show turtle graphic on screen.
        """
        self.visible = True
        self.update()

    def hide_turtle(self):
        """Hide turtle graphic (do NOT show on screen).
        """
        self.visible = False
        self.update()

    def toggle_show(self):
        """Toggle turtle visibility.
        """
        self.visible = not self.visible
        LOGGER.debug('toggle_show: visible=%s', self.visible)
        self.update()

    def reset(self):
        """Reset location (center of board) and direction (facing up).
        """
        x_0, y_0 = self.board.get_size()
        x_0 = x_0 // 2
        y_0 = y_0 // 2
        self.angle = 0
        self.move_to(x_0, y_0)

    def help(self):
        """Get a list of methods the Turtle object supports.
        """
        help(HELP_TURTLE)

    def get_input(self):
        """Get user input via events.

        Returns:
            An intent, as a string.  Can be 'pause' or 'quit'.
        """
        intent = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intent = 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    intent = 'quit'
                elif event.key == pygame.K_p:
                    intent = 'pause'
                elif event.key in (pygame.K_QUESTION, pygame.K_h):
                    help()

                elif event.key == pygame.K_LEFT:
                    if 'l' not in self._keys:
                        self._keys.append('l')
                elif event.key == pygame.K_RIGHT:
                    if 'r' not in self._keys:
                        self._keys.append('r')
                elif event.key == pygame.K_UP:
                    if 'f' not in self._keys:
                        self._keys.append('f')
                elif event.key == pygame.K_DOWN:
                    self.toggle_pen()
                elif event.key == pygame.K_z:
                    self.cycle_pen_color()
                elif event.key == pygame.K_a:
                    self.cycle_bg_color()

                elif event.key == pygame.K_COMMA:
                    self.left(90)
                elif event.key == pygame.K_PERIOD:
                    self.right(90)

                elif event.key == pygame.K_SPACE:
                    self.toggle_show()
                elif event.key == pygame.K_BACKQUOTE:
                    self.angle = 0
                    self.update()
                elif event.key == pygame.K_BACKSPACE:
                    self.clear(self.bg_color)
                elif event.key == pygame.K_r:
                    self.reset()

                elif event.key == pygame.K_MINUS:
                    self.pen_size -= 1
                    if self.pen_size < 1:
                        self.pen_size = 1
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    self.pen_size += 1
                    if self.pen_size > THICKNESS_MAX:
                        self.pen_size = THICKNESS_MAX

                elif event.key == pygame.K_s:
                    self.star()
                elif event.key == pygame.K_c:
                    self.ngon(MAX_SIDES)
                elif event.key in range(pygame.K_3, pygame.K_9 + 1):
                    sides = event.key - pygame.K_0
                    self.ngon(sides)
                elif event.key == pygame.K_0:
                    self.ngon(MAX_SIDES)

                else:
                    print('Unused KEYDOWN = %s' % event.key)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    if 'f' in self._keys:
                        self._keys.remove('f')
                elif event.key == pygame.K_LEFT:
                    if 'l' in self._keys:
                        self._keys.remove('l')
                elif event.key == pygame.K_RIGHT:
                    if 'r' in self._keys:
                        self._keys.remove('r')

        for key in self._keys:
            if key == 'l':
                self.left()
            elif key == 'r':
                self.right()
            elif key == 'f':
                self.forward()

        return intent

    def cycle_bg_color(self):
        """Change the background color (by cycling it).
        """
        self.bg_color = self.cycle_color(self.bg_color)
        self.update()

    def cycle_pen_color(self):
        """Change the current turtle color (by cycling it).
        """
        self.color = self.cycle_color()

    def cycle_color(self, color=None):
        """Return the next color in the color cycle.

        Args:
            color: Name of a supported color, which will be incremented.

        Returns:
            The next color name in the list of colors.
        """
        if not color:
            color = self.color
        color_names = list(COLORS.keys())
#        color_names = sorted(COLORS.keys())
        index = color_names.index(color) + 1
        if index >= len(color_names):
            index = 0
        new_color = color_names[index]
        return new_color

    def ngon(self, sides=MIN_SIDES, length=None):
        """Draw an N-gon, from MIN_SIDES to MAX_SIDES sides.

        Drawing with a number of sides that does not divide evenly into
        360, such at 7, may result in less-than-perfect polygons.

        Args:
            sides: Number of sides (MIN_SIDES to MAX_SIDES, inclusive).
            length: Length of each side; if this is not set, the length
                will be scaled based on speed.
        """
        if sides > MAX_SIDES:
            sides = MAX_SIDES
        elif sides < MIN_SIDES:
            sides = MIN_SIDES
        angle = 360 // sides
        if not length:
            length = (self.speed * 36) // sides
        LOGGER.debug('ngon: sides=%s, length=%s', sides, length)
        self.repeat(sides, angle, length)

    def star(self, length=DEFAULT_LENGTH):
        """Draw a star.

        Args:
            length: Length of each side.
        """
        LOGGER.debug('star: length=%s', length)
        self.repeat(5, 144, length)

    def repeat(self, times, angle=144, length=DEFAULT_LENGTH):
        """Move and turn repeatedly.

        Args:
            times: How many times to do this.
            angle: Integer angle to turn; positive>right, negative>left
            length: Integer length to move.
        """
        LOGGER.debug('repeat: times=%s, angle=%s, length=%s',
                     times, angle, length)
        for _ in range(times):
            self.move(length)
            self.right(angle)


def parse_args():
    """Parse user arguments and return as parser object.

    Returns:
        Parser object with arguments as attributes.
    """
    parser = argparse.ArgumentParser(description='PyTurtle.')
    parser.add_argument(
        '-L', '--loglevel', choices=LOG_LEVELS, default=DEFAULT_LOG_LEVEL,
        help='Set the logging level.')
    args = parser.parse_args()
    return args


def help(help_text=HELP_INTERACTIVE):
    """Show available help in two modes, interactive and methods.

    Args:
        help_text: One of the CONSTANT help text blocks
    """
    print(help_text)


def add_color(color_name, rgb_triplet):
    """Add a new color definition to the existing colors.

    This can also change an existing color definition if the name
    already exists.

    Args:
        color_name: Name of the color, preferably cased similar to the
            existing color names.
        rgb_triplet: Sequence of three decimal numbers from 0 to 255,
            with each number in the triplet specifying, in order, the
            amount of red, green, and blue desired in the new color.
    """
    new_definition = []
    for rgb_part in rgb_triplet:
        if rgb_part < 0:
            LOGGER.warning(
                'add_color: RGB value should be >= 0 (was %s)', rgb_part)
            rgb_part = 0
        elif rgb_part > 255:
            LOGGER.warning(
                'add_color: RGB value should be <= 255 (was %s)', rgb_part)
            rgb_part = 255
        new_definition.append(rgb_part)
    COLORS[color_name] = tuple(new_definition)


def get_color(color_name):
    """Gets color RGB triplet by name.

    Args:
        color_name: Name of an existing color.

    Returns:
        A color RGB triplet, or None if the name could not be found.
    """
    if color_name in COLORS:
        rgb_triplet = COLORS[color_name]
    else:
        a_color = COLORS.keys()[0]
        rgb_triplet = COLORS[a_color]
    return rgb_triplet


def sleep(seconds=1):
    """Wait for a specified number of seconds before continuing.

    Args:
        seconds: Number of seconds to wait.
    """
    LOGGER.info('sleep: Sleeping for %s seconds...', seconds)
    for index in range(seconds, 0, -1):
        LOGGER.debug(index)
        pygame.time.wait(1000)


def start():
    """Initialize PyGame, and thus Pyturtle.
    """
    LOGGER.debug('start: Initializing Pyturtle.')
    pygame.init()


def end(exit_code=0):
    """Quit PyGame.

    Args:
        exit_code: Numeric exit code from 0 to 255 (0 is clean exit).
    """
    LOGGER.debug('end: Ending Pyturtle.')
    pygame.quit()
    sys.exit(exit_code)


def main():
    """Main game.
    """
    exit_code = 0
    clock = pygame.time.Clock()
    turtle = Turtle()

    game_over = False
    while not game_over:
        intent = turtle.get_input()
        if intent == 'quit':
            game_over = True
        clock.tick(FRAME_RATE)
    return exit_code


if __name__ == '__main__':
    ARGS = parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=getattr(logging, ARGS.loglevel))
    start()
    EXIT_CODE = main()
    end(EXIT_CODE)
