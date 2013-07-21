#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import Image
import math
import os

from optparse import OptionParser, OptionGroup
from xml.dom import minidom

settings = {
    'image': "map.png",
    'info': "info.json",
}

town_colors = [
    # for old maps
    (253, 253, 3),
    (230, 230, 23),
    (211, 211, 38),
    (167, 166, 63),
    (186, 188, 46),
    # for new maps
    (255, 255, 0),
    (227, 227, 0),
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

    img = Image.open(settings['image']).convert('RGB')
    data = img.load()

    with open(settings['info'], 'r') as info_file:
        info = json.load(info_file)

    get_primary_areas(info, data, img.size)
    remove_geographical_labels_from_towns(info)
    fix_unrecognized_areas(data, img.size, info['towns'])
    convert_town_areas(info['towns'])

    with open(settings['info'], 'w') as info_file:
        json.dump(info, info_file)

    print "Done"

def get_primary_areas(info, data, size):
    if not 'labels' in info:
        info['labels'] = []
    for town in info['towns']:
        x = int(town['pos']['x'])/100
        y = size[1] - int(town['pos']['y'])/100

        if x <0 or x > size[0] or y < 0 or y > size[1]:
            print "Removing {0} town.".format(town['label']['en'])
            info['towns'].remove(town)
            continue

        print "Calculating {0} area.".format(town['label']['en'])
        area, pos = get_area((x, y), data, size)
        if area:
            town['area'] = area
            update_town_pos(town, pos, size)
        else:
            info['labels'].append(town)

def get_area(start_pos, data, size):
    if data[start_pos] in town_colors:
        coords = start_pos
    else:
        coords = find_nearest_color_point(town_colors, start_pos, data, size)
    if coords:
        area, coords = get_filled_area(
            town_colors, (255, 0, 0), coords, data, size)
    else:
        area = []
    return area, coords

def find_nearest_color_point(colors, coords, data, size, max_radius=10):
    radius = 1
    point = None
    while radius < max_radius:
        point = get_first_color_point_on_edge(
            colors, coords, radius, data, size)
        if point:
            break
        radius += 1
    return point

def get_first_color_point_on_edge(colors, coords, radius, data, size):
    left_top = (coords[0]-radius, coords[1]-radius)
    side_size = radius*2+1

    x1 = left_top[0]
    x1 = x1 if x1 >= 0 else 0

    x2 = left_top[0]+side_size-1
    x2 = x2 if x2 < size[0] else size[0]-1

    y1 = left_top[1]
    y1 = y1 if y1 >= 0 else 0

    y2 = left_top[1]+side_size-1
    y2 = y2 if y2 < size[1] else size[1]-1

    i = 0
    while i < side_size:
        x = left_top[0]+i
        i += 1
        if x < 0 or x >= size[0]:
            continue

        p = (x, y1)
        if data[p] in colors:
            return p
        p = (x, y2)
        if data[p] in colors:
            return p

    i = 1
    while i < side_size-1:
        y = left_top[1]+i
        i += 1
        if y < 0 or y >= size[1]:
            continue

        p = (x1, y)
        if data[p] in colors:
            return p
        p = (x2, y)
        if data[p] in colors:
            return p

    return None

def get_filled_area(colors, fill_color, start_pos, data, size):
    area = []
    to_fill = []
    to_fill.append(start_pos)

    while to_fill:
        (x, y) = to_fill.pop()
        if data[(x, y)] not in colors:
            continue
        data[(x, y)] = fill_color
        area.append((x, y))

        to_fill.append((x-1, y))
        to_fill.append((x+1, y))
        to_fill.append((x, y-1))
        to_fill.append((x, y+1))

    center = get_area_center(area, size)
    return area, center

def remove_geographical_labels_from_towns(info):
    for label in info['labels']:
        if label in info['towns']:
            info['towns'].remove(label)
        if 'area' in label:
            del label['area']

def fix_unrecognized_areas(data, size, towns):
    print "Fixing unrecognized areas"
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            if data[x, y] in town_colors:
                color = (0, 0, 255)
                area, center = get_filled_area(
                    town_colors, color, (x, y), data, size)

                if looks_like_road(area, color, data):
                    continue

                print "Got {0} area at {1}".format(len(area), center)

                min_distanse = math.sqrt(size[0]**2+size[1]**2)
                nearest_town = None
                for town in towns:
                    distanse = math.sqrt(
                        (center[0]-(town['pos']['x']/100))**2 +
                        (center[1]-(size[1]-(town['pos']['y']/100)))**2)
                    if distanse > 500:
                        continue
                    for p1 in town['area']:
                        for p2 in area:
                            distanse = math.sqrt(
                                (p1[0]-p2[0])**2 +
                                (p1[1]-p2[1])**2)
                            if distanse < min_distanse:
                                min_distanse = distanse
                                nearest_town = town
                    if min_distanse > 30:
                        continue
                    for p in area:
                        data[p] = (255, 0, 0)
                    town['area'].extend(area)
                    center = get_area_center(town['area'], size)
                    update_town_pos(town, center, size)

def looks_like_road(area, supposed_color, data):
    border_points = 0
    for p in area:
        if (data[p[0]-1, p[1]-1] != supposed_color
        or data[p[0], p[1]-1] != supposed_color
        or data[p[0]+1, p[1]-1] != supposed_color

        or data[p[0]-1, p[1]] != supposed_color
        or data[p[0]+1, p[1]] != supposed_color

        or data[p[0]-1, p[1]+1] != supposed_color
        or data[p[0], p[1]+1] != supposed_color
        or data[p[0]+1, p[1]+1] != supposed_color):
            border_points += 1

    road_like = (float(border_points)/len(area)) > 0.9

    if road_like:
        for p in area:
            data[p] = (0, 0, 0)
    return road_like

def get_area_center(area, size):
    min_x = size[0]
    min_y = size[1]
    max_x, max_y = 0, 0

    for p in area:
        if p[0] < min_x:
            min_x = p[0]
        if p[0] > max_x:
            max_x = p[0]

        if p[1] < min_y:
            min_y = p[1]
        if p[1] > max_y:
            max_y = p[1]

    return ((min_x+max_x)/2), ((min_y+max_y)/2)

def convert_town_areas(towns):
    print "Converting town areas"
    for town in towns:
        town['area'] = len(town.get('area', []))

def update_town_pos(town, pos, size):
    town['pos']['x'], town['pos']['y'] = pos
    town['pos']['x'] *= 100
    town['pos']['y'] = (size[1] - town['pos']['y'])*100

if __name__ == "__main__":
    main()
