import random,colorsys
class Particle:
    def __init__(self,huer=None, satr=None, valr=None):
        self.updated = False
        self.density = 1
        self.velocity = [[0,0],[0,0]]
        self.gravity = self.density/5
        self.max_velocity = 10
        self.temperature = 20
        self.static = False
        self.moved = False
        self.flammability = 0
        self.corrodable = True
        self.health = 100
        self.conductive = False
        if huer and satr and valr:
            self.colour = self.randomcolour(huer, satr, valr)
    def randomcolour(self,huer,satr,valr):
        hue = random.uniform(*huer)
        saturation = random.uniform(*satr)
        value = random.uniform(*valr)
        r,g,b = colorsys.hsv_to_rgb(hue,saturation,value)
        return int(r*255),int(g*255),int(b*255)
    def update(self, grid, row, column):
        return row,column
    def apply_gravity(self):
        self.velocity[0][1] += self.gravity
        self.velocity[0][1] = min(self.velocity[0][1], self.max_velocity)

class PowderParticle:
    def __init__(self):
        self.inertialresistance = 0.1
        self.hardness = 1
        self.left = [0,0]
    def update(self, grid, row, column):
        return self.apply_movement_powder(grid,row,column)
    def apply_movement_powder(self,grid,row,column):
        if self.updated:
            return row, column
        self.apply_gravity()
        was_moved = self.moved
        self.moved = False

        max_fall = int(self.velocity[0][1])
        for step in range(1,max_fall+2):
            new_row = row + step
            if not grid.check_cell(new_row,column):
                break
            row=new_row
            self.moved=True
        if self.moved:
            self.updated = True
            return row, column

        l,r = grid.get_cell(row, column - 1),grid.get_cell(row, column + 1)
        if (self.freefall == False and (l and hasattr(l, "freefall") and l.freefall) or (r and hasattr(r, "freefall") and r.freefall) and random.random()>self.inertialresistance):
            self.freefall = True
        elif not was_moved:
            self.freefall = False

        if self.freefall:
            offset=[-1,1]
            random.shuffle(offset)
            for offsets in offset:
                new_column=column+offsets
                if grid.check_cell(row+1, new_column) and grid.check_cell(row,new_column) and self.freefall:
                    self.moved=True
                    self.updated = True
                    return row+1,new_column
                
        below=grid.get_cell(row + 1, column)
        if below and below.density < self.density and not getattr(below, "static", False):
            grid.swap_cell(row, column, row + 1, column)
            self.moved=True
            self.updated = True
            return row, column
        
        if self.velocity[1][1] > 0:
            if self.left[1]==0:
                self.left[0] = min(int(self.velocity[1][1]),5)
                offset=[self.left[0],-self.left[0]]
                self.left[1]=random.choice(offset)
            for offsets in range(abs(self.left[1])):
                direction = 1 if self.left[1] > 0 else -1
                new_column = column + direction
                if grid.check_cell(row, new_column):
                    if self.left[1] > 0:
                        self.left[1]-=1
                    elif self.left[1] < 0:
                        self.left[1] += 1
                    self.velocity[0][0]=offsets
                    self.moved=True
                    self.updated = True
                    self.velocity[1]=self.velocity[0]
                    self.velocity[0] = [0,0]
                    return row,new_column
                break

                    
        self.velocity[1]=self.velocity[0]
        self.velocity[0] = [0,0]
        return row,column

class LiquidParticle:
    def update(self, grid, row, column):
        return self.apply_movement_liquid(grid,row,column)
    def apply_movement_liquid(self,grid,row,column):
        self.apply_gravity()
        new_row = row + int(self.velocity[0][1])
        if self.updated:
            return row, column
        cord = [row, column]
        for step in range(1, int(self.velocity[0][1])+2):
            new_row = row + step
            if not grid.check_cell(new_row,column):
                break
            cord = [new_row,column]
        if cord != [row,column]:
            self.moved=True
            self.updated = True
            return (cord[0],cord[1])
        for _ in range(5):   
            new_column=column+random.choice([-1, 1])
            if grid.check_cell(row+1, new_column):
                self.updated = True
                return row+1,new_column
            new_column=column+random.choice([-1, 1])
            if grid.check_cell(row, new_column):
                self.updated = True
                return row,new_column
        below=grid.get_cell(row + 1, column)
        if below and below.density < self.density and not getattr(below, "static", False):
            grid.swap_cell(row, column, row + 1, column)
            self.updated = True
            return row, column
        return row,column

