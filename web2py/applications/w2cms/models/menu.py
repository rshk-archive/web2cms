# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

##@todo: read from configuration
from cms_settings import cfg_parser
main_cfg = cfg_parser('cms-settings', force_reload=True)

#response.title = "web2cms"
#response.subtitle = T('A web2py-based Content Management System')
response.title = main_cfg.getd('information','title','web2cms')
response.subtitle = main_cfg.getd('information','subtitle','')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Samuele Santi <redshadow@hackzine.org>'
response.meta.description = 'A web2py-based Content Management System'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'
response.meta.copyright = 'Copyright (C) 2011 - Under GPLv3'

## your http://google.com/analytics id
#response.google_analytics_id = None
response.google_analytics_id = main_cfg.getd('misc', 'google_analytics_id') or None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

import cms_settings

response.menu = [
    (T('Home'), False, URL('default','index'), []),
    
    ## Node stuff
    (T('Content'), False, URL('default','node_list'), [
        (T('List content'), False, URL('default','node_list'), []),
        (T('Add'), False, URL('default','node_create'), [
            (T('New %s', type_def['label']), False, URL('default','node_create', args=[node_type]))
            for node_type, type_def in cms_settings.list_node_types().items()
        ]),
        (T('Search'), False, URL('default','node_search'), []),
    ]),
    
    ## Administration panel
    (T('Admin'), False, URL('admin','index'), []),
    
#    ## Development          
#    (T('Devel'), False, URL('devel','index'), [
#        (T('Status'), False, URL('devel','status'), []),
#        (T('Generate'), False, URL('devel','generate'), []),
#        (T('Appadmin'), False, URL('appadmin','index'), []),
#    ]),
    
    ]

menu_development = (T('Devel'), False, URL('devel','index'), [
    (T('Status'), False, URL('devel','status'), [],
        {'icon':URL('static','images/icons/system-monitor.png')}),
    (T('Generate'), False, URL('devel','generate'), [],
        {'icon':URL('static','images/icons/devel.png')}),
    (T('Appadmin'), False, URL('appadmin','index'), [],
        {'icon':URL('static','images/icons/devel.png')}),
    (T('CSS Devel'), False, URL('devel','css_devel'), [],
        {'icon':URL('static','images/icons/devel.png')}),
])

response.menu.append(menu_development)

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller    
    # useful links to internal admin and appadmin pages
    response.menu+=[
        (T('This App'),False, 
         URL('admin','default','design/%s' % app), [
                (T('Controller'),False,
                 URL('admin','default','edit/%s/controllers/%s.py' % (app,ctr))),
                (T('View'),False,
                 URL('admin','default','edit/%s/views/%s' % (app,response.view))),
                (T('Layout'),False,
                 URL('admin','default','edit/%s/views/layout.html' % app)),
                (T('Stylesheet'),False,
                 URL('admin','default','edit/%s/static/base.css' % app)),
                (T('DB Model'),False,
                 URL('admin','default','edit/%s/models/db.py' % app)),
                (T('Menu Model'),False,
                 URL('admin','default','edit/%s/models/menu.py' % app)),
                (T('Database'),False, URL(app,'appadmin','index')),
                (T('Errors'),False, URL('admin','default','errors/' + app)),
                (T('About'),False, URL('admin','default','about/' + app)),
                ]
         )]    

    # useful links to external resources
    response.menu+=[
        (T('Resources'),False, None, [
                (T('Documentation'),False,'http://www.web2py.com/book', [
                        (T('Preface'),False,'http://www.web2py.com/book/default/chapter/00'),
                        (T('Introduction'),False,'http://www.web2py.com/book/default/chapter/01'),
                        (T('Python'),False,'http://www.web2py.com/book/default/chapter/02'),
                        (T('Overview'),False,'http://www.web2py.com/book/default/chapter/03'),
                        (T('The Core'),False,'http://www.web2py.com/book/default/chapter/04'),
                        (T('The Views'),False,'http://www.web2py.com/book/default/chapter/05'),
                        (T('Database'),False,'http://www.web2py.com/book/default/chapter/06'),
                        (T('Forms and Validators'),False,'http://www.web2py.com/book/default/chapter/07'),
                        (T('Access Control'),False,'http://www.web2py.com/book/default/chapter/08'),
                        (T('Services'),False,'http://www.web2py.com/book/default/chapter/09'),
                        (T('Ajax Recipes'),False,'http://www.web2py.com/book/default/chapter/10'),
                        (T('Deployment Recipes'),False,'http://www.web2py.com/book/default/chapter/11'),
                        (T('Other Recipes'),False,'http://www.web2py.com/book/default/chapter/12'),
                        (T('Buy this book'),False,'http://stores.lulu.com/web2py'),
                        ]),
                (T('Community'),False, None, [
                        (T('Groups'),False,'http://www.web2py.com/examples/default/usergroups'),
                        (T('Twitter'),False,'http://twitter.com/web2py'),
                        (T('Live chat'),False,'http://mibbit.com/?channel=%23web2py&server=irc.mibbit.net'),
                        (T('User Voice'),False,'http://web2py.uservoice.com/'),
                        ]),
                (T('Web2py'),False,'http://www.web2py.com', [
                        (T('Download'),False,'http://www.web2py.com/examples/default/download'),
                        (T('Support'),False,'http://www.web2py.com/examples/default/support'),
                        (T('Quick Examples'),False,'http://web2py.com/examples/default/examples'),
                        (T('FAQ'),False,'http://web2py.com/AlterEgo'),
                        (T('Free Applications'),False,'http://web2py.com/appliances'),
                        (T('Plugins'),False,'http://web2py.com/plugins'),
                        (T('Recipes'),False,'http://web2pyslices.com/'),
                        (T('Demo'),False,'http://web2py.com/demo_admin'),
                        (T('Semantic'),False,'http://web2py.com/semantic'),
                        (T('Layouts'),False,'http://web2py.com/layouts'),
                        (T('Videos'),False,'http://www.web2py.com/examples/default/videos/'),
                        ]),
                ]
         )]
#_()
