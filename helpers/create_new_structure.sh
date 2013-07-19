#!/bin/bash


# ------------------------------------------------------------------------------
# Definitions
# ------------------------------------------------------------------------------

prog_name=$(basename $0)

# Default source root path
SOURCE_PATH=`pwd`"/Maps/"

# Default target root path
TARGET_PATH=`pwd`"/data/"

# ------------------------------------------------------------------------------
# Parameters parse
# ------------------------------------------------------------------------------

# Execute getopt on the arguments passed to this program, identified by the
# special character $@
PARSED_OPTIONS=$(getopt -n "$0"  -o hs:t: --long "help,source:,target:"  -- "$@")

#Bad arguments, something has gone wrong with the getopt command.
if [ $? -ne 0 ];
then
  exit 1
fi

# A little magic, necessary when using getopt.
eval set -- "$PARSED_OPTIONS"

function printHelp {
    echo "NAME"
    echo -e "\t$prog_name"

    exit 0
}

while true;
do
    case "$1" in
        -h|--help)
            printHelp
            shift;;

        -s|--source)
            if [ -n "$2" ];
            then
                SOURCE_PATH=$2
            fi
            shift 2;;

        -t|--target)
            if [ -n "$2" ];
            then
                TARGET_PATH=$2
            fi
            shift 2;;

        --)
            shift
            break;;
    esac
done

# ------------------------------------------------------------------------------
# Print selected parameters
# ------------------------------------------------------------------------------

echo -e "Source directory:\t" $SOURCE_PATH
echo -e "Target directory:\t" $TARGET_PATH

# ------------------------------------------------------------------------------
# Processing
# ------------------------------------------------------------------------------

for DIR_PATH in $(find $SOURCE_PATH -mindepth 1 -maxdepth 1 -type d); do
    DIR_PATH=$DIR_PATH"/"
    DIR_NAME=$(basename $DIR_PATH)

    NEW_DIR_PATH=$TARGET_PATH"/"$DIR_NAME"/"
    HEIGHTS_PATH=$NEW_DIR_PATH"heights/"

    mkdir -p $NEW_DIR_PATH
    mkdir -p $HEIGHTS_PATH

    cp $DIR_PATH"Map.png" $NEW_DIR_PATH"map.png"
    cp $DIR_PATH"Map_h.png" $HEIGHTS_PATH"bw.png"

    xml2json.py -s $DIR_PATH"Props.xml" -t $NEW_DIR_PATH"info.json"
done
