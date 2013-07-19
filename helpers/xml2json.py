#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from optparse import OptionParser, OptionGroup
from xml.dom import minidom

settings = {
    'source': "Props.xml",
    'target': "info.json",
}

def main():
    parse_args()
    validate_settings()
    convert()

def parse_args():
    parser = init_parser()
    options, args = parser.parse_args()

    settings['source'] = options.source or settings['source']
    settings['target'] = options.target or settings['target']

def init_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    init_parser_groups(parser)
    return parser

def init_parser_groups(parser):
    group = OptionGroup(parser, u"Input/output options")
    group.add_option(
        '-s', '--source',
        action='store',
        dest='source',
        help=u"Path to the source Props.xml file")
    group.add_option(
        '-t', '--target',
        action='store',
        dest='target',
        help=u"Path to the target info.json file")
    parser.add_option_group(group)

def validate_settings():
    validate_source_path()
    validate_target_path()

def validate_source_path():
    path = settings['source']
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise ValueError(u"Invalid source path {0}.".format(path))
    else:
        raise ValueError(u"Source file {0} does not exist.".format(path))

def validate_target_path():
    path = settings['target']
    if os.path.exists(path) and not os.path.isfile(path):
        raise ValueError(u"Invalid target path {0}.".format(path))

def convert():
    data = get_data()
    with open(settings['target'], 'w') as target:
        json.dump(data, target)

def get_data():
    path = settings['source']
    getters = [get_map_info, get_towns_info, get_airfields_info, ]
    data = {}
    try:
        xmldoc = minidom.parse(path)
        for getter in getters:
            getter(xmldoc, data)
    except Exception:
        print u"Parsing source XML file {0} failed.".format(path)
        raise
    return data

def get_map_info(xmldoc, data):
    info = {}
    node = xmldoc.getElementsByTagName('MisCode')[0].childNodes[0]
    info['code_name'] = node.nodeValue

    info['geometry'] = {}
    node = xmldoc.getElementsByTagName('Width')[0].childNodes[0]
    info['geometry']['width'] = int(node.nodeValue)
    node = xmldoc.getElementsByTagName('Height')[0].childNodes[0]
    info['geometry']['height'] = int(node.nodeValue)

    data.update(info)

def get_towns_info(xmldoc, data):
    town_list = []
    nodes = xmldoc.getElementsByTagName('MapText')
    for node in nodes:
        town = {}
        town['code_name'] = node.attributes['Code'].value
        town['pos'] = get_position(node)

        town['label'] = {}
        town['label']['en'] = unicode(node.attributes['NameEng'].value)
        town['label']['ru'] = unicode(node.attributes['NameRus'].value)

        town_list.append(town)
    data.update({
        'towns': town_list,
    })

def get_airfields_info(xmldoc, data):
    airfield_list = []
    nodes = xmldoc.getElementsByTagName('Airfield')
    for node in nodes:
        airfield = {}
        airfield['id'] = int(node.attributes['ID'].value)
        airfield['landing_vector'] = int(node.attributes['A'].value)
        airfield['type'] = int(node.attributes['T1'].value)
        airfield['pos'] = get_position(node)

        airfield_list.append(airfield)
    data.update({
        'airfields': airfield_list,
    })

def get_position(node):
    x = float(node.attributes['X'].value)
    y = float(node.attributes['Y'].value)
    return {
        'x': x,
        'y': y,
    }

if __name__ == "__main__":
    main()
