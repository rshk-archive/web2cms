#!/usr/bin/python
# -*- coding: utf-8 -*-

##--------------------------------------------------
## Global routes.py
##--------------------------------------------------

default_application = 'w2cms'
default_controller = 'default'
default_function = 'index'

## Experimental router for w2cms
routers = dict(BASE = dict(default_application = 'w2cms'))
routes_app = ((r'/(?P<app>w2cms|admin)\b.*', r'\g<app>'),)

routes_in = ((r'.*:/favicon.ico', r'/w2cms/static/favicon.ico'),
             (r'.*:/robots.txt', r'/w2cms/static/robots.txt'),)
