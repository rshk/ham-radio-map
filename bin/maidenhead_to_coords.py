import re
import sys
from collections import namedtuple
from functools import partial

BoundingBox = namedtuple('BoundingBox', 'lon,lat,minlon,maxlon,minlat,maxlat')


RE_MAIDENHEAD_LOCATOR = re.compile(
    r'^'
    r'(?P<g1>[a-r]{2})'
    r'(?P<g2>[0-9]{2})'
    r'(?P<g3>[a-x]{2})'

    r'((?P<g4>[0-9]{2})'
    r'((?P<g5>[a-x]{2})'
    r'((?P<g6>[0-9]{2})'
    r'((?P<g7>[a-x]{2})'

    r'(?P<g8>[0-9]{2})?'

    r')?'  # g7
    r')?'  # g6
    r')?'  # g5
    r')?'  # g4

    r'$')


def parse(locator):
    m = RE_MAIDENHEAD_LOCATOR.match(locator.lower())
    if m:
        return (
            m.group('g1'),
            m.group('g2'),
            m.group('g3'),
            m.group('g4'),
            m.group('g5'),
            m.group('g6'),
            m.group('g7'),
            m.group('g8'))
    raise ValueError('Bad locator: {}'.format(locator))


class _MaidenheadDecoder:

    def __init__(self):
        pass

    def initialize(self):
        self.minlon = -180
        self.maxlon = 180
        self.minlat = -90
        self.maxlat = 90
        self.square_size_lon = 360
        self.square_size_lat = 180

    def decode_alpha(self, xy, base):
        self.square_size_lon /= base
        self.square_size_lat /= base

        rawx, rawy = xy
        x = (ord(rawx) - ord('a'))
        y = (ord(rawy) - ord('a'))
        assert 0 <= x < base
        assert 0 <= y < base

        self.minlon += x * self.square_size_lon
        self.maxlon = self.minlon + self.square_size_lon
        self.minlat += y * self.square_size_lat
        self.maxlat = self.minlat + self.square_size_lat

    def decode_num(self, xy):
        x = int(xy[0])
        y = int(xy[1])

        self.square_size_lon /= 10
        self.square_size_lat /= 10

        self.minlon += x * self.square_size_lon
        self.maxlon = self.minlon + self.square_size_lon
        self.minlat += y * self.square_size_lat
        self.maxlat = self.minlat + self.square_size_lat

    def decode(self, locator):
        self.initialize()

        pairs = parse(locator)

        decoders = [
            partial(self.decode_alpha, base=18),
            self.decode_num,
            partial(self.decode_alpha, base=24),
            self.decode_num,
            partial(self.decode_alpha, base=24),
            self.decode_num,
            partial(self.decode_alpha, base=24),
            self.decode_num]

        for decoder, pair in zip(decoders, pairs):
            if not pair:
                break
            decoder(pair)

        return BoundingBox(
            lon=(self.minlon + self.maxlon) / 2,
            lat=(self.minlat + self.maxlat) / 2,
            minlon=self.minlon, maxlon=self.maxlon,
            minlat=self.minlat, maxlat=self.maxlat)


def decode(locator):
    """Decode a maidenhead locator to coordinates bounding box
    """

    return _MaidenheadDecoder().decode(locator)


def main(args):
    for locator in args:
        try:
            decoded = decode(locator)
        except Exception as exc:
            print(str(exc))
        else:
            print(locator, f'{decoded.lat},{decoded.lon}')


if __name__ == '__main__':
    main(sys.argv[1:])
