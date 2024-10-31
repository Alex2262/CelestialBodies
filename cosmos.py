
import math
import numpy as np
from numba import njit, prange

from objects import *
from constants import *
from pygame.examples.go_over_there import MIN_SPEED


def get_gui_position(position, scale, view_center):
    x = position[0] / scale * WIDTH - view_center[0]
    y = position[1] / scale * HEIGHT - view_center[1]
    return x, y


def draw_arrow(screen, start, angle, color, thickness, length):

    y_length = math.sin(angle) * length
    x_length = math.cos(angle) * length

    angle_perpendicular = angle + math.pi / 2

    end = (start[0] + x_length, start[1] + y_length)

    triangle_ratio = 0.1
    triangle_width_ratio = 0.5

    # Ensure nice looking triangle proportional
    # side_ratio = triangle_ratio * (2 ** 0.5) * length

    optimal_size = length * triangle_ratio

    triangle_width = optimal_size * triangle_width_ratio

    midpoint_x = (1 - triangle_ratio) * length * math.cos(angle) + start[0]
    midpoint_y = (1 - triangle_ratio) * length * math.sin(angle) + start[1]

    triangle = (end,

                # Vertices from midpoint of the base of the triangle
                (midpoint_x + triangle_width * math.cos(angle_perpendicular),
                 midpoint_y + triangle_width * math.sin(angle_perpendicular)),
                (midpoint_x - triangle_width * math.cos(angle_perpendicular),
                 midpoint_y - triangle_width * math.sin(angle_perpendicular)))

    # print(start, end, (midpoint_x, midpoint_y), triangle)

    pygame.draw.line(screen, color, start, (midpoint_x, midpoint_y), thickness)  # Draw line
    pygame.draw.polygon(screen, color, triangle, 0)  # Draw triangle


