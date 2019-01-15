import requests


class HttpBoard:
    _url = 'http://192.168.1.146:5555'

    _set = '{_url}/set'.format(_url=_url)
    _fill = '{_url}/fill'.format(_url=_url)
    _clear = '{_url}/clear'.format(_url=_url)

    @staticmethod
    def set(colors):
        return requests.post(HttpBoard._set, json={'pixels': colors})

    @staticmethod
    def fill(color):
        return requests.post(HttpBoard._fill, json={'color': color})

    @staticmethod
    def clear():
        return requests.post(HttpBoard._clear)


class PiBoard:

    def __init__(self, pin, num, brightness=0.2, auto_write=False):
        import neopixel
        self.pixels = neopixel.NeoPixel(pin, num, brightness=0.2, auto_write=False)

    async def init(self, app):
        app['pixels'] = self

    def clean(self, app):
        self.fill((0,0,0))
        self.pixels.deinit()

    @staticmethod
    def xy_to_board(x, y):
        x = x % 16
        y = y % 16

        return y * 16 + (15 - x if y % 2 else x)

    def set(self, colors):
        for coord, color in colors:
            pos = PiBoard.xy_to_board(*coord)
            self.pixels[pos] = tuple(color)

        self.pixels.show()

    def fill(self, color):
        self.pixels.fill(tuple(color))

    def clear(self):
        self.pixels.fill((0, 0, 0))
