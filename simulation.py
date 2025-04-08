import pygame, os, sys, math, random,skimage.draw
from Mgrid import Grid
from particle import *
from particle import Particle
class Simulation:
    def __init__(self, width, height, cellsize):
        self.grid = Grid(width, height, cellsize)
        self.cellsize=cellsize
        self.materials=[
            "sand","rock","steel","platinum","wood","ice","water","steam","acid","flammablegas","fire","smoke","lava","nitrogen","oil"]
        self.materialsclass=[
            Sand,Rock,Steel,Platinum,Wood,Ice,Water,Steam,Acid,FlammableGas,Fire,Smoke,Lava,Nitrogen,Oil]
        self.selected = Sand
        self.createtypes=["randomcircle","circle"]
        self.createmode = 0
        self.mode=self.materials[0]
        self.brushradius = 3
        self.scroll = 0
        self.pos = [0,0]
        self.oldpos = [0,0]
    def draw(self,screen):
        self.grid.draw(screen)
        self.drawbrush(screen)
    def destroy(self, row, column):
        self.grid.destroy(row, column)
    def update(self):
        for row in range(self.grid.rows,-1,-1):
            if row % 2 ==0:
                colrange=range(self.grid.columns)
            else:
                colrange = reversed(range(self.grid.columns))
            for column in colrange:
                particle = self.grid.get_cell(row,column)
                if particle is not None:
                    new_pos=particle.update(self.grid, row, column)
                    if new_pos != (row,column):
                        self.grid.set_cell(new_pos[0],new_pos[1],particle)
                        self.grid.destroy(row,column)
    def restart(self):
        self.grid.clear()
    def handlecontrols(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.handlekey(event)
            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1 and self.brushradius < 3000:
                    self.brushradius += 1
                if event.y == -1 and self.brushradius > 1:
                    self.brushradius -= 1
        self.handlemouse()
    def handlekey(self, event):
        match event.key:
            case pygame.K_SPACE:
                self.restart()
            case pygame.K_1:
                if self.scroll != 0:
                    self.scroll -= 1
                    self.mode=self.materials[self.scroll]
            case pygame.K_2:
                if self.scroll < len(self.materials)-1:
                    self.scroll += 1
                    self.mode=self.materials[self.scroll]
            case pygame.K_3:
                self.mode = "eraser"
            case pygame.K_q:
                if self.createmode != 0:
                    self.createmode -= 1
            case pygame.K_w:
                if self.createmode != len(self.createtypes)-1:
                    self.createmode += 1
    def handlemouse(self):
        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            self.pos=pygame.mouse.get_pos()
            row = self.pos[1]//self.cellsize
            column = self.pos[0]//self.cellsize
            self.pos=(row,column)
            self.applybrush(self.oldpos,self.pos)
            self.oldpos=self.pos
        else:
            cupos = pygame.mouse.get_pos()
            row = cupos[1]//self.cellsize
            column = cupos[0]//self.cellsize
            self.oldpos = (row,column)

    def applybrush(self,oldpos,pos):
            r0, c0 = oldpos
            r1, c1 = pos
            particle_class = self.materialsclass[self.scroll]
            temp_particle = particle_class()
            rr, cc = self.grid.get_line(particle_class,r0, c0, r1, c1)
            for r, c in zip(rr, cc):
                cpos = (r,c)
                if self.mode == "eraser":
                    self.grid.destroy_circle(cpos,self.brushradius)
                else:
                    if not temp_particle.static and self.brushradius > 1:
                        match self.createtypes[self.createmode]:
                            case "randomcircle":
                                self.grid.create_circle_random(cpos,self.brushradius,particle_class)
                            case "circle":
                                self.grid.create_circle(cpos,self.brushradius,particle_class)
                    else:
                        self.grid.create_circle(cpos,self.brushradius,particle_class)

    def drawbrush(self, screen):
        mousepos=pygame.mouse.get_pos()
        column=mousepos[0]//self.cellsize
        row=mousepos[1]//self.cellsize
        rr, cc = skimage.draw.circle_perimeter(row, column, self.brushradius, shape=(self.grid.rows, self.grid.columns))
        for r, c in zip(rr, cc):
            x = c * self.cellsize
            y = r * self.cellsize
            pygame.draw.rect(screen, (255, 255, 255), (x, y, self.cellsize, self.cellsize))