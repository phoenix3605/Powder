import pygame
import skimage.draw
class Grid:
    def __init__(self, width, height, cellsize):
        self.rows=height//cellsize
        self.columns=width//cellsize
        self.cellsize=cellsize
        self.cells=[[None for _ in range(self.columns)] for _ in range(self.rows)]
    def in_bounds(self,row,column):
        return True if 0 <= row < self.rows and 0 <= column < self.columns else False
    def draw(self, screen):
        for row in range(self.rows):
            for column in range(self.columns):
                particle=self.cells[row][column]
                if particle is not None:
                    colour=particle.colour
                    pygame.draw.rect(screen,colour,(column*self.cellsize,row*self.cellsize,self.cellsize,self.cellsize))
    def create(self, row, column, particle_type):
        if self.in_bounds(row,column) and self.check_cell(row,column):
            self.cells[row][column] = particle_type()
    def destroy(self, row, column):
        if self.in_bounds(row,column):
            self.cells[row][column] = None
    def check_cell(self,row,column):
        if self.in_bounds(row,column):
            if self.cells[row][column] == None:
                return True
        return False
    def set_cell(self, row, column, particle):
        if not (0 <= row < self.rows and 0 <= column < self.columns):
            return
        self.cells[row][column] = particle
    def get_cell(self,row,column):
        if self.in_bounds(row,column):
            return self.cells[row][column]
        return None
    def clear(self):
        for row in range(self.rows):
            for column in range(self.columns):
                self.destroy(row,column)
    def swap_cell(self, row1, col1, row2, col2):
        p1 = self.get_cell(row1, col1)
        p2 = self.get_cell(row2, col2)
        self.cells[row1][col1], self.cells[row2][col2] = self.cells[row2][col2],self.cells[row1][col1]
    def replace_cell(self,row,column,newparticle):
        self.destroy(row,column)
        self.create(row,column,newparticle)
    def reset_particles(self):
        for row in self.cells:
            for particle in row:
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
        rr,cc = skimage.draw.line(row,column,row2,column2)
        for r, c in zip(rr, cc):
            if self.check_cell(r,c):
                self.create(r,c,particle)
    def get_line(self,particle,row,column,row2,column2):
        rr,cc = skimage.draw.line(row,column,row2,column2)
        return rr,cc
    def create_circle(self,centre,radius,particle):
        rr,cc = skimage.draw.disk(centre,radius)
        for r, c in zip(rr, cc):
            if self.check_cell(r,c):
                self.create(r,c,particle)      
    def destroy_circle(self,centre,radius,particle):
        rr,cc = skimage.draw.disk(centre,radius)
        for r, c in zip(rr, cc):
            self.destroy(r,c)
    
