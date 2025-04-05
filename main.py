import pygame
from simulation import Simulation
WIDTH=1200
HEIGHT=600
CELLSIZE=8
GREY = (29,29,29)
FPS=60
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
simulation = Simulation(WIDTH,HEIGHT,CELLSIZE)
clock = pygame.time.Clock()
running=True
while running:
    simulation.grid.reset_particles()
    simulation.handlecontrols()
    simulation.update()
    screen.fill(GREY)
    simulation.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    pygame.display.set_caption(f"{simulation.mode} {simulation.brushradius} || 1/2 -> materials | 3 -> Eraser | Scroll Wheel -> brush size | Space -> reset")