class CelestialBody:
    def __init__(self,
                 name: str,
                 mass: float,
                 position: tuple[float, float],
                 velocity: tuple[float, float],
                 radius: float,
                 color: tuple[int, int, int]):

        self.radius = radius
        # print(name)

        self.color = color

        self.name = name
        self.mass = mass
        self.position = position  # A tuple (x, y)
        self.position_prev = position
        self.velocity = velocity  # A tuple (vx, vy)
        self.acceleration = (0, 0)
        self.acceleration_computed = False

        self.trail = []
        self.net_force = (0, 0)

    def update_position(self, dt):
        self.trail.append(self.position)

        self.position = (self.position[0] + self.velocity[0] * dt,
                         self.position[1] + self.velocity[1] * dt)

        if len(self.trail) > 5000:
            self.trail.pop(0)

    def update_position_verlet(self, dt):

        self.trail.append(self.position)

        self.position_prev = self.position

        self.position = (
            self.position[0] + self.velocity[0] * dt + 0.5 * self.acceleration[0] * dt ** 2,
            self.position[1] + self.velocity[1] * dt + 0.5 * self.acceleration[1] * dt ** 2,
        )

        if len(self.trail) > 5000:
            self.trail.pop(0)

    def taper_color(self):
        speed = math.sqrt((self.velocity[0] ** 2) + (self.velocity[1] ** 2))
        speed = max(min(speed, MAX_SPEED), MIN_SPEED)
        t_speed = (speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)

        # print(t_speed)
        red = int(50 - (50 * t_speed))
        green = int(80 + (240 - 80) * t_speed)
        blue = int(250 - (30 * t_speed))

        return red, green, blue

    def draw(self, surface, scale, view_center):
        g_radius = int(max((min(self.radius / scale * WIDTH, self.radius / scale * HEIGHT)), 1))
        x, y = get_gui_position(self.position, scale, view_center)
        x = int(x)
        y = int(y)

        # print(self.name, g_radius, (x, y))

        tapered_color = self.taper_color()

        if g_radius == 1:
            surface.set_at((x, y), tapered_color)
        else:
            pygame.draw.circle(surface, tapered_color,
                                (x, y), g_radius, 0)

    def draw_trail(self, surface, scale, view_center):

        screen_size = surface.get_size()
        for trail_position in self.trail:
            tx, ty = get_gui_position(trail_position, scale, view_center)

            if tx < 0 or tx >= screen_size[0] or ty < 0 or ty >= screen_size[1]:
                continue

            pygame.draw.circle(surface, (self.color[0] // 5 + 200, self.color[1] // 5 + 200, self.color[2] // 5 + 200),
                               (tx, ty), 1, 0)

    def draw_velocity(self, surface, scale, view_center):
        magnitude = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        angle = math.atan(abs(self.velocity[1] / self.velocity[0]))

        if self.velocity[1] < 0 and self.velocity[0] < 0:
            angle += math.pi
        elif self.velocity[1] < 0:
            angle = 2 * math.pi - angle
        elif self.velocity[0] < 0:
            angle = math.pi - angle

        # print(self.velocity, magnitude, angle)
        arrow_length = math.sqrt(magnitude / scale * 1e10)
        # print(magnitude, scale, arrow_length)

        draw_arrow(surface, get_gui_position(self.position, scale, view_center), angle,
                   (self.color[0] / 2 + 120, self.color[1] / 2 + 120, self.color[2] / 2 + 120),
                   2, arrow_length)

    def draw_forces(self, surface, scale, view_center):
        gui_position = get_gui_position(self.position, scale, view_center)

        screen_size = surface.get_size()

        if gui_position[0] < 0 or gui_position[0] >= screen_size[0] or \
                gui_position[1] < 0 or gui_position[1] >= screen_size[1]:
            return

        for force in (self.net_force,):
            magnitude = math.sqrt(force[0] ** 2 + force[1] ** 2)
            den = 1e-10 if force[0] == 0 else force[0]
            angle = math.atan(abs(force[1] / den))

            if force[1] < 0 and force[0] < 0:
                angle += math.pi
            elif force[1] < 0:
                angle = 2 * math.pi - angle
            elif force[0] < 0:
                angle = math.pi - angle

            # order = int(math.log(magnitude, 10))
            # print(magnitude, order)
            arrow_length = math.sqrt(magnitude / scale / 3e13)
            # print(arrow_length)

            draw_arrow(surface, gui_position, angle,
                       (self.color[0] // 5 + 200, self.color[1] // 5 + 200, self.color[2] // 5 + 200),
                       2, arrow_length)


class BlackHole(CelestialBody):
    def __init__(self,
                 name: str,
                 mass: float,
                 position: tuple[float, float],
                 velocity: tuple[float, float],
                 radius: float,
                 color1: tuple[int, int, int],
                 color2: tuple[int, int, int]):

        super().__init__(name, mass, position, velocity, radius, color1)
        self.color2 = color2

    def draw(self, surface, scale, view_center):
        g_radius = (min(self.radius / scale * WIDTH, self.radius / scale * HEIGHT) + 1)
        o_radius = g_radius + 2  # border outline

        x, y = get_gui_position(self.position, scale, view_center)

        pygame.draw.circle(surface, self.color2, (x, y), o_radius, 0)
        pygame.draw.circle(surface, self.color,(x, y), g_radius, 0)


def compute_gravitational_force(body1: CelestialBody, body2: CelestialBody):
    dx = body2.position[0] - body1.position[0]
    dy = body2.position[1] - body1.position[1]

    distance_squared = dx ** 2 + dy ** 2
    softened_distance_squared = distance_squared + EPSILON ** 2
    softened_distance = math.sqrt(softened_distance_squared)

    force = G_CONSTANT * body1.mass * body2.mass / softened_distance_squared
    force_x = force * dx / softened_distance
    force_y = force * dy / softened_distance

    return force_x, force_y


def update_velocity(body: CelestialBody, net_force: tuple[float, float], dt: int):

    ax = net_force[0] / body.mass
    ay = net_force[1] / body.mass

    body.velocity = (body.velocity[0] + ax * dt, body.velocity[1] + ay * dt)
    body.acceleration = (ax, ay)


def update_velocity_verlet(body: CelestialBody, net_force: tuple[float, float], dt: int):

    """

    Verlet Integration method

    Error of O(dt^-3)

    """

    ax = net_force[0] / body.mass
    ay = net_force[1] / body.mass

    body.velocity = (
        body.velocity[0] + 0.5 * (body.acceleration[0] + ax) * dt,
        body.velocity[1] + 0.5 * (body.acceleration[1] + ay) * dt,
    )

    body.acceleration = (ax, ay)


def update_velocity_rk4(body: CelestialBody, forces: list[tuple[float, float]], dt: int):

    """

    Runge Kutta 4 method

    Error of O(dt^-5) and accumulated error across all steps that
    scales as O(dt^-4)

    Runge Kutta 4 equations:

    k1 = dt * evaluate(t, y)
    k2 = dt * evaluate(t + 0.5*dt, y + 0.5*k1)
    k3 = dt * evaluate(t + 0.5*dt, y + 0.5*k2)
    k4 = dt * evaluate(t + dt, y + k3)

    """

    ax = sum([f[0] for f in forces]) / body.mass
    ay = sum([f[1] for f in forces]) / body.mass


def compute_forces(positions, masses):

    # numpy matrix broadcasting
    # ~10x faster than basic force calculations

    delta_r = positions[np.newaxis, :, :] - positions[:, np.newaxis, :]  # (n, n, 2)

    softened_distance = np.sqrt(np.sum(delta_r ** 2, axis=2)) + EPSILON
    softened_distance_squared = softened_distance ** 2

    mass_product = masses[:, np.newaxis] * masses[np.newaxis, :]  # (n, n)

    force_magnitudes = G_CONSTANT * mass_product / softened_distance_squared  # (n, n)
    unit_directions = delta_r / softened_distance[:, :, np.newaxis]  # (n, n, 2)

    forces = force_magnitudes[:, :, np.newaxis] * unit_directions  # (n, n, 2)

    net_forces = np.sum(forces, axis=1)  # (n, 2)

    return net_forces


@njit(parallel=True)
def compute_forces_numba(positions, masses):

    # using numba jit compiling and parallelization,
    # ~10x faster than numpy matrix broadcasting

    n = positions.shape[0]
    net_forces = np.zeros((n, 2), dtype=np.float64)

    for i in prange(n):
        for j in range(i + 1, n):
            dx = positions[j, 0] - positions[i, 0]
            dy = positions[j, 1] - positions[i, 1]
            softened_distance_squared = dx * dx + dy * dy + EPSILON * EPSILON
            softened_distance = np.sqrt(softened_distance_squared)
            force = G_CONSTANT * masses[i] * masses[j] / softened_distance_squared

            fx = force * dx / softened_distance
            fy = force * dy / softened_distance

            net_forces[i, 0] += fx
            net_forces[i, 1] += fy

            net_forces[j, 0] -= fx
            net_forces[j, 1] -= fy

    return net_forces


class Cosmos:
    def __init__(self):
        self.bodies = []
        self.computed_forces = np.zeros((1, 2))

    def add_body(self, body):
        self.bodies.append(body)

    def update(self, dt: int):

        num_bodies = len(self.bodies)

        positions = np.array([body.position for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])

        self.computed_forces = compute_forces_numba(positions, masses)
        for i in range(num_bodies):
            self.bodies[i].net_force = tuple(self.computed_forces[i])

        for body in self.bodies:
            if not body.acceleration_computed:
                update_velocity(body, body.net_force, dt)
                body.update_position(dt)
                body.acceleration_computed = True
            else:
                update_velocity_verlet(body, body.net_force, dt)
                body.update_position_verlet(dt)

