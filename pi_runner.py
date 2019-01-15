import board

from boards import PiBoard
from conway import runner

if __name__ == '__main__':
    pi = PiBoard(board.D18, num=256)
    runner(16, 16, pi)

    pi.clear()
