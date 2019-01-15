import random
import time
from functools import partial
from itertools import chain

import requests

from utils import RGBTuple, any_range
from colors import *


def random_colors(n=255):
    return random.randint(0, n), random.randint(0, n), random.randint(0, n)


def one_of_n(value, k=3, other=0):
    if random.choice(0, k - 1) == 0:
        return value
    return other


def random_color_decay(cell) -> RGBTuple:
    if cell.alive:
        return (70, 70, 70)
    if cell.age == 1:
        return (one_of_n(20), one_of_n(20), one_of_n(20))
    if cell.age < 5:
        return tuple(map(lambda a: a // 2, cell.last_color))
    return off


def random_color(cell) -> RGBTuple:
    if cell.alive:
        return (one_of_n(40), one_of_n(40), one_of_n(40))
    return off


def rainbow_color(cell) -> RGBTuple:
    if cell.alive:
        return random.choice(rainbow)
    return off


def muted_rainbow_color(by=4) -> RGBTuple:
    def colors(cell):
        if cell.alive:
            return tuple(map(lambda a: a // by, random.choice(rainbow)))
        return off

    return colors


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

    last_color = None

    def __init__(self, alive=False, color_fn=muted_rainbow_color(by=5)):
        self.alive = alive
        self.last_color = off

        self.color_fn = partial(color_fn or Cell.color_fn, self)

    def color_fn(self):
        if self.alive:
            return (70, 70, 70)
        return off

    @property
    def color(self):
        self.last_color = self.color_fn()

        return self.last_color

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

        self.past_states = []

    def surrounding(self, x, y):
        for (cx, cy) in any_range((x - 1, y - 1), (x + 1, y + 1)):
            if cx != x or cy != y:
                yield cx % self.max_x, cy % self.max_y

    def hash_state(self):
        alive_cells = (c for c, cell in self.cells.items() if cell.alive)
        return hash(tuple(sorted(alive_cells)))

    def track_state(self, restart_if_repeated=False):

        this_state = self.hash_state()

        self.past_states = [this_state] + self.past_states[:31]

        if self.past_states.count(this_state) > 5 and restart_if_repeated:
            self.cells = random_state(40)

    def prepare(self):
        populate_queue = []

        for (x, y), cell in self.cells.items():
            if cell.alive:
                for coord in [c for c in self.surrounding(x, y) if c not in self.cells]:
                    populate_queue.append(coord)

        for c in [c for c in populate_queue if c not in self.cells]:
            self.cells[c] = Cell()

    def tick(self):
        self.prepare()

        next_state = {}
        for (x, y), cell in self.cells.items():
            surrounding = list(self.surrounding(x, y))

            neighbors = sum(self.cells.get(c, Cell()).alive for c in surrounding)
            next_state[x, y] = cell.step(neighbors)

        self.send_state(next_state)

        self.cells = {k: v for k, v in next_state.items() if v.alive or v.age < 5}

        self.track_state(restart_if_repeated=True)

    def send_state(self, state=None):
        state = state or self.cells

        all_cells = {coord: Cell() for coord in any_range((0, 0), (self.max_x - 1, self.max_y - 1))}
        all_cells.update(state)

        cells = [((x, y), c.color) for (x, y), c in all_cells.items()]

        Board.set(cells)


def random_state(k=40):
    all_cells = list(chain(any_range((0, 0), (15, 15))))
    return {c: Cell(alive=True) for c in random.sample(all_cells, k=k)}


def glider(xo=0, yo=0):
    base = (0, 0), (1, 0), (2, 0), (2, 1), (1, 2)
    return [(x + xo, y + yo) for x, y in base]


def run(x, y):
    game = Game(x, y)

    game.cells.update({c: Cell(alive=True) for c in chain(glider(), glider(4, 4), )})

    game.cells = random_state(40)

    game.send_state()
    time.sleep(.1)
    while True:
        game.tick()
        time.sleep(.02)


if __name__ == '__main__':
    try:
        run(16, 16)
    except KeyboardInterrupt:
        pass
    finally:
        Board.clear()
