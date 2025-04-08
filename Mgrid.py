import pygame,random
from skimage.draw import disk, line
import numpy as np
from particle import Air
class Grid:
    def __init__(self, width, height, cellsize):
        self.rows=height//cellsize
        self.columns=width//cellsize
        self.cellsize=cellsize
        self.cells = np.empty((self.rows, self.columns), dtype=object)
        self.cells[:] = np.array([[Air() for _ in range(self.columns)] for _ in range(self.rows)])
    def in_bounds(self,row,column):
        return 0 <= row < self.rows and 0 <= column < self.columns
    def draw(self, screen):
        for row in range(self.rows):
            for column in range(self.columns):
                particle=self.cells[row,column]
                if particle is not None:
                    colour=particle.colour
                    pygame.draw.rect(screen,colour,(column*self.cellsize,row*self.cellsize,self.cellsize,self.cellsize))
    def create(self, row, column, particle_type):
        if self.in_bounds(row,column) and self.check_cell(row,column):
            self.cells[row,column] = particle_type()
    def destroy(self, row, column):
        if self.in_bounds(row,column):
            self.cells[row,column] = Air()
    def check_cell(self,row,column):
        if self.in_bounds(row,column):
            return isinstance(self.cells[row, column], Air)
        return False
    def set_cell(self, row, column, particle):
        if self.in_bounds(row,column):
            self.cells[row,column] = particle
    def get_cell(self,row,column):
        if self.in_bounds(row,column):
            return self.cells[row,column]
        return None
    def clear(self):
        for row in range(self.rows):
            for column in range(self.columns):
                self.destroy(row,column)
    def swap_cell(self, row1, col1, row2, col2):
        p1 = self.get_cell(row1, col1)
        p2 = self.get_cell(row2, col2)
        self.cells[row1,col1], self.cells[row2,col2] = self.cells[row2,col2],self.cells[row1,col1]
    def replace_cell(self,row,column,newparticle):
        self.destroy(row,column)
        self.create(row,column,newparticle)
    def reset_particles(self):
        for row in range(self.rows):
            for column in range(self.columns):
                particle = self.cells[row, column]
                if particle:
                    particle.updated = False
    def act_on_other(self,grid, row, column, action):
        offset=[[0,1],[0,-1],[1,0],[-1,0]]
        acted = False
        for offsetx, offsety in offset:
            new_row, new_column = row + offsetx, column + offsety
            if self.in_bounds(new_row,new_column):
                new_cell = self.get_cell(new_row, new_column)
                if new_cell:
                    acted = action(grid, new_cell, row, column, new_row, new_column)
        return acted
    def corrode(self,p,row,column,newpart):
        p.health -= 20
        if p.health == 0:
            self.replace_cell(row,column,newpart)
    def replace_cell(self,row,column,particle):
        self.destroy(row,column)
        self.create(row,column,particle)
    def create_line(self,particle,row,column,row2,column2):
        rr,cc = line(row,column,row2,column2)
        for r, c in zip(rr, cc):
            if self.check_cell(r,c):
                self.create(r,c,particle)
    def get_line(self,particle,row,column,row2,column2):
        rr,cc = line(row,column,row2,column2)
        return rr,cc
    def create_circle(self,centre,radius,particle):
        rr,cc = disk(centre,radius)
        for r, c in zip(rr, cc):
            if self.check_cell(r,c):
                self.create(r,c,particle)   
    def create_circle_random(self,centre,radius,particle):
        rr,cc = disk(centre,radius)
        for r, c in zip(rr, cc):
            if self.check_cell(r,c) or hasattr(self.get_cell(r,c),"condensing"):
                if random.random() < 0.08:
                    self.create(r,c,particle)      
    def destroy_circle(self,centre,radius):
        rr,cc = disk(centre,radius)
        for r, c in zip(rr, cc):
            self.destroy(r,c)
    def is_covered(self,grid,row,column,exception1,exception2):
        offsets=[[0,1],[0,-1],[1,0],[-1,0],[-1,1],[1,-1],[1,1],[-1,-1]]
        covered = 0
        for x,y in offsets:
            new_row = row+x
            new_column = column+y
            if not grid.check_cell(new_row,new_column) and not isinstance(grid.get_cell(new_row,new_column), exception1) and not isinstance(grid.get_cell(new_row,new_column), exception2):
                covered += 1
        if covered >= 8:
            return True
        return False
            
        
    
