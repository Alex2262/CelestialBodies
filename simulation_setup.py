

from cosmos import *
from constants import *
import random
import numpy as np
import pygame
import time


def weighted_random(lower_bound, upper_bound, weight):
    r = np.random.power(weight)
    rand = lower_bound + r * (upper_bound - lower_bound)
    return rand


def setup_solar_system(cosmos):
    sun = CelestialBody("Sun", 1.989e30, (0, 0), (0, 0), 6.96e8, (255, 255, 0))
    earth = CelestialBody("Earth", 5.972e24, (1.496e11, 0), (0, 29780), 6.371e6, (0, 100, 200))
    moon = CelestialBody("Moon", 7.3e22, (1.49984e11, 0), (0, 30780), 1.738e6, (100, 100, 100))
    mars = CelestialBody("Mars", 6.39e23, (2.1781e11, 0), (0, 24080), 3.3895e6, (200, 10, 10))

    cosmos.add_body(sun)
    cosmos.add_body(earth)
    cosmos.add_body(mars)
    cosmos.add_body(moon)

    view_object = earth
    dt = 60 * 10
    scale = 5e10
    # dt = 60 * 10 * 24
    # scale = 5e11

    return view_object, scale, dt


def setup_three(cosmos):
    body1 = CelestialBody("A", 5e28, (-2e9, 0), (0, -20000), 3e8, (200, 10, 10))
    body2 = CelestialBody("B", 1e28, (4e9, 0), (5100, -1930), 6e7, (10, 10, 200))
    body3 = CelestialBody("C", 2e28, (0, 5e9), (-10200, 3000), 1.4e8, (200, 200, 50))
    cosmos.add_body(body1)
    cosmos.add_body(body2)
    cosmos.add_body(body3)
    view_object = body1
    dt = 60 * 5
    scale = 2e10

    return view_object, scale, dt


def setup_multi(cosmos):
    num_bodies = 10000

    black_hole = BlackHole("SMBH", 1e33, (0, 0), (0, 0), 2e9,
                           (10, 10, 10), (240, 240, 220))
    cosmos.add_body(black_hole)

    bodies = []
    max_radius = 1e11
    min_radius = 5e9

    for i in range(num_bodies):

        r = weighted_random(min_radius, max_radius, 0.2)
        theta = random.uniform(0, 2 * math.pi)

        x = r * math.cos(theta)
        y = r * math.sin(theta)

        mass = random.uniform(1e26, 1e29)
        radius = random.uniform(1e7, 2e8)

        velocity_magnitude = math.sqrt(G_CONSTANT * black_hole.mass / r)
        velocity_angle = theta + math.pi / 2

        vx = velocity_magnitude * math.cos(velocity_angle)
        vy = velocity_magnitude * math.sin(velocity_angle)

        color = (random.randint(230, 255), random.randint(230, 255), random.randint(230, 255))

        body = CelestialBody(f"star_{i + 1}", mass, (x, y), (vx, vy), radius, color)
        bodies.append(body)
        cosmos.add_body(body)

    view_object = black_hole
    dt = 60 * 3
    scale = 4e11

    return view_object, scale, dt


