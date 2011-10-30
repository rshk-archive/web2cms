#!/bin/bash
## Automatically build Sphinx documentation upon file change
## Copyright (c) 2011 Samuele ~redShadow~ Santi - Under GPL

WORKDIR="$( dirname "$0" )"
while :; do
    ## Wait for changes
    inotifywait -e modify,create,delete -r "$WORKDIR"
    ## Make html documentation
    make -C "$WORKDIR" html
done
