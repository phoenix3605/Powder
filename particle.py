import random,colorsys
class Particle:
    def __init__(self,huer=None, satr=None, valr=None):
        self.updated = False
        self.density = 1
        self.velocity = [[0,0],[0,0]]
        self.gravity = self.density/5
        self.max_velocity = 10
        self.static = False
        self.moved = False
        self.corrodable = True
        self.health = 100
        self.conductive = False
        self.ignitiontemp = 5000
        self.tempresistance = 0.3
        self.temperature = 20
        self.melting = 100
        if huer and satr and valr:
            self.colour = self.randomcolour(huer, satr, valr)
    def randomcolour(self,huer,satr,valr):
        hue = random.uniform(*huer)
        saturation = random.uniform(*satr)
        value = random.uniform(*valr)
        r,g,b = colorsys.hsv_to_rgb(hue,saturation,value)
        return int(r*255),int(g*255),int(b*255)
    def update(self, grid, row, column):
        self.transfer_heat(grid,row,column)
        return row,column
    def apply_gravity(self,grid,row,column):
        if grid.check_cell(row+1,column):
            self.velocity[0][1] += self.gravity
            self.velocity[0][1] = min(self.velocity[0][1], self.max_velocity)
    def ignite(self,grid,row,column,particle):
        if self.temperature > self.ignitiontemp and random.random()<0.05:
            grid.replace_cell(row,column,particle)
    def melt(self,grid,row,column,newparticle):
        if self.temperature > self.melting and random.random() < (0.001*self.temperature):
            grid.replace_cell(row,column,newparticle)
    def transfer_heat(self, grid, row, column):
        ccell = grid.get_cell(row,column)
        acells =[(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in acells:
             r, c = row + dr, column + dc
             if grid.in_bounds(r,c):
                acell = grid.get_cell(r, c)
                if acell and hasattr(acell, 'temperature'):
                    diff = self.temperature - acell.temperature
                    transfer = diff * acell.tempresistance
                    if ccell == Lava or ccell == Nitrogen:
                        self.temperature -= transfer
                    else:
                        self.temperature -= transfer
                    acell.temperature += transfer

class Air(Particle):
    def __init__(self):
        super().__init__()
        self.colour = (0,0,0)
        self.temperature = 20.0
    def update(self, grid, row, column):
        if self.temperature > 20:
            self.temperature -= (self.temperature - 20) * 0.01
        self.transfer_heat(grid, row, column)
        return row, column
class PowderParticle:
    def __init__(self):
        self.inertialresistance = 0.1
        self.hardness = 1
        self.left = [0,0]
    def update(self, grid, row, column):
        self.transfer_heat(grid, row, column)
        return self.apply_movement_powder(grid,row,column)
    def apply_movement_powder(self,grid,row,column):
        if self.updated:
            return row, column
        self.apply_gravity(grid,row,column)
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
    def __init__(self):
        self.dispersionrate = 5
        self.boiling = 0
        self.freezing = 0
    def update(self, grid, row, column):
        self.transfer_heat(grid, row, column)
        return self.apply_movement_liquid(grid,row,column)
    def boil(self,grid,row,column,newparticle):
        if self.temperature > self.boiling and random.random()<0.4:
            if newparticle:
                grid.replace_cell(row,column,newparticle)
            else:
                grid.destroy(row,column)
    def freeze(self,grid,row,column,newparticle):
        if self.temperature < self.freezing and random.random()<0.4:
            grid.replace_cell(row,column,newparticle)
    def apply_movement_liquid(self,grid,row,column):
        new_row = row + int(self.velocity[0][1])
        if self.updated:
            return row, column
        self.apply_gravity(grid,row,column)
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
        for _ in range(self.dispersionrate):   
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
        adjs = random.choice([(row, column-1),(row, column+1)])
        adj = grid.get_cell(row,adjs[1])
        if adj and adj.density < self.density and not getattr(adj, "static", False):
            grid.swap_cell(row,column,row,adjs[1])
        return row,column

class GasParticle:
    def __init__(self):
        self.condensing = 100
    def update(self, grid, row, column):
        self.transfer_heat(grid, row, column)
        return self.apply_movement_gas(grid,row,column)
    def condense(self,grid,row,column,newparticle):
        if self.temperature < self.condensing and random.random() < (0.01*(1/self.temperature)):
            grid.replace_cell(row,column,newparticle)
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
            
        above=grid.get_cell(row - 1, column)
        if above and above.density < self.density and hasattr(above, "apply_movement_gas"):
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
        self.tempresistance = 0.1
        self.melting = 2000
    def update(self, grid, row, column):
        self.melt(grid,row,column,Lava)
        return Particle.update(self, grid, row, column)
    
class Platinum(Particle):
    def __init__(self):
        super().__init__()
        self.colour = (255, 255, 255)
        self.density=2000
        self.static = True
        self.tempresistance = 0.1
        self.corrodable = False
    def update(self, grid, row, column):
        return Particle.update(self, grid, row, column) 
    
class Steel(Particle):
    def __init__(self):
        super().__init__()
        self.density=10000
        self.static = True
        self.tempresistance = 0.8
    def update(self, grid, row, column):
        temp = self.temperature
        if temp < 100:
            r = g = b = int(180 - (temp / 300) * 60) 
        elif temp < 300:
            t = (temp - 300) / 300
            r = int(120 + t * 60)
            g = int(50 - t * 10)
            b = int(50 - t * 10)
        elif temp < 600:
            t = (temp - 600) / 200
            r = int(180 + t * 75)
            g = int(40 + t * 20)
            b = int(40 + t * 20)
        elif temp < 1000:
            t = (temp - 800) / 200
            r = 255
            g = int(60 + t * 80)
            b = int(60 - t * 60)
        else:
            t = min((temp - 1000) / 500, 1)
            r = 255
            g = int(140 + t * 80)
            b = int(60 + t * 120)
        self.colour = tuple(max(0, min(255, c)) for c in (r, g, b))
        return Particle.update(self, grid, row, column)
class Wood(Particle):
    def __init__(self):
        super().__init__((0.02,0.06),(0.5,0.6),(0.12,0.18))
        self.density=400
        self.ignitiontemp = 200
        self.tempresistance = 0.1
        self.static = True
    def update(self, grid, row, column):
        self.ignite(grid,row,column,Fire)
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

class Ice(Particle):
    def __init__(self):
        super().__init__((0.5,0.6),(0.78,0.82),(0.7,0.75))
        self.density=100
        self.melting = 10
        self.static = True
        self.tempresistance = 0.1
    def update(self, grid, row, column):
        self.melt(grid,row,column,Water)
        return Particle.update(self, grid, row, column) 
class Water(Particle, LiquidParticle):
    def __init__(self):
        Particle.__init__(self)
        LiquidParticle.__init__(self)
        self.dispersionrate = 3
        self.tempresistance = 0.1
        self.boiling = 100
        self.freezing = 0
        self.density=998
        self.colour = (17, 50, 61)
    def update(self, grid, row, column):
        self.freeze(grid,row,column,Ice)
        self.boil(grid,row,column,Steam)
        return LiquidParticle.update(self, grid, row, column)
class Steam(Particle, GasParticle):
    def __init__(self):
        super().__init__((0,0),(0,0),(0.9,1))
        self.corrodable = False
        self.density=0.6
        self.temperature = 150
        self.condensing = 80
    def update(self, grid, row, column):
        self.condense(grid,row,column,Water)
        return GasParticle.update(self, grid, row, column)
    
class Acid(Particle,LiquidParticle):
    def __init__(self):
        Particle.__init__(self)
        LiquidParticle.__init__(self)
        self.dispersionrate = 1
        self.colour = (75, 186, 71)
        self.corrodecount=0
        self.density = 1149
        self.corrodable = False
    def corrode(self,row,column):
        pass
    @staticmethod
    def corrodeacid(grid,p,row,column, r, c):
        if hasattr(p,"corrodable"):
            if p.corrodable and not isinstance(p, Acid) and not isinstance(p, Air):
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
        self.ignitiontemp = 60
    def update(self, grid, row, column):
        self.ignite(grid,row,column,Fire)
        return GasParticle.update(self, grid, row, column)
    
class Fire(Particle):
    def __init__(self):
        super().__init__((0.03,0.15),(0.9,1),(0.9,1))
        self.temperature = 900
        self.lifetime = random.randint(10,100)
        self.density = 0.3
    def update(self, grid, row, column):
        self.temperature = min(self.temperature+100,900)
        self.transfer_heat(grid, row, column)
        self.colour = self.randomcolour((0.03,0.15),(0.9,1),(0.9,1))
        if self.lifetime <=0 or grid.is_covered(grid,row,column,Fire,Smoke) or self.temperature < 100:
            grid.replace_cell(row,column,Smoke)
        self.lifetime -= 1

        return row,column
class Smoke(Particle,GasParticle):
    def __init__(self):
        super().__init__((0.37,0.38),(0.13,0.14),(0.17,0.18))
        self.density = 0.05
        self.lifetime = 200
        self.lifetimecol = 200
        self.isember = True if random.random()<0.05 else False
        if self.isember:
            self.temperature = 900
    def update(self, grid, row, column):
        self.lifetime -= 1
        t = max(self.lifetime / self.lifetimecol, 0)
        if self.isember:
            self.colour = self.randomcolour((0.03,0.15),(0.9,1),(0.9,1))
            self.temperature = min(600,self.temperature+100)
            self.transfer_heat(grid,row,column)
        else:
            self.colour = (38*t,38*t,38*t)
        if self.lifetime <=0:
            grid.destroy(row,column)
        if self.updated:
            return row, column
        x = random.random()
        if grid.check_cell(row-1,column) and random.random() < 0.6:
            if x<0.1:
                self.updated = True
                return row-1,column
            else:
                return row,column
        for _ in range(5):   
            new_column = [column - 1, column + 1]
            random.shuffle(new_column)
            if grid.check_cell(row-1, new_column[0]):
                self.updated = True
                return row-1,new_column[0]
            if grid.check_cell(row, new_column[1]):
                self.updated = True
                return row,new_column[1]
        return row,column
class Lava(Particle, LiquidParticle):
    def __init__(self):
        Particle.__init__(self)
        LiquidParticle.__init__(self)
        self.temperature = 3000
        self.dispersionrate = 1
        self.tempresistance = 0.3
        self.boiling = 8000
        self.freezing = 600
        self.density=3100
        self.colour = (255, 42, 0)
    def update(self, grid, row, column):
        if self.temperature < 2500:
            self.temperature += 200
        self.freeze(grid,row,column,Rock)
        return LiquidParticle.update(self, grid, row, column)
class Nitrogen(Particle, LiquidParticle):
    def __init__(self):
        Particle.__init__(self)
        LiquidParticle.__init__(self)
        self.temperature = -200
        self.dispersionrate = 1
        self.tempresistance = 0.3
        self.boiling = -100
        self.density=800
        self.colour = (191, 254, 255)
    def update(self, grid, row, column):
        self.temperature = max(self.temperature - 100, -200)
        self.boil(grid,row,column,None)
        return LiquidParticle.update(self, grid, row, column)
class Oil(Particle,LiquidParticle):
    def __init__(self):
        Particle.__init__(self)
        LiquidParticle.__init__(self)
        self.dispersionrate = 3
        self.density=825
        self.ignitiontemp = 150
        self.colour = (94, 74, 49)
    def update(self, grid, row, column):
        self.ignite(grid,row,column,Fire)
        return LiquidParticle.update(self, grid, row, column)