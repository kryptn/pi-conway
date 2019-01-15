import random
import time
from collections import defaultdict
from itertools import chain
from typing import Generator, Tuple

import requests

white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 200)
off = (0, 0, 0)
pink = (255, 0, 144)

AnyDimensionalTuple = Tuple[int, ...]
ndt = AnyDimensionalTuple


def any_range(c1: ndt, c2: ndt) -> Generator[ndt, None, None]:
    assert len(c1) == len(c2)
    x, c1 = c1[0], c1[1:]
    y, c2 = c2[0], c2[1:]

    lower, upper = [(x, y), (y, x)][x > y]

    for n in range(lower, upper + 1):
        if not (c1 and c2):
            yield (n,)
        else:
            for down in any_range(c1, c2):
                yield (n, *down)


def random_colors():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


class Board:
    _url = 'http://192.168.1.146:5555'

    _set = f'{_url}/set'
    _fill = f'{_url}/fill'
    _clear = f'{_url}/clear'

    @staticmethod
    def set(colors):
        return requests.post(Board._set, json={'pixels': colors})

    @staticmethod
    def fill(color):
        return requests.post(Board._fill, json={'color': color})

    @staticmethod
    def clear():
        return requests.post(Board._clear)


class Cell:
    alive = False
    age = 0
    total_age = 0

    def __init__(self, alive=False):
        self.alive = alive

    @property
    def color(self):
        if self.alive:
            return random_colors()
        # if self.age == 1:
        #     return (150, 0, 0)
        # if self.age == 2:
        #     return (100, 0, 0)
        # if self.age == 3:
        #     return (50, 0, 0)
        return off
        # if self.alive and self.total_age == 0:
        #     return green
        # if self.alive:
        #     return blue
        # return off

    def step(self, neighbors):
        start_state = self.alive

        alive_states = {
            (True, 3): True,
            (True, 2): True,
            (False, 3): True
        }

        next_cell = Cell()
        next_cell.alive = alive_states.get((self.alive, neighbors), False)
        next_cell.age = self.age + 1 if start_state == self.alive else 1
        next_cell.total_age = self.age + 1

        return next_cell


class Game:
    cells = {}

    def __init__(self, x, y):
        self.cells = {}
        self.max_x = x
        self.max_y = y

    def surrounding(self, x, y):
        for (cx, cy) in any_range((x - 1, y - 1), (x + 1, y + 1)):
            if cx != x or cy != y:
                yield cx % self.max_x, cy % self.max_y

    def prepare(self):
        populate_queue = []

        for (x, y), cell in self.cells.items():
            if cell.alive:
                for coord in [c for c in self.surrounding(x, y) if c not in self.cells]:
                    populate_queue.append(coord)

        for c in [c for c in populate_queue if c not in self.cells]:
            self.cells[c] = Cell()
        # print('added ', len(populate_queue), ' new cells')

    def tick(self):
        # print('total cells: ', len(self.cells))
        self.prepare()

        next_state = {}
        for (x, y), cell in self.cells.items():
            surrounding = list(self.surrounding(x, y))
            # print((x, y), surrounding)
            neighbors = sum(self.cells.get(c, Cell()).alive for c in surrounding)
            next_state[x, y] = cell.step(neighbors)

        self.send_state(next_state)

        self.cells = {k: v for k, v in next_state.items() if v.alive}

    def send_state(self, state=None):
        state = state or self.cells

        all_cells = {coord: Cell() for coord in any_range((0, 0), (self.max_x - 1, self.max_y - 1))}
        all_cells.update(state)

        cells = [((x, y), c.color) for (x, y), c in all_cells.items()]

        Board.set(cells)


def run(x, y):
    game = Game(x, y)

    glider = (         (13, 4),
                                (14, 3),
              (12, 2), (13, 2), (14, 2))

    second = ((x-8, y+3) for x, y in glider)
    third = ((x - 1, y + 7) for x, y in glider)
    fourth = ((x - 9, y + 8) for x, y in glider)

    for c in chain(glider, second, third, fourth):
        game.cells[c] = Cell(alive=True)

    game.send_state()
    time.sleep(.1)
    while True:
        game.tick()
        time.sleep(.1)


if __name__ == '__main__':
    try:
        run(16, 16)
    except KeyboardInterrupt:
        Board.clear()
