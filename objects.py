
import pygame
from constants import *


class Object:
    def __init__(self, rect, square):
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.square = square

        self.ratios = (0 if self.x == 0 else DEFAULT_SCREEN_SIZE[0] / self.x,
                       0 if self.y == 0 else DEFAULT_SCREEN_SIZE[1] / self.y,
                       DEFAULT_SCREEN_SIZE[0] / self.width, DEFAULT_SCREEN_SIZE[1] / self.height)

    def scale(self, screen_size):
        if self.square:
            self.width = min(screen_size[0] / self.ratios[2], screen_size[1] / self.ratios[3])
            self.height = min(screen_size[0] / self.ratios[2], screen_size[1] / self.ratios[3])
            self.x = screen_size[0] / self.ratios[0] + (screen_size[0] / self.ratios[2] - self.width) / 2
            self.y = screen_size[1] / self.ratios[1] + (screen_size[1] / self.ratios[3] - self.height) / 2
        else:
            self.x = 0 if self.ratios[0] == 0 else screen_size[0] / self.ratios[0]
            self.y = 0 if self.ratios[1] == 0 else screen_size[1] / self.ratios[1]
            self.width = screen_size[0] / self.ratios[2]
            self.height = screen_size[1] / self.ratios[3]


# ----------------- A circular Object -----------------
# (extends Object)
class CircleObject(Object):
    # 3 panels
    def __init__(self, color, center, thickness, radius):
        super().__init__((center[0], center[1], radius, radius), True)

        self.center = center
        self.color = color

        self.thickness = thickness
        self.radius = radius

    # Draw the item
    def draw(self, surface, selected):
        if len(self.color) < 4 or self.color[3] != 0:
            pygame.draw.circle(surface, self.color,
                              (self.x, self.y), self.radius, self.thickness)


# ----------------- A rectangular Object -----------------
# (extends Object)
class RectObject(Object):
    def __init__(self, color, rect, square, border, radius):
        super().__init__(rect, square)
        self.color = color

        self.border = border
        self.radius = radius

    def draw(self, surface, selected):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height), self.border, self.radius)
