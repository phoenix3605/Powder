import pygame
from simulation import Simulation
WIDTH=1200
HEIGHT=600
CELLSIZE=8
BG = (0,0,0)
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
    screen.fill(BG)
    simulation.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    pygame.display.set_caption(f"{simulation.mode} {simulation.createtypes[simulation.createmode]} {simulation.brushradius} {int(clock.get_fps())} || 1/2 -> materials | q/w -> brush type | 3 -> Eraser | Scroll Wheel -> brush size | Space -> reset")