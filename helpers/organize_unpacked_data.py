#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from optparse import OptionParser, OptionGroup

settings = {
    'source': "./src",
    'target': "./dst",
}

langs = {
    'en': '',
    'ru': 'ru',
}

def main():
    parse_args()
    update_all_maps()

def parse_args():
    parser = init_parser()
    options, args = parser.parse_args()

    if options.source:
        settings['source'] = options.source
    if options.target:
        settings['target'] = options.target

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
        help=u"Path to the unpacked SFS files root directory")
    group.add_option(
        '-t', '--target',
        action='store',
        dest='target',
        help=u"Output directory root path")
    parser.add_option_group(group)

def update_all_maps():
    target_root = os.path.join(settings['target'], 'maps')
    all_maps_info_path = os.path.join(target_root, 'all.json')
    with open(all_maps_info_path, 'r') as f:
        map_code_names = json.load(f)
    for code_name in map_code_names:
        update_map(os.path.join(target_root, code_name))

def update_map(target_path):
    info_path = os.path.join(target_path, 'info.json')
    with open(info_path, 'r') as f:
        info = json.load(f)
    for variant in info['variants']:
        update_map_variant(info, variant)
    # TODO: copy maps
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=4, sort_keys=True)

def update_map_variant(info, variant):
    loader_config_path = os.path.join(
        settings['source'], 'MAPS', variant['loader'])
    with open(loader_config_path, 'r') as f:
        flag = None
        for line in f.readlines():
            if 'PRESSURE' in line:
                variant['conditions']['pressure'] = \
                    int(get_config_value(line))
            elif 'TEMPERATURE' in line:
                variant['conditions']['temperature'] = \
                    int(get_config_value(line))
            elif '[text]' in line:
                flag = 'text'
            elif flag == 'text':
                texts_file_name = line.strip()
                load_map_variant_texts(
                    info,
                    variant,
                    paths={
                        'texts': os.path.join(
                            os.path.dirname(loader_config_path),
                            texts_file_name
                        ),
                        'props_root': os.path.join(settings['source'], 'i18n'),
                    }

                )
                flag = None

def get_config_value(line):
    return line.split('=')[1].strip()

def load_map_variant_texts(info, variant, paths):
    i18n = {}
    for lang in langs.keys():
        name = info['code_name']
        suffix = langs[lang]
        if suffix:
            name += "_" + suffix
        name += ".properties"
        path = os.path.join(paths['props_root'], name)
        with open(path, 'r') as f:
            for line in f.readlines():
                cols = line.split()
                code_name = cols[0].strip()
                value = unicode(cols[1].strip().decode('raw_unicode_escape'))
                if code_name not in i18n:
                    i18n[code_name] = {}
                i18n[code_name][lang] = value
    with open(paths['texts'], 'r') as f:
        for line in f.readlines():
            cols = line.strip().split()
            code_name = cols[6]
            storage_name = 'towns' if int(cols[5]) == 0 else 'labels'
            info[storage_name][code_name] = {
                'pos': {
                    'x': int(cols[0]),
                    'y': int(cols[1]),
                },
                'type': int(cols[4]),
                'title': dict([
                    (lang, i18n[code_name][lang]) for lang in langs.keys()
                ]),
            }
            if code_name not in variant[storage_name]:
                variant[storage_name].append(code_name)

if __name__ == "__main__":
    main()
