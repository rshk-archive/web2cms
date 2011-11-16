'''
Created on Nov 1, 2011

@author: samu
'''

import os, sys
from helpers import use_custom_view
from cms_auth import requires_cms_permission

## The main administration menu, shown in the administrative page
admin_menu = [
    (T('Database'), False, URL('admin', 'dbadmin'), [],
        {'icon':URL('static','images/icons/server-database.png'),
         'description':T('Administer database')}),
    (T('Plugins'), False, URL('admin', 'plugins'), [],
        {'icon':URL('static','images/icons/plugin.png'),
         'description':T('Administer plugins')}),
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

@requires_cms_permission(auth, "access admin panel")
@use_custom_view('generic/menu_page')
def index():
    links = admin_menu[:]
    return dict(
        title=T('Administration panel'),
        menu_items=links,
        layout='grid')

@requires_cms_permission(auth, "administer", "content")
def content():
    #[row.type for row in db().select(db.node.type, distinct=True, orderby=db.node.type)]
    import datetime
    def _str_to_datetime(ts,fmt="%Y-%m-%d %H:%M:%S"):
        if not ts: return None
        return datetime.datetime.strptime(ts,fmt)
    
    form = SQLFORM.factory(
        Field('node_type', label="Node type",
              requires=IS_EMPTY_OR(IS_IN_SET([row.type for row in db().select(db.node.type, distinct=True, orderby=db.node.type)])),
              default=request.vars.node_type),
        Field('title_contains', label="Title contains",
              default=request.vars.title_contains),
        Field('body_contains', label="Body contains",
              default=request.vars.body_contains),
        Field('created_start', 'datetime', label="Created after",
              default=_str_to_datetime(request.vars.created_start)),
        Field('created_end', 'datetime', label="Created before",
              default=_str_to_datetime(request.vars.created_end)),
        Field('updated_start', 'datetime', label="Updated after",
              default=_str_to_datetime(request.vars.updated_start)),
        Field('updated_end', 'datetime', label="Updated before",
              default=_str_to_datetime(request.vars.updated_end)),
        Field('author', db.auth_user, label="Author",
              requires=IS_EMPTY_OR(IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s')),
              default=request.vars.author),
        )
    
    query = []
    description = []
    
    if form.accepts(request.vars):
        if form.vars.node_type:
            query.append(db.node.type == form.vars.node_type)
            description.append((T('Node type:'), form.vars.node_type))
        
        if form.vars.title_contains:
            query.append(db.node.title.contains(form.vars.title_contains))
            description.append((T('Title contains:'), form.vars.title_contains))
        
        if form.vars.body_contains:
            query.append(db.node.body.contains(form.vars.body))
            description.append((T('Body contains:'), form.vars.body_contains))
        
        if form.vars.created_start:
            query.append(db.node.created >= form.vars.created_start)
            description.append((T('Created after:'), form.vars.created_start))
        
        if form.vars.created_end:
            query.append(db.node.created <= form.vars.created_end)
            description.append((T('Created before:'), form.vars.created_end))
        
        if form.vars.updated_start:
            query.append(db.node.updated >= form.vars.updated_start)
            description.append((T('Updated after:'), form.vars.updated_start))
        
        if form.vars.updated_end:
            query.append(db.node.updated <= form.vars.updated_end)
            description.append((T('Updated before:'), form.vars.updated_end))
        
        if form.vars.author:
            query.append(db.node.author == form.vars.author)
            description.append((T('Author:'), '%(first_name)s %(last_name)s' % db.auth_user[form.vars.author]))
    
    if len(description):
        description.append(('', A(T('Reset query'), _href=URL(request.controller, request.function))))
    
    if query:
        query = reduce(lambda x, y: x & y, query)
    else:
        query=None
    return dict(
        nodes=db(query).select(db.node.ALL),
        filter_form=form,
        description=description,
        )

@requires_cms_permission(auth, "administer", "users")
def users():
    return "TODO: Add the users administration page"

@requires_cms_permission(auth, "administer", "files")
def files():
    return "TODO: Add the files administration page"

@requires_cms_permission(auth, "administer", "database")
def dbadmin():
    ## Everything is done in the view
    return dict()

@requires_cms_permission(auth, "administer", "plugins")
def plugins():
    plugins_dir = os.path.abspath(os.path.join(request.folder, 'cms_plugins'))
    _all_files = os.listdir(plugins_dir)
    _found = []
    
    for f in _all_files:
        _fullname = os.path.join(plugins_dir, f)
        if f.endswith('.py'):
            _found.append(f[:-3])
        elif os.path.isdir(_fullname) and os.path.isfile(os.path.join(_fullname, '__init__.py')):
            _found.append(f)
    
    _errors = []
    _loaded_plugins = {}
    
    _app_folder = os.path.abspath(request.folder)
    
    if not _app_folder in sys.path:
        sys.path.insert(0, _app_folder)
    
    from cms_plugin_def import *
    
    for plugin_name in _found:
        try:
            _mod = __import__('cms_plugins', globals=globals(), locals=locals(), fromlist=[plugin_name])
            plugin_module = getattr(_mod, plugin_name)
            plugin_info = plugin_module.cms_plugin_info
            plugin_contents = []
            
            for elm_name in dir(plugin_module):
                if elm_name.startswith('_'): continue
                elm = getattr(plugin_module, elm_name)
                if type(elm).__name__ == 'classobj':
                    if issubclass(elm, CustomController) and not elm is CustomController:
                        plugin_contents.append(('CustomController', elm))
                    elif issubclass(elm, NodeTypeManager) and not elm is NodeTypeManager:
                        plugin_contents.append(('NodeTypeManager', elm))
                    elif issubclass(elm, DynamicBlock) and not elm is DynamicBlock:
                        plugin_contents.append(('DynamicBlock', elm))
            
            _loaded_plugins[plugin_name] = dict(
                module=plugin_module,
                info=plugin_info,
                contents=plugin_contents,
                )
            
            #dir(getattr(plugin_module, 'example_plugin'))
        except Exception, e:
            _errors.append((plugin_name, e))
    
    return dict(
        found_plugins=_found,
        errors=_errors,
        loaded_plugins=_loaded_plugins,
        )
