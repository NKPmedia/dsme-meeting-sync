#!/bin/bash

# get directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# activate virtualenv
source $DIR/.venv/bin/activate

#Run main.py in the same directory as this script
#Log output to a file (override if it exists)
$DIR/.venv/bin/python $DIR/main.py > $DIR/log.txt 2>&1

# Capture exit code
EXIT_CODE=$?


if [ $EXIT_CODE -ne 0 ]; then
    echo "Script failed with exit code $EXIT_CODE"
    # Use zenity to display a dialog box
    zenity --error --text="DSME-sync failed with exit code $EXIT_CODE - see log.txt for details"
fi
