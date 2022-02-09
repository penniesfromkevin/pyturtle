#!/usr/bin/env python3
"""A simple turtle implementation in Python.

This is intended for both interactive sessions and keyboard control.
It came about when I was preparing a Python class and wanted to try a
few things.
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
    'orange': (255, 205, 0),
    'yellow': (255, 255, 0),
    'brown': (205, 205, 0),
    'green': (0, 255, 0),
    'cyan': (0, 255, 255),
    'blue': (0, 0, 255),
    'magenta': (255, 0, 255),
    'pink': (255, 205, 205),
    'purple': (204, 0, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    }


class Turtle(pygame.sprite.Sprite):
    """Controllable turtle.
    """
    def __init__(self, board=None, speed=DEFAULT_SPEED):
        """Initialize the turtle.

        Args:
            board_size: Display surface size; tuple of (width, height).
            speed: Integer speed.  Movement multiplier.
        """
        pygame.sprite.Sprite.__init__(self)
        self._keys = []

        self.angle = 0
        self.color = 'red'
        self.bg_color = 'black'
        self.speed = speed
        self.thickness = 3
        self.pen = False
        self.x_pos = self.y_pos = 0

        if board:
            self.board = board
        else:
            self.board = pygame.display.set_mode(BOARD_SIZE)

        try:
            image_object = pygame.image.load(DEFAULT_IMAGE).convert_alpha()
        except pygame.error:
            print('ERROR: Could not load image %s' % DEFAULT_IMAGE)
            image_object = None
        self._image = self.image = image_object
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.page = None

        self.reset()
        self.clear()

    def update(self):
        """Update sprite.
        """
        while self.angle > 360:
            self.angle -= 360
        while self.angle < 0:
            self.angle += 360

        self.image = pygame.transform.rotate(self._image, -self.angle)
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.center = self.x_pos, self.y_pos

        self.board.fill(get_color(self.bg_color))
        if self.page:
            self.board.blit(self.page, (0, 0))
        x_off = self.x_pos - self.width // 2
        y_off = self.y_pos - self.height // 2
        self.board.blit(self.image, (x_off, y_off))
        pygame.event.pump()
        pygame.display.flip()

    def clear(self, bg_color=None):
        """Clear the draw page with the specified color.

        Args:
            bg_color: Name of a supported color to use as background.
        """
        if not bg_color:
            bg_color = self.bg_color
        self.page = pygame.Surface(self.board.get_size())
        self.page.set_colorkey(get_color(bg_color))
        self.page.fill(get_color(bg_color))
        self.update()

    def left(self, degrees=DEFAULT_ANGLE):
        """Rotates turtle counter-clockwise.

        Args:
            degrees: Integer degrees.
        """
        self.right(-degrees)
#        self.angle -= degrees
#        self.update()

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
                             (x_new, y_new), self.thickness)
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

    def reset(self):
        """Reset location.
        """
        x_0, y_0 = self.board.get_size()
        x_0 = x_0 // 2
        y_0 = y_0 // 2
        self.move_to(x_0, y_0)

    def help_interactive(self):
        """Show available interactive keys.
        """
        print('Possible interactive keys:')
        print(' <cursor_left>: Rotate left.')
        print(' <cursor_right>: Rotate right.')
        print(' <cursor_up>: Move forward.')
        print(' <space>: Set turtle angle to 0.')
        print(' <comma>: Rotate left 90 degrees')
        print(' <period>: Rotate right 90 degrees')
        print()
        print(' <cursor_down>: Toggle pen up/down.')
        print(' <minus>: Reduce pen thickness.')
        print(' <plus/equals>: Increase pen thickness.')
        print()
        print(' <escape>: Quit.')
        print(' <backspace/delete>: Clear board.')
        print(' p: Pause (whatever that means).')
        print(' z: Cycle pen color.')
        print(' a: Cycle background color.')
        print(' 0: Reset turtle position to center of screen.')
        print(' 3 through 9: n-gon.')
        print(' c: Circle.')
        print(' s: Star.')

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
                    self.help_interactive()

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
                    self.angle = 0
                    self.update()
                elif event.key == pygame.K_0:
                    self.reset()
                elif event.key == pygame.K_BACKSPACE:
                    self.clear()

                elif event.key == pygame.K_MINUS:
                    self.thickness -= 1
                    if self.thickness < 1:
                        self.thickness = 1
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    self.thickness += 1
                    if self.thickness > THICKNESS_MAX:
                        self.thickness = THICKNESS_MAX

                elif event.key == pygame.K_s:
                    self.star()
                elif event.key == pygame.K_c:
                    self.ngon(MAX_SIDES)
                elif event.key in range(pygame.K_3, pygame.K_9 + 1):
                    sides = event.key - pygame.K_0
                    self.ngon(sides)

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
        color_names = sorted(COLORS.keys())
        index = color_names.index(color) + 1
        if index >= len(color_names):
            index = 0
        new_color = color_names[index]
        return new_color

    def toggle_pen(self):
        """Toggle pen state.
        """
        self.pen = not self.pen
        LOGGER.debug('toggle_pen: pen=%s', self.pen)

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
#            length = int(self.speed * 36 / sides)
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
    parser = argparse.ArgumentParser(description='KPyTurtle.')
    parser.add_argument(
        '-L', '--loglevel', choices=LOG_LEVELS, default=DEFAULT_LOG_LEVEL,
        help='Set the logging level.')
    args = parser.parse_args()
    return args


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
    """Initialize PyGame, and thus KPyturtle.
    """
    LOGGER.debug('start: Initializing KPyturtle.')
    pygame.init()


def end(exit_code=0):
    """Quit PyGame.

    Args:
        exit_code: Numeric exit code from 0 to 255 (0 is clean exit).
    """
    LOGGER.debug('end: Ending KPyturtle.')
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
