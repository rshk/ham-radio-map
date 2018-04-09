import csv
import json
import os
import re
import sys
from collections import namedtuple

import lxml
import lxml.html
import requests

from maidenhead_to_coords import decode as maidenhead_decode

PAGE_URL = 'http://www.irts.ie/cgi/repeater.cgi'
USER_AGENT = 'Mozilla/5.0'
CACHE_FILE = '/tmp/irts-repeaters.html'
RE_FREQUENCY = re.compile(r'Output:\s*(.*)Input:\s*(.*)')
RE_LOCATOR = re.compile(r'[A-R]{2}[0-9]{2}[A-X]{2}')

Record = namedtuple('Record', (
    'callsign', 'channel', 'freqout', 'freqin', 'access', 'loc_name',
    'locator', 'lat', 'lon', 'notes'))


def _message(text):
    print(f'\x1b[32m{text}\x1b[0m', file=sys.stderr)


def get_page_data():
    if os.path.exists(CACHE_FILE):
        _message('Using cached data from {}'.format(CACHE_FILE))
        with open(CACHE_FILE, 'r') as fp:
            return fp.read()
    data = _get_page_data()
    with open(CACHE_FILE, 'w') as fp:
        fp.write(data)
    return data


def _get_page_data():
    _message('Fetching page data from {}'.format(PAGE_URL))
    resp = requests.get(PAGE_URL, headers={'User-agent': USER_AGENT})
    assert resp.ok
    return resp.content.decode()


def parse_page_data(raw_content):
    html = lxml.html.fromstring(raw_content)
    table, = html.xpath('//table')
    rows = table.xpath('//tr')[1:]

    for row in rows:
        tdchannel, tdfreq, tdcall, tdacc, tdloc, tdnotes = row

        channel = tdchannel.text_content()
        callsign = tdcall.text_content()
        freqout, freqin = (
            int(float(x) * 1e6)
            for x in RE_FREQUENCY.match(tdfreq.text_content()).groups())
        access = tdacc.text_content()

        locparts = list(tdloc.itertext())
        loc_name = re.sub(r'\s+', ' ', ' '.join(locparts[:-1])).strip()
        locator = locparts[-1]

        notes = ' '.join(tdnotes.itertext())

        location = maidenhead_decode(locator)

        yield Record(
            callsign, channel, freqout, freqin, access, loc_name, locator,
            location.lat, location.lon, notes)


if __name__ == '__main__':
    raw_content = get_page_data()
    records = parse_page_data(raw_content)

    output = {
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature',
             'geometry': {
                 'type': 'Point',
                 'coordinates': [row.lon, row.lat],
             },
             'properties': {
                 'callsign': row.callsign,
                 'channel': row.channel,
                 'freqout': row.freqout,
                 'freqin': row.freqin,
                 'access': row.access,
                 'loc_name': row.loc_name,
                 'locator': row.locator,
                 'notes': row.notes,
             }}
            for row in records
        ],
    }

    json.dump(output, sys.stdout)
