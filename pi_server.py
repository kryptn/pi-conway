import asyncio
from collections import namedtuple

from aiohttp import web

import board
from boards import PiBoard


router = web.RouteTableDef()


@router.post('/set')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    payload = await request.json()

    pixels = payload.get('pixels', [])

    board.set(pixels)

    return web.json_response({'ok': True})


@router.post('/clear')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    board.fill((0, 0, 0))

    return web.json_response({'ok': True})


@router.post('/fill')
async def set_pixel(request: web.Request) -> web.Response:
    board = request.app['pixels']

    payload = await request.json()

    board.fill(tuple(payload['color']))

    return web.json_response({'ok': True})


def create_app(loop=None):
    app = web.Application()

    pb = PiBoard(pin=board.D18, num=256)

    app.on_startup.append(pb.init)
    app.on_cleanup.append(pb.clean)

    app.router.add_routes(router)

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5555)
