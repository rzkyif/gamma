import os
import copy
import random
import keyboard
import math
import time

X = ' '
WALL = 'W'
M = 10
N = 50

DRAWDELAY = 25
DIJKSTRA = False
SEED = 25

UP = 'w'
DOWN = 's'
RIGHT = 'd'
LEFT = 'a'

class AStarQueue:
    # queue

    def __init__(self):
        self.queue = []

    def __repr__(self):
        return str(self.queue)

    def Insert(self, node):
        if self.Contain(node):
            return
        i = 0
        while i < len(self.queue):
            if DIJKSTRA:
                cmp1 = self.queue[i].cost
                cmp2 = node.cost
            else:
                cmp1 = self.queue[i].priority
                cmp2 = node.priority
            if cmp1 > cmp2:
                break
            else:
                i += 1
        if i >= len(self.queue):
            self.queue.append(node)
        else:
            self.queue.insert(i, node)
    
    def Contain(self, node):
        return any(x.pos == node.pos for x in self.queue)
    
    def Pop(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

class AStarGraph:
    def __init__(self):
        return
    
    def neighbours(self, node):
        return [node.pos.up(), node.pos.down(), node.pos.right(), node.pos.left()]

class AStarNode:
    # pos
    # cost
    # nearness
    # priority

    def __init__(self, pos, parent, start, end):
        self.pos = pos
        self.parent = parent
        self.cost = self.generate_cost(start)
        self.nearness = self.generate_nearness(end)
        self.priority = self.cost + self.nearness
    
    def __eq__(self, value):
        if value:
            return self.pos == value.pos
        else:
            return False

    def __repr__(self):
        return f'{self.pos} {self.cost} {self.nearness} {self.priority}'

    def generate_cost(self, start):
        return math.sqrt((self.pos.i-start.i)*(self.pos.i-start.i) + (self.pos.j-start.j)*(self.pos.j-start.j))

    def generate_nearness(self, end):
        return math.sqrt((end.i-self.pos.i)*(end.i-self.pos.i) + (end.j-self.pos.j)*(end.j-self.pos.j))

class Vector:
    # i
    # j

    def __init__(self, i, j):
        self.i = i
        self.j = j
    
    def __add__(self, o):
        return Vector(self.i+o.i, self.j+o.j)
    
    def __repr__(self):
        return f'({self.i}, {self.j})'

    def __eq__(self, value):
        return self.i == value.i and self.j == value.j

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
    # playerpos
    # cursorpos
    # drawtime
    # overlay

    def __init__(self, M, N):
        global X
        self.height = M
        self.width = N
        self.stop = False
        self.prep()
    
    def start(self):
        self.running = True
        self.drawing = True
        self.map_input()
        while self.running:
            if self.stop:
                self.running = False
            if self.drawing:
                self.draw()
        
    def prep(self):
        self.drawtime = 0
        self.map = [[X for j in range(self.width)] for i in range(self.height)]
        self.placewalls()
        pos = self.random_coordinates()
        while not self.valid(pos):
            pos = self.random_coordinates()
        self.playerpos = pos
        self.place('P', pos)
        self.cursorpos = pos

    def random_coordinates(self):
        return Vector(random.randrange(0, M), random.randrange(0, N))
    
    def place(self, thing, vector):
        self.map[vector.i][vector.j] = thing

    def placewalls(self):
        for i in range(random.randint(1,20)):
            orientation = random.randint(0, 1)
            self.placewall(self.random_coordinates(), orientation)
        
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
        keyboard.on_release_key('t', self.on_trace)
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

    def on_trace(self, event):
        self.astar()

    def on_exit(self, event):
        self.stop = True

    def on_reset(self, event):
        self.prep()

    def astar(self, start=None, end=None):
        if not start:
            start = self.playerpos
        if not end:
            end = self.cursorpos
        
        finishset = []
        nodeset = []
        queue = AStarQueue()
        graph = AStarGraph()

        currentnode = AStarNode(start, start, start, end)
        nodeset.append(currentnode)

        found = False
        while not found:
            for pos in graph.neighbours(currentnode):
                if pos in finishset or not self.valid(pos):
                    continue

                node = AStarNode(pos, currentnode.pos, start, end)
                queue.Insert(node)
                nodeset.append(node)

                if node.pos == end:
                    found = True
                    break
                else:
                    self.place('_', pos)
            
            finishset.append(currentnode.pos)
            currentnode = queue.Pop()
            if currentnode == None:
                break

        if found:
            pos = end
            while pos != start:
                pos = next(node.parent for node in nodeset if node.pos == pos)
                if pos != start:
                    self.place('-', pos)

        self.stop = True
    
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
    if SEED: 
        random.seed(SEED)
    s = Simulation(M, N)
    s.start()