import os
import copy
import random
import keyboard
import math
import time
from termcolor import cprint, colored, COLORS

X = '░'
WALL = '█'
CURSOR = '╳'
PATH = '▓'
CHECKED = '▒'
LEFT_TOP_CORNER = '┏'
LEFT_BOTTOM_CORNER = '┗'
RIGHT_TOP_CORNER = '┓'
RIGHT_BOTTOM_CORNER = '┛'
HORIZONTAL_LINE = '━'
VERTICAL_LINE = '┃'

M = 10
N = 50

DRAWDELAY = 25
DIJKSTRA = False
OPTIMAL = True
FIXED_COST = False
SEED = None

GOTO = [6,2]

UP = 'w'
DOWN = 's'
RIGHT = 'd'
LEFT = 'a'
TRACE = 't'
ESC = 'esc'
RESET = 'r'
GO = 'g'

class AStarQueue:
    # locals:
    #   queue

    def __init__(self):
        self.queue = []

    def __repr__(self):
        return str(self.queue)

    def Insert(self, node):
        if self.ContainBetter(node):
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
    
    def ContainBetter(self, node):
        return any(x.pos == node.pos and x.cost <= node.cost for x in self.queue)
    
    def Pop(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

class AStarGraph:
    def __init__(self):
        return
    
    def neighbors(self, node):
        return [node.pos.up(), node.pos.down(), node.pos.right(), node.pos.left()]

    def weight(self, a, b):
        return 1

class AStarNode:
    # locals:
    #   pos
    #   cost
    #   nearness
    #   priority

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
        if FIXED_COST:
            return math.sqrt((self.pos.i-start.i)*(self.pos.i-start.i) + (self.pos.j-start.j)*(self.pos.j-start.j))
        else:
            if self.parent:
                return self.parent.cost + 1
            else:
                return 0

    def generate_nearness(self, end):
        return math.sqrt((end.i-self.pos.i)*(end.i-self.pos.i) + (end.j-self.pos.j)*(end.j-self.pos.j))

class Vector:
    # locals: 
    #   i 
    #   j

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
    # locals:
    #   map
    #   height
    #   width
    #   playerpos
    #   cursorpos
    #   drawtime
    #   overlay
    #   trace

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
        self.checked = 0
        self.pathed = 0
        self.map = [[X for j in range(self.width)] for i in range(self.height)]
        self.trace = [[None for j in range(self.width)] for i in range(self.height)]
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
        keyboard.on_release_key(TRACE, self.on_trace)
        keyboard.on_release_key(ESC, self.on_exit)
        keyboard.on_release_key(RESET, self.on_reset)
        keyboard.on_release_key(GO, self.on_goto)
    
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
    
    def on_goto(self, evend):
        self.cursorpos = Vector(GOTO[0], GOTO[1])

    def astar(self, start=None, end=None):
        if not start:
            start = self.playerpos
        if not end:
            end = self.cursorpos

        self.trace = [[None for j in range(self.width)] for i in range(self.height)]
        self.checked = 0
        self.pathed = 0
        
        finishset = []
        nodeset = []
        queue = AStarQueue()
        graph = AStarGraph()

        currentnode = AStarNode(start, None, start, end)
        nodeset.append(currentnode)

        found = False
        while not found:
            for pos in graph.neighbors(currentnode):
                if not self.valid(pos):
                    continue

                node = AStarNode(pos, currentnode, start, end)

                i = next((i for i, x in enumerate(nodeset) if (x.pos == node.pos and x.cost > node.cost)), None)
                if i:
                    nodeset.insert(i, node)
                else:
                    if not any(x.pos == node.pos for x in nodeset):
                        nodeset.append(node)

                if pos in finishset:
                    continue

                queue.Insert(node)

                if not OPTIMAL:
                    if node.pos == end:
                        found = True
                        break

                if node.pos != end:
                    self.mark_checked(pos)

            finishset.append(currentnode.pos)
            currentnode = queue.Pop()

            if OPTIMAL:
                if currentnode.pos == end:
                    found = True
                    break
        
        if found:
            pos = end
            while pos != start:
                pos = next(node.parent.pos for node in nodeset if node.pos == pos)
                if pos != start:
                    self.mark_path(pos)

        time.sleep(1)
        self.stop = True
    
    def draw(self):
        if self.drawtime % DRAWDELAY == 0:
            self.clear_screen()
            self.overlay = [[None for j in range(self.width)] for i in range(self.height)]
            self.drawcursor()

            if self.pathed > 0:
                print(colored(str(self.pathed), 'green'), 'steps required,', colored(str(self.checked), 'yellow'), 'nodes checked.')

            print(LEFT_TOP_CORNER + HORIZONTAL_LINE*(self.width) + RIGHT_TOP_CORNER)
            for i in range(self.height):
                print(VERTICAL_LINE, end='')
                for j in range(self.width):
                    if self.overlay[i][j]:
                        print(self.overlay[i][j], end='')
                    else:
                        if self.trace[i][j]:
                            print(self.trace[i][j], end='')
                        else:
                            print(self.map[i][j], end='')
                print(VERTICAL_LINE)
            print(LEFT_BOTTOM_CORNER + HORIZONTAL_LINE*(self.width) + RIGHT_BOTTOM_CORNER)
            
            print(self.playerpos, end=' -> ')
            print(self.cursorpos, end=' ')
            print(self.version(), '\n')
        self.drawtime += 1
    
    def overlayplace(self, thing, vector):
        self.overlay[vector.i][vector.j] = thing

    def drawcursor(self):
        self.overlayplace(CURSOR, self.cursorpos)
    
    def mark_checked(self, pos):
        self.trace[pos.i][pos.j] = colored(CHECKED, 'yellow')
        self.checked += 1

    def mark_path(self, pos):
        self.trace[pos.i][pos.j] = colored(PATH, 'green')
        self.pathed += 1
    
    def version(self):
        return (colored('DIJKSTRA', 'red') if DIJKSTRA else colored('ASTAR', 'green')) + ' ' + (colored('OPTIMAL', 'green') if OPTIMAL else colored('FIRST', 'red')) + ' ' + (colored('FIXED_COST', 'red') if FIXED_COST else colored('GENERATED_COST', 'green'))

    def valid(self, vector):
        return (0 <= vector.i < self.height) and (0 <= vector.j < self.width) and not self.wall(vector)
    
    def wall(self, vector):
        return self.map[vector.i][vector.j] == WALL


if __name__ == "__main__":
    if SEED: 
        random.seed(SEED)
    s = Simulation(M, N)
    s.start()