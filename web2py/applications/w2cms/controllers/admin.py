'''
Created on Nov 1, 2011

@author: samu
'''

import os
from helpers import use_custom_view

admin_menu = [
    (T('Content'), False, URL('admin','content'), [],
        {'icon': URL('static', 'images/icons/admin-content.png'),
         'description': 'Administer the CMS content.'}),
    (T('Users'), False, URL('admin','users'), [],
        {'icon': URL('static', 'images/icons/system-users.png'),
         'description': 'Administer the CMS users.'}),
    (T('Files'), False, URL('admin','files'), [],
        {'icon': URL('static', 'images/icons/folder.png'),
         'description': 'Use the web file manager to administer uploaded files.'}),
]

@use_custom_view('generic/menu_page')
def index():
    links = admin_menu[:]
    
    for i in xrange(8):
        links.append((T('Fake %d', i), False, URL('admin','fake_page'), [],
            {'icon': URL('static', 'images/icons/folder.png'),
             'description' : 'Just a fake menu item, #%d' % i,}))
    
    
    return dict(
        title=T('Administration panel'),
        menu_items=links,
        layout='grid')

def content():
    return dict(nodes=db(db.node).select())

def users():
    pass

def files():
    pass
