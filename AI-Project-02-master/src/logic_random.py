#!/bin/env python3
# True logic

from random import choice, shuffle
from pysat.solvers import Glucose3

class SuperInteligentPlayer():
    _viewed_vision = [[False]*10 for _ in range(10)]

    def __init__(self):
        self._model = Glucose3()
        self.__shoot_queue = []
        self._wumpus_mat = [[(i + j*10) for i in range(1, 11)]
                            for j in range(0, 10)]
        self._pit_mat = [[100 + (i + j*10) for i in range(1, 11)]
                         for j in range(0, 10)]
        self._clauses = []
        self._move_count = 0
        self.is_giving_up = False

    def reset(self):
        self.__shoot_queue.clear()
        self._clauses = []
        self._viewed_vision = [[False]*10 for _ in range(10)]
        self._model = Glucose3()
        self._move_count = 0
        self.is_giving_up = False

    def get_neighbour_of_visited(self):
        neighbor_list = []
        vision = []
        for i in range(10):
            for j in range(10):
                if (self._viewed_vision[i][j]):
                    vision.append((i, j))

        def is_valid(_x, _y):
            return _x in range(10) and _y in range(10)
        for cell in vision:
            for dx, dy in zip([0, 0, 1, -1], [1, -1, 0, 0]):
                x = cell[0] + dx
                y = cell[1] + dy
                if is_valid(x, y) and (x, y) not in neighbor_list and not self._viewed_vision[x][y]:
                    neighbor_list.append((x, y))
        return neighbor_list

    def get_viewed(self):
        vision = []
        for i in range(10):
            for j in range(10):
                if (self._viewed_vision[i][j]):
                    vision.append((i, j))
        return vision

    def expand_safezone(self, expanded):
        expanding = set(expanded.copy())

        def is_valid(_x, _y):
            return _x in range(10) and _y in range(10)
        neighbour = self.get_neighbour_of_visited()

        for cell in expanded:
            for dx, dy in zip([0, 0, 1, -1], [1, -1, 0, 0]):
                x = cell[0] + dx
                y = cell[1] + dy
                if is_valid(x, y) and ((x, y) in neighbour or self._viewed_vision[x][y]):
                    expanding.add((x, y))
        return expanding

    def optimal_path(self, _start, _end):
        from collections import deque
        q = deque()
        visited = [[False]*10 for _ in range(10)]
        visited[_start[0]][_start[1]] = True
        q.append(_start)
        path = [[-1]*10 for _ in range(10)]

        def is_valid(_x, _y):
            return _x in range(10) and _y in range(10)
        while q:
            topx, topy = q.popleft()
            if (topx, topy) == _end:
                break
            for dx, dy in zip([0, 0, 1, -1], [1, -1, 0, 0]):
                x = topx + dx
                y = topy + dy
                if is_valid(x, y) and not visited[x][y] and self.is_safe((x, y)):
                    visited[x][y] = True
                    q.append((x, y))
                    path[x][y] = (topx, topy)

        def path_get(_start, _end):
            pre = path[_end[0]][_end[1]]
            while(pre != -1 and path[pre[0]][pre[1]] != _start):
                pre = path[pre[0]][pre[1]]
            return pre
        return path_get(_start, _end)

    def is_safe(self, node):
        entailed = self.entail()
        return self.convert_wumpus(node) not in entailed and self.convert_pit(node) not in entailed

    def entail(self):
        self._model = Glucose3()
        if self._clauses:
            for clause in self._clauses:
                self._model.add_clause(clause)
            self._model.solve()
            res = self._model.get_model()
            if res:
                return res
        return []

    def convert_wumpus(self, node):
        x, y = node
        return self._wumpus_mat[x][y]

    def convert_pit(self, node):
        x, y = node
        return self._pit_mat[x][y]

    def handle_remaining_shot(self, map_object, currentPos):
        # If action queue is still there
        if self.__shoot_queue:
            if 'S' in currentPos and not self._viewed_vision[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]:
                self._clauses.append(
                    [-1*self._wumpus_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                if 'W' in map_object._map[self.__shoot_queue[-1][1][1]][self.__shoot_queue[-1][1][0]]:
                    while [self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]] in self._clauses:
                        self._clauses.remove(
                            [self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                    self._clauses.append(
                        [-1*self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                return self.__shoot_queue.pop()
            else:
                while self.__shoot_queue:
                    self.__shoot_queue.pop()
    
    def handle_pit(self, currentPos, adjacents):
        # Pit
        if 'B' in currentPos:
            if self._move_count == 0:
                print("[L] Go to cave")

                # Climb out
                return 'leave'
            for each in adjacents:
                if [-1*self._pit_mat[each[0]][each[1]]] not in self._clauses:
                    self._clauses.append([self._pit_mat[each[0]][each[1]]])
        else:
            for each in adjacents:
                while [self._pit_mat[each[0]][each[1]]] in self._clauses:
                    self._clauses.remove([self._pit_mat[each[0]][each[1]]])
                self._clauses.append([-1*self._pit_mat[each[0]][each[1]]])


    def handle_wumpus(self, map_object, currentPos, adjacents):
        # Wumpus
        if 'S' in currentPos:
            can_shoot = len(adjacents)
            if not self.__shoot_queue:
                for each in adjacents:
                    if self._viewed_vision[each[0]][each[1]] or [-1*self._wumpus_mat[each[0]][each[1]]] in self._clauses:
                        can_shoot -= 1
                        continue # I a
                    if 'W' in map_object._map[each[1]][each[0]] or can_shoot > 0:
                        self.__shoot_queue.append(
                            ('shoot', each))
                        can_shoot -= 1
                if self.__shoot_queue:
                    self._clauses.append(
                        [-1*self._wumpus_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                    # self._viewed_vision[self.__shoot_queue[-1][1]
                    # [0]][self.__shoot_queue[-1][1][1]] = True
                    if 'W' in map_object._map[self.__shoot_queue[-1][1][1]][self.__shoot_queue[-1][1][0]]:
                        while [self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]] in self._clauses:
                            self._clauses.remove(
                                [self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                        self._clauses.append(
                            [-1*self._pit_mat[self.__shoot_queue[-1][1][0]][self.__shoot_queue[-1][1][1]]])
                    return self.__shoot_queue.pop()
        else:
            for each in adjacents:
                while [self._wumpus_mat[each[0]][each[1]]] in self._clauses:
                    self._clauses.remove([self._wumpus_mat[each[0]][each[1]]])
                self._clauses.append([-1*self._wumpus_mat[each[0]][each[1]]])

    def handle_new_move(self, safety_node,adjacents,location):
        shuffle(adjacents)
        possible_move = set()
        for move in adjacents:
            if move in safety_node:
                possible_move.add(move)

        for move in possible_move:
            # if not self._viewed_vision[move[0]][move[1]]:
            print("[A] move safety", move)
            return move

        is_moved = False
        expand = set(adjacents.copy())
        pre = set()
        while not is_moved:
            pre = expand
            expand = self.expand_safezone(expand)

            if sorted(pre) == sorted(expand):
                break
                # return
            for move in expand:
                if move in safety_node:
                    possible_move.add(move)

            for move in possible_move:
                if not self._viewed_vision[move[0]][move[1]]:
                    next_move = self.optimal_path(location, move)
                    print("[A] Target ", next_move)
                    if next_move != -1:
                        print("[A] Move out of adj ", next_move)
                        is_moved = True
                        return next_move
                    
    def make_move(self, map_object):
        current = map_object.reveal()
      
        handleResult = self.handle_remaining_shot(map_object, current)
        if handleResult:
            return handleResult

        location = map_object.location()
        self._viewed_vision[location[0]][location[1]] = True
        adjacents = map_object.adjacents()

        # Pit
        handleResult = self.handle_pit(current, adjacents)
        if handleResult:
            return handleResult

        # Wumpus
        handleResult = self.handle_wumpus(map_object, current, adjacents)
        if handleResult:
            return handleResult

        # Gold
        if 'G' in current:
            return 'gold'
        
        self._move_count += 1
        safety_node = []
        entailed = self.entail() # using propositional logic to solve based on knowledge base
        if entailed:
            print("[KB] ", entailed)
            for node in self.get_neighbour_of_visited():
                if self.convert_wumpus(node) not in entailed and self.convert_pit(node) not in entailed:
                    safety_node.append(node)

        if self.is_giving_up == False:
            # If no other options
            # print("[+S] ", safety_node, len(entailed))
           handleResult =  self.handle_new_move(safety_node,adjacents,location)
           if handleResult:
            return handleResult

        self.is_giving_up = True
        init_location = map_object.init_location()
        print("[L] Go to cave")
        print("$: ", init_location, location)
        next_move = self.optimal_path(location, init_location)
        if location == init_location:
            return ('leave')
        if next_move == -1:
            return init_location
        return next_move
