#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import optparse
import os

from PIL import Image


def parse_args():
    usage = """usage: %prog --src=SRC --zoom=ZOOM --tile_size=TILE_SIZE --dst=DST"""
    parser = optparse.OptionParser(usage)

    help = "Path to the source topographical map."
    parser.add_option('--src', help=help)

    help = "Zoom layer number. Default is 0."
    parser.add_option('-z', '--zoom', type='int', default=0, help=help)

    help = "Size of a tile's side. Default is 256"
    parser.add_option('-t', '--tile_size', type='int', default=256, help=help)

    help = "Path to the target directory."
    parser.add_option('--dst', help=help)

    options, args = parser.parse_args()

    if not options.src:
        parser.error("Path to the source topographical map is not specified.")
    if not options.dst:
        parser.error("Path to the destination directory is not specified.")
    try:
        im = Image.open(options.src)
    except IOError as e:
        parser.error("Failed to open source map: %s" % e)
    max_side = max(im.size)
    max_zoom = int(math.ceil(max_side/float(options.tile_size)))-1
    if options.zoom < 0 or options.zoom > max_zoom:
        parser.error("Zoom is out of range: 0-%d." % max_zoom)
    return im, options.tile_size, options.zoom, options.dst


def main():
    src, tsize, zoom, dst = parse_args()
    sw, sh = src.size

    tiles = int(math.pow(2, zoom))
    side_size = tiles*tsize
    if sw > sh:
        w = min(sw, side_size)
        h = int(sh/(sw/float(w)))
    else:
        h = min(sh, side_size)
        w = int(sw/(sh/float(h)))
    im = src.resize((w, h), Image.ANTIALIAS)

    if h < side_size or w < side_size:
        new = Image.new('RGB', (side_size, side_size), (255, 255, 255))
        nw, nh = new.size
        offset = ((nw-w)/2, (nh-h)/2)
        new.paste(im, offset)
        im = new

    dname = os.path.join(dst, str(zoom))
    if not os.path.exists(dname):
        os.makedirs(dname)

    for i, x in enumerate(xrange(0, side_size, tsize)):
        for j, y in enumerate(xrange(0, side_size, tsize)):
            box = (x, y, x+tsize, y+tsize)
            fname = os.path.join(dname, "{:}_{:}.png".format(i, j))
            region = im.crop(box)
            region.save(fname)


if __name__ == '__main__':
    main()
