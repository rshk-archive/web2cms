#!/bin/bash

## Executes a shell for w2cms

APPNAME="w2cms"
[ -n "$1" ] && APPNAME="$1"

echo "Launching shell for ${APPNAME} ..."
"$(dirname "$0")"/../web2py/web2py.py -M -S "$APPNAME"
