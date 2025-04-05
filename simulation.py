import pygame, os, sys, math, random
from Mgrid import Grid
from particle import *
class Simulation:
    def __init__(self, width, height, cellsize):
        self.grid = Grid(width, height, cellsize)
        self.cellsize=cellsize
        self.materials=["sand","rock","water","steam","acid","flammablegas","fire"]
        self.materialsclass=[Sand,Rock,Water,Steam,Acid,FlammableGas,Fire]
        self.mode=self.materials[0]
        self.brushradius = 3
        self.selected = Sand
        self.scroll = 0
    def draw(self,screen):
        self.grid.draw(screen)
        self.drawbrush(screen)
    def create(self, row, column):
        particle = self.materialsclass[self.scroll]
        cparticle=particle()
        if random.random() < 0.15 or cparticle.static == True or self.brushradius == 1 or self.mode=="eraser":
            self.grid.create(row,column,particle)
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
                if self.scroll < len(self.materials)-2:
                    self.scroll += 1
                    self.mode=self.materials[self.scroll]
            case pygame.K_3:
                self.mode = "eraser"
    def handlemouse(self):
        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            pos=pygame.mouse.get_pos()
            row = pos[1]//self.cellsize
            column = pos[0]//self.cellsize
            self.applybrush(row,column)
    def applybrush(self,row,column):
        for r in range(self.brushradius):
            for c in range(self.brushradius):
                rrow = row + r
                ccolumn = column + c
                if self.mode == "eraser":
                    self.destroy(rrow,ccolumn)
                else:
                    self.create(rrow,ccolumn)
    def drawbrush(self, screen):
        mousepos=pygame.mouse.get_pos()
        column=mousepos[0]//self.cellsize
        row=mousepos[1]//self.cellsize
        brushvisualsize=self.brushradius*self.cellsize
        col=(255,255,255)
        pygame.draw.rect(screen,col,(column*self.cellsize,row*self.cellsize,brushvisualsize,brushvisualsize))
