#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import json
import Image
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

exclude_icons = [
    'empty.tga',
    'faractor.tga',
]


def main():
    parse_args()
    update_all_maps()
    update_icons()

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
        update_map_variant(info, variant, target_path)
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=4, sort_keys=True)


def update_map_variant(info, variant, target_path):
    loader_config_path = os.path.join(
        settings['source'], 'MAPS', variant['loader'])
    source_path = os.path.dirname(loader_config_path)
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
                            source_path, texts_file_name),
                        'props_root': os.path.join(
                            settings['source'], 'i18n'),
                    }
                )
                flag = None
    update_map_image(
        info,
        paths={
            'src': os.path.join(source_path, "ed_m01.tga"),
            'tgt': os.path.join(target_path, "map.png"),
        }
    )


def update_map_image(info, paths):
    img = Image.open(paths['src'])
    img.save(paths['tgt'])
    info['geometry']['width'] = img.size[0]*100
    info['geometry']['height'] = img.size[1]*100


def get_config_value(line):
    return line.split('=')[1].strip()


def load_map_variant_texts(info, variant, paths):

    def get_properties_path(code_name, lang):
        if lang:
            name = "{0}_{1}.properties".format(code_name, lang)
        else:
            name = "{0}.properties".format(code_name)
        return os.path.join(paths['props_root'], name)

    def get_code_name_translations():
        result = {}
        for lang in langs.keys():
            path = get_properties_path(info['code_name'], langs[lang])
            with open(path, 'r') as f:
                for line in f.readlines():
                    cols = line.split()
                    code_name = cols[0]
                    value = unicode(cols[1].decode('raw_unicode_escape'))
                    if code_name not in result:
                        result[code_name] = {}
                    result[code_name][lang] = value
        return result

    i18n = get_code_name_translations()
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

def update_icons():
    source_path = os.path.join(settings['source'], 'icons')
    target_path = os.path.join(settings['target'], 'icons')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for img_name in os.listdir(source_path):
        if fnmatch.fnmatch(img_name, '*.tga') and img_name not in exclude_icons:
            img = Image.open(
                os.path.join(source_path, img_name))
            img.save(
                os.path.join(target_path, img_name.replace('.tga', '.png')))

if __name__ == "__main__":
    main()
