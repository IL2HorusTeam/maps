#!/bin/sh

SRC=$1
DST=$2
LOCATION=$3
TSIZE=$4
ZOOM=$5

python map_tiler.py --src=$SRC"/"$LOCATION"/topographical.png" --dst=$DST"/"$LOCATION"/topo" --tile_size=$TSIZE -z $ZOOM
python map_tiler.py --src=$SRC"/"$LOCATION"/plains.png" --dst=$DST"/"$LOCATION"/plains" --tile_size=$TSIZE -z $ZOOM
python map_tiler.py --src=$SRC"/"$LOCATION"/jet.png" --dst=$DST"/"$LOCATION"/jet" --tile_size=$TSIZE -z $ZOOM
