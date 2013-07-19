#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from optparse import OptionParser, OptionGroup
from PIL import Image
from xml.dom import minidom

settings = {
    'image': "map.png",
    'info': "info.json",
}

pixel_indexes = [
    20, # (253, 253, 3)
    44, # (230, 230, 23)
    43, # (118, 117, 104)
    44, # (230, 230, 23)
    47, # (145, 145, 104)
    52, # (145, 144, 86)
    69, # (211, 211, 38)
    72, # (167, 166, 63)
    79, # (186, 188, 46)
]

def main():
    parse_args()
    validate_settings()
    update_areas()

def parse_args():
    parser = init_parser()
    options, args = parser.parse_args()

    settings['image'] = options.image or settings['image']
    settings['info'] = options.info or settings['info']

def init_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    init_parser_groups(parser)
    return parser

def init_parser_groups(parser):
    group = OptionGroup(parser, u"Input/output options")
    group.add_option(
        '--image',
        action='store',
        dest='image',
        help=u"Path to the map png image file")
    group.add_option(
        '--info',
        action='store',
        dest='info',
        help=u"Path to the map json info file")
    parser.add_option_group(group)

def validate_settings():
    validate_path(u"image", settings['image'])
    validate_path(u"info", settings['info'])

def validate_path(source_name, path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise ValueError(u"Invalid map {0} path {1}.".format(
                source_name, path))
    else:
        raise ValueError(u"Map {0} file {1} does not exist.".format(
            source_name, path))

def update_areas():
    print "Updating town areas info..."

    img = Image.open(settings['image'])
    pixels = img.load()

    with open(settings['info'], 'r') as info_file:
        info = json.load(info_file)

    for town in info['towns']:
        print "\tProcessing " + town['label']['en']
        x = int(town['pos']['x'])/100
        y = img.size[1]-int(town['pos']['y'])/100
        town['area'] = get_area((x, y), pixels, img.size)

    with open(settings['info'], 'w') as info_file:
        json.dump(info, info_file)

    print "Done"

def get_area(coords, pixels, size):
    area = 1
    radius = 1 # radius of a square, not a circle
    while radius < 20:
        chunk_area = count_pixels(coords, radius, pixels, size)
        radius += 1
        if chunk_area:
            area += chunk_area
            break
    if area > 1:
        while True:
            chunk_area = count_pixels(coords, radius, pixels, size)
            if chunk_area == 0:
                break
            area += chunk_area
            radius += 1
    return area

def count_pixels(coords, radius, pixels, size):
    left_top = (coords[0]-radius, coords[1]-radius)
    side_size = radius*2+1
    result, i, = (0, 0)

    x1 = left_top[0]
    x1 = x1 if x1 >= 0 else 0

    x2 = left_top[0]+side_size-1
    x2 = x2 if x2 < size[0] else size[0]-1

    y1 = left_top[1]
    y1 = y1 if y1 >= 0 else 0

    y2 = left_top[1]+side_size-1
    y2 = y2 if y2 < size[1] else size[1]-1

    while i < side_size:
        x = left_top[0]+i
        i += 1
        if x < 0 or x >= size[0]:
            continue
        result += check_pixel((x, y1), pixels)
        result += check_pixel((x, y2), pixels)

    i = 1
    while i < side_size-1:
        y = left_top[1]+i
        i += 1
        if y < 0 or y >= size[1]:
            continue
        result += check_pixel((x1, y), pixels)
        result += check_pixel((x2, y), pixels)

    return result

def check_pixel(coords, pixels):
    return 1 if pixels[coords] in pixel_indexes else 0

if __name__ == "__main__":
    main()
