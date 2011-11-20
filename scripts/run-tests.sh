#!/bin/bash

## Run all test cases in w2cms/tests

WEB2PY="$( dirname "$0" )"/../web2py/web2py.py
TESTSDIR="$( dirname "$0" )"/../web2py/applications/w2cms/tests

for f in $( echo "${TESTSDIR}"/*.py | sort ); do
    echo -e "\033[1;37m=====( \033[1;32mRUNNING TESTS IN \033[1;33m$( basename "$f" )\033[1;32m \033[1;37m)=====\033[0m"
    "$WEB2PY" -S w2cms -M -R "$f"
    echo;echo
done
