import asyncio
from collections import namedtuple

import board
import neopixel
from aiohttp import web
from aiojobs.aiohttp import setup, spawn
from aiojobs import create_scheduler

num_pixels = 256

router = web.RouteTableDef()


def xy_to_board_order(x, y):
    x = x % 16
    y = y % 16

    return y * 16 + (15 - x if y % 2 else x)


@router.post('/set')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    payload = await request.json()

    pixels = payload.get('pixels', [])

    for pixel in pixels:
        coord, color = pixel
        pos = xy_to_board_order(*coord)
        board[pos] = tuple(color)

        # print('set {} to {}'.format(pos, board[pos]))

    board.show()
    # print('board.showed')

    return web.json_response({'ok': True})


@router.post('/clear')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    board.fill((0, 0, 0))
    board.show()

    return web.json_response({'ok': True})


@router.post('/fill')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    payload = await request.json()

    board.fill(tuple(payload['color']))
    board.show()

    return web.json_response({'ok': True})


async def init_neopixel(app):
    pixel_pin = board.D18
    app['pixels'] = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)


async def clean_neopixel(app):
    board = app['pixels']
    board.fill((0, 0, 0))
    board.show()
    board.deinit()


def create_app(loop=None):
    app = web.Application()

    app.on_startup.append(init_neopixel)
    app.on_cleanup.append(clean_neopixel)

    app.router.add_routes(router)

    return app


if __name__ == '__main__':
    app = create_app()
    setup(app)
    web.run_app(app, host='0.0.0.0', port=5555)
