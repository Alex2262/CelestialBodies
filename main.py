
from cosmos import *
from constants import *
from simulation_setup import *

import pygame
import time

MAX_FPS = 120


def main():
    # ----------------- Initializing Pygame Variables -----------------
    pygame.init()
    clock = pygame.time.Clock()  # Clock for adjusting the frames per second

    screen_size = DEFAULT_SCREEN_SIZE
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    screen.fill(SCREEN_COLOR)
    pygame.display.set_caption("life")
    #

    cosmos = Cosmos()

    view_object, scale, dt = setup_three(cosmos)
    zoom_scale = scale
    zoom_min = max(scale / 1e2, 1)
    zoom_max = scale * 1e3

    celestial_bodies = cosmos.bodies

    past_stable_center = [(screen_size[0] // 2), (screen_size[1] // 2)]
    curr_stable_center = [(screen_size[0] // 2), (screen_size[1] // 2)]

    # tick = 0
    # start_time = time.time()

    holding = False
    start_hold = (0, 0)
    start_hold_time = 0
    hold_velocity = [0, 0]

    running = True
    while running:

        # ----------------- Looping through Pygame Events -----------------
        for event in pygame.event.get():

            # Quit Pygame
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.VIDEORESIZE:
                # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen_size = screen.get_size()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if not holding:
                    holding = True
                    start_hold = mouse_pos
                    past_stable_center = curr_stable_center
                    start_hold_time = pygame.time.get_ticks()

            # ----------------- Mouse Released -----------------
            if event.type == pygame.MOUSEBUTTONUP:
                if holding:
                    mouse_pos = pygame.mouse.get_pos()
                    curr_stable_center = [(mouse_pos[0] - start_hold[0]) * HOLD_SCALAR + past_stable_center[0],
                                          (mouse_pos[1] - start_hold[1]) * HOLD_SCALAR + past_stable_center[1]]

                    past_stable_center = curr_stable_center

                    hold_time = max((pygame.time.get_ticks() - start_hold_time) / 10.0, 0.01)

                    hold_velocity = [
                        (mouse_pos[0] - start_hold[0]) * HOLD_SCALAR / hold_time,
                        (mouse_pos[1] - start_hold[1]) * HOLD_SCALAR / hold_time,
                    ]

                holding = False

            # ----------------- Mouse Scroll -----------------
            if event.type == pygame.MOUSEWHEEL:
                y_comp = event.y

                zoom_mag = zoom_scale / 1e2
                zoom_scale += zoom_mag * -y_comp
                zoom_scale = min(zoom_scale, zoom_max)
                zoom_scale = max(zoom_scale, zoom_min)

        if holding:
            mouse_pos = pygame.mouse.get_pos()
            curr_stable_center = [(mouse_pos[0] - start_hold[0]) * HOLD_SCALAR + past_stable_center[0],
                                  (mouse_pos[1] - start_hold[1]) * HOLD_SCALAR + past_stable_center[1]]

        curr_stable_center[0] += hold_velocity[0]
        curr_stable_center[1] += hold_velocity[1]
        hold_velocity[0] *= HOLD_VELOCITY_SCALAR
        hold_velocity[1] *= HOLD_VELOCITY_SCALAR

        cosmos.update(dt)

        # print(curr_stable_center)

        if view_object is not None:
            view_center = get_gui_position(view_object.position, zoom_scale,
                                           curr_stable_center)

        else:
            view_center = get_gui_position((0, 0), zoom_scale, curr_stable_center)

        screen.fill(SCREEN_COLOR)
        draw_body_trails(screen, celestial_bodies, zoom_scale, view_center)
        draw_body_velocities(screen, celestial_bodies, zoom_scale, view_center)
        draw_body_forces(screen, celestial_bodies, zoom_scale, view_center)
        draw_celestial_bodies(screen, celestial_bodies, zoom_scale, view_center)

        clock.tick(MAX_FPS)

        print("FPS:", clock.get_fps())

        pygame.display.update()

    pygame.quit()


def draw_celestial_bodies(surface, celestial_bodies, scale, view_center):
    for celestial_body in celestial_bodies:
        celestial_body.draw(surface, scale, view_center)


def draw_body_trails(surface, celestial_bodies, scale, view_center):
    for celestial_body in celestial_bodies:
        celestial_body.draw_trail(surface, scale, view_center)


def draw_body_velocities(surface, celestial_bodies, scale, view_center):
    for celestial_body in celestial_bodies:
        celestial_body.draw_velocity(surface, scale, view_center)


def draw_body_forces(surface, celestial_bodies, scale, view_center):
    for celestial_body in celestial_bodies:
        celestial_body.draw_forces(surface, scale, view_center)


if __name__ == "__main__":
    main()

