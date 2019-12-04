import os
import copy
import random
import keyboard

X = ' '
M = 10
N = 50
WALL = 'W'
DRAWDELAY = 25
UP = 'w'
DOWN = 's'
RIGHT = 'd'
LEFT = 'a'

class Vector:
    def __init__(self, i, j):
        self.i = i
        self.j = j
    
    def __add__(self, o):
        return Vector(self.i+o.i, self.j+o.j)
    
    def __repr__(self):
        return f'({self.i}, {self.j})'

    def up(self, count=1):
        return Vector(self.i-count, self.j)
    def down(self, count=1):
        return Vector(self.i+count, self.j)
    def right(self, count=1):
        return Vector(self.i, self.j+count)
    def left(self, count=1):
        return Vector(self.i, self.j-count)


class Simulation:
    # map
    # height
    # width
    # cursorpos
    # drawtime
    # overlay

    def __init__(self, M, N):
        global X
        self.height = M
        self.width = N
        self.prep()
    
    def start(self):
        self.drawing = True
        self.map_input()
        while self.drawing:
            self.draw()
        
    def prep(self):
        self.drawtime = 0
        self.map = [[X for j in range(self.width)] for i in range(self.height)]
        self.placewalls()
        pos = self.random_coordinates()
        while not self.valid(pos):
            pos = self.random_coordinates()
        self.place('P', pos)
        self.cursorpos = pos

    def random_coordinates(self):
        return Vector(random.randrange(0, M), random.randrange(0, N))
    
    def place(self, thing, vector):
        self.map[vector.i][vector.j] = thing

    def placewalls(self):
        for i in range(random.randint(1,20)):
            self.placewall(self.random_coordinates(), random.randint(0, 1))
        
    def placewall(self, vector, orientation):
        if orientation == 1:
            fr = vector.up(2)
            to = vector.down(2)
        else:
            fr = vector.left(2)
            to = vector.right(2)

        for i in range(fr.i, to.i+1):
            for j in range(fr.j, to.j+1):
                v = Vector(i, j)
                if self.valid(v):
                    self.place(WALL, v)


    def clear_screen(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def map_input(self):
        keyboard.on_release_key(UP, self.on_up)
        keyboard.on_release_key(DOWN, self.on_down)
        keyboard.on_release_key(RIGHT, self.on_right)
        keyboard.on_release_key(LEFT, self.on_left)
        keyboard.on_release_key('esc', self.on_exit)
        keyboard.on_release_key('r', self.on_reset)
    
    def on_up(self, event):
        x = self.cursorpos.up()
        if self.valid(x):
            self.cursorpos = x

    def on_down(self, event):
        x = self.cursorpos.down()
        if self.valid(x):
            self.cursorpos = x

    def on_right(self, event):
        x = self.cursorpos.right()
        if self.valid(x):
            self.cursorpos = x

    def on_left(self, event):
        x = self.cursorpos.left()
        if self.valid(x):
            self.cursorpos = x

    def on_exit(self, event):
        self.drawing = False

    def on_reset(self, event):
        self.prep()
    
    def draw(self):
        if self.drawtime % DRAWDELAY == 0:
            self.clear_screen()
            self.overlay = [[None for j in range(self.width)] for i in range(self.height)]
            self.drawcursor()

            print('-'*(self.width+2))
            for i in range(self.height):
                print('|', end='')
                for j in range(self.width):
                    if self.overlay[i][j]:
                        print(self.overlay[i][j], end='')
                    else:
                        print(self.map[i][j], end='')
                print('|')
            print('-'*(self.width+2))

            print(self.cursorpos)
            print(self.drawtime)
        self.drawtime += 1
    
    def overlayplace(self, thing, vector):
        self.overlay[vector.i][vector.j] = thing

    def drawcursor(self):
        self.overlayplace('+', self.cursorpos)

    def valid(self, vector):
        return (0 <= vector.i < self.height) and (0 <= vector.j < self.width) and not self.wall(vector)
    
    def wall(self, vector):
        return self.map[vector.i][vector.j] == WALL


if __name__ == "__main__":
    s = Simulation(M, N)
    s.start()