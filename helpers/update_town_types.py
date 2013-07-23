#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from optparse import OptionParser, OptionGroup

settings = {
    'path': "./",
    'info_paths': [],
}

def main():
    parse_args()
    validate_settings()
    update_types()

def parse_args():
    parser = init_parser()
    options, args = parser.parse_args()
    settings['path'] = options.path or settings['path']

def init_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    init_parser_groups(parser)
    return parser

def init_parser_groups(parser):
    group = OptionGroup(parser, u"Input/output options")
    group.add_option(
        '-p', '--path',
        action='store',
        dest='path',
        help=u"Path to the maps data root directory")
    parser.add_option_group(group)

def validate_settings():
    path = settings['path']
    if not os.path.exists(path):
        raise ValueError(u"Directory '{0}' does not exist.".format(path))
    if not os.path.isdir(path):
        raise ValueError(u"Invalid directory path '{0}'.".format(path))
    map_dirs = [
        map_dir for map_dir in [os.path.join(path, d) for d in os.listdir(path)]
        if os.path.isdir(map_dir)
    ]
    if not map_dirs:
        raise ValueError(u"No map subdirs were found in '{0}'.".format(path))
    for map_dir in map_dirs:
        validate_map_directory(map_dir)

def validate_map_directory(path):
    info_path = os.path.join(path, "info.json")
    if not os.path.exists(info_path):
        raise ValueError(
            u"Info file does not exist in '{0}' directory.".format(path))
    if not os.path.isfile(info_path):
        raise ValueError(u"Invalid map info path '{0}'.".format(info_path))
    settings['info_paths'].append(info_path)

def update_types():
    areas = get_town_areas(settings['info_paths'])
    print areas

def get_town_areas(file_paths):
    areas = []
    for file_path in file_paths:
        with open(file_path, 'r') as info_file:
            info = json.load(info_file)
            areas.extend(
                [town['area'] for town in info['towns'] if town['area'] > 0]
            )
    return areas

if __name__ == "__main__":
    main()
