#!/usr/bin/env python
"""A simple turtle implementation in Python.

This is intended for both interactive sessions and keyboard control.
It came about when I was preparing a Python class and wanted to try a
few things.
"""
__author__ = 'Kevin (penniesfromkevin@)'
__copyright__ = 'Copyright (c) 2014-2015, Kevin'

import math
import sys

import pygame

FRAME_RATE = 20
BOARD_SIZE = (640, 480)
DEFAULT_SPEED = 4
DEFAULT_IMAGE = 'turtle.png'
THICKNESS_MAX = 20
DEG_TO_RAD = 0.017453293  # Converts degrees to radians.
ALPHA_COLOR = (1, 2, 3)
COLORS = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'magenta': (255, 0, 255),
        'cyan': (0, 255, 255),
        'purple': (204, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        }
COLOR_NAMES = sorted(COLORS.keys())
SETTINGS = {
        'init': False,
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
        if not SETTINGS['init']:
            print('WARNING: You should initialize PyGame first.')
            init()
            print('    For convenience, PyGame has been initialized for you.')
        pygame.sprite.Sprite.__init__(self)
        self._keys = []

        self.angle = 0
        self.color = 'red'
        self.bg_color = 'black'
        self.speed = speed
        self.thickness = 3
        self.pen = False

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

        self.board.fill(COLORS[self.bg_color])
        if self.page:
            self.board.blit(self.page, (0, 0))
        x_off = self.x_pos - self.width // 2
        y_off = self.y_pos - self.height // 2
        self.board.blit(self.image, (x_off, y_off))
        pygame.display.flip()

    def clear(self, color=None):
        """Clear the draw page with the specified color.

        Args:
            color: Name of a supported color.
        """
        self.page = pygame.Surface(self.board.get_size())
        self.page.set_colorkey(ALPHA_COLOR)
        self.page.fill(ALPHA_COLOR)
        self.update()

    def left(self, degrees=5):
        """Rotates turtle counter-clockwise.

        Args:
            degrees: Integer degrees.
        """
        self.angle -= degrees
        self.update()

    def right(self, degrees=5):
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

    def move_to(self, x_new, y_new):
        """Move from current (x, y) to new (x, y).

        Args:
            x_new: New X coordinate.
            y_new: New Y coordinate.
        """
        if self.pen:
            if self.color not in COLOR_NAMES:
                self.color = COLOR_NAMES[0]
            color = COLORS[self.color]
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
                    self.change_color()
                elif event.key == pygame.K_a:
                    self.change_bg()

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

                elif event.key == pygame.K_c:
                    self.ngon(72)
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

    def change_bg(self):
        """Change the background color (by cycling it).
        """
        self.bg_color = self.cycle_color(self.bg_color)
        self.update()

    def change_color(self):
        """Change the current turtle color (by cycling it).
        """
        self.color = self.cycle_color()

    def cycle_color(self, color=None):
        """Increment the color.

        Args:
            color: Name of a supported color.

        Returns:
            A new color name.
        """
        if color not in COLOR_NAMES:
            color = self.color
        index = COLOR_NAMES.index(color) + 1
        if index >= len(COLOR_NAMES):
            index = 0
        new_color = COLOR_NAMES[index]
        return new_color

    def toggle_pen(self):
        """Toggle pen state.
        """
        self.pen = not self.pen

    def ngon(self, sides=3, length=None):
        """Draw an N-gon, from 3 to 72 sides.

        Drawing with a number of sides that does not divide evenly into
        360, such at 7, may result in less-than-perfect polygons.

        Args:
            sides: Number of sides, from 3 to 72, inclusive.
            length: Length of each side; if this is not set, the length
                will be scaled based on speed.
        """
        if sides > 72:
            sides = 72
        elif sides < 3:
            sides = 3
        angle = 360 // sides
        if not length:
            length = int(self.speed * 36 / sides)
        for _ in range(sides):
            self.right(angle)
            self.forward(length)

    def init(self):
        """Warn wrong scope.
        """
        print('init() is a module-level command.')

    def quit(self):
        """Warn wrong scope.
        """
        print('quit() is a module-level command.')


def init():
    """Initialize PyGame.
    """
    if not SETTINGS['init']:
        pygame.init()
        SETTINGS['init'] = True
    else:
        print('PyGame already initialized.')


def quit():
    """Quit PyGame.
    """
    pygame.quit()


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
    init()
    exit_code = main()
    quit()
    sys.exit(exit_code)
