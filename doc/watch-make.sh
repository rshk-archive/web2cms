#!/bin/bash

## Automatically build Sphinx documentation upon file change
## Copyright (c) 2011 Samuele ~redShadow~ Santi - Under GPL

if [ "$1" == "--help" ]; then
    echo "Usage: $(basename "$0") [<watchdir>]"
    echo "Waits for changes on <watchdir>, then rebuilds documentation"
    echo "by running \`make html' in the script directory."
    echo "If not specified, <watchdir> defaults to the script directory."
    exit 0
fi

WORKDIR="$( dirname "$0" )"
WATCHDIR="$WORKDIR"

if [ -n "$1" ]; then
    WATCHDIR="$1"
fi

while :; do
    ## Wait for changes
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "  Watching ${WATCHDIR} for changes"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    inotifywait -e modify,create,delete -r "$WATCHDIR"

    ## Make html documentation
    make -C "$WORKDIR" html

    echo;echo
done