class GasParticle:
    def update(self, grid, row, column):
        return self.apply_movement_gas(grid,row,column)
    def apply_movement_gas(self,grid,row,column):
        if self.updated:
            return row, column
        if grid.check_cell(row-1,column):
            self.updated = True
            return row-1,column
        for _ in range(5):   
            new_column = [column - 1, column + 1]
            random.shuffle(new_column)
            if grid.check_cell(row-1, new_column[0]):
                self.updated = True
                return row-1,new_column[0]
            if grid.check_cell(row, new_column[1]):
                self.updated = True
                return row,new_column[1]
            
        below=grid.get_cell(row - 1, column)
        if below and below.density < self.density and not getattr(below, "static", False):
            grid.swap_cell(row, column, row - 1, column)
            self.updated = True
            return row, column
        p = grid.get_cell(row, new_column[0])
        if hasattr(p,"density") and hasattr(p,"apply_movement_gas"):
            if p.density < self.density:
                grid.swap_cell(row,column,row,new_column[0])
                self.updated = True
        p = grid.get_cell(row, new_column[1])
        if hasattr(p,"density") and hasattr(p,"apply_movement_gas"):
            if p.density < self.density:
                grid.swap_cell(row,column,row,new_column[1])
                self.updated = True
        return row,column
    
class Rock(Particle):
    def __init__(self):
        super().__init__((0.0,0.1),(0.1,0.3),(0.3,0.5))
        self.density=2000
        self.static = True
    def update(self, grid, row, column):
        return Particle.update(self, grid, row, column)
    
class Sand(Particle, PowderParticle):
    def __init__(self):
        Particle.__init__(self, (0.1,0.12), (0.5,0.7), (0.7,0.9))
        PowderParticle.__init__(self)
        self.density=1602
        self.moved = False
        self.freefall = True
        self.colour = self.randomcolour((0.1,0.12),(0.5,0.7),(0.7,0.9))
        self.inertialresistance = 0.2
        self.friction = 2
    def update(self, grid, row, column):
        return PowderParticle.update(self, grid, row, column)

class Water(Particle, LiquidParticle):
    def __init__(self):
        super().__init__((0.5,0.62),(0.5,0.7),(0.6,0.8))
        self.density=998
        self.temperature = 5
        self.colour = (17, 50, 61)
    def update(self, grid, row, column):
        if self.temperature < 1:
            pass
        return LiquidParticle.update(self, grid, row, column)
        
    
class Steam(Particle, GasParticle):
    def __init__(self):
        super().__init__((0,0),(0,0),(0.9,1))
        self.corrodable = False
        self.density=0.6
    def update(self, grid, row, column):
        return GasParticle.update(self, grid, row, column)
    
class Fire(Particle):
    def __init__(self):
        super().__init__((0,0),(0,0),(0.9,1))
        self.temperature = 1000
        self.lifetime = 100
    def update(self, grid, row, column):
        return Particle.update(self, grid, row, column)
class Acid(Particle,LiquidParticle):
    def __init__(self):
        super().__init__()
        self.colour = (75, 186, 71)
        self.corrodecount=0
        self.density = 1149
        self.corrodable = False
    def corrode(self,row,column):
        pass
    @staticmethod
    def corrodeacid(grid,p,row,column, r, c):
        if hasattr(p,"corrodable"):
            if p.corrodable and not isinstance(p, Acid):
                grid.corrode(p,r,c,FlammableGas)
                return True
        return False
    def update(self, grid, row, column):
        if grid.act_on_other(grid,row,column,self.corrodeacid) == True:
            self.corrodecount +=1
            if self.corrodecount == 4:
                grid.destroy(row,column)
                self.corrodecount = 0
        return LiquidParticle.update(self, grid, row, column)
class FlammableGas(Particle,GasParticle):
    def __init__(self):
        super().__init__((0.37,0.38),(0.13,0.14),(0.17,0.18))
        self.flammability = 100
        self.density = 1.49
    def update(self, grid, row, column):
        return GasParticle.update(self, grid, row, column)