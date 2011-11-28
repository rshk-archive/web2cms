#!/usr/bin/python
# -*- coding: utf-8 -*-

##--------------------------------------------------
## w2cms-specific routes.py
##--------------------------------------------------

routers = dict(
    BASE = dict(default_application = 'w2cms'),
    #TODO: Languages should be loaded from configuration
    w2cms = dict(
        languages=['en', 'it', 'jp', 'es', 'de', 'fr'],
        default_language='en',
        ),
)
