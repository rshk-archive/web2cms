# -*- coding: utf-8 -*-

import os, sys
from helpers import use_custom_view
from cms_auth import requires_cms_permission

## The main administration menu, shown in the administrative page


@cms_auth.requires_permission(auth, "access admin panel")
@use_custom_view('generic/menu_page')
def index():
    links = menu_admin[:]
    return dict(
        title=T('Administration panel'),
        menu_items=links,
        layout='grid')

@cms_auth.requires_permission(auth, "administer", "content")
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
        nodes=cmsdb.node.search(query=query),
        filter_form=form,
        description=description,
        )

@cms_auth.requires_permission(auth, "administer", "users")
def users():
    return "TODO: Add the users administration page"

@cms_auth.requires_permission(auth, "administer", "files")
def files():
    return "TODO: Add the files administration page"

@cms_auth.requires_permission(auth, "administer", "database")
def dbadmin():
    ## Everything is done in the view
    return dict()

@cms_auth.requires_permission(auth, "administer", "plugins")
def modules():
    return dict(
        modules=cms_extm.discover_modules(),
        enabled_modules=cms_extm.list_enabled_modules(),
        )

@cms_auth.requires_permission(auth, "administer", "plugins")
@use_custom_view('generic/form')
def module_enable():
    module_name = request.args[0]
    module_label = None
    module = cms_extm.load_module(module_name)
    module_label = module['info']['name']
    enabled = int(request.vars.get('enabled',1))
    _form_destination = URL('admin','modules')
    from helpers import confirm_form
    form = confirm_form(
        message=T('Are you sure you want to %(action)s module %(module)s?') %
            dict(action=T('enable') if enabled else T('disable'), module=module_label),
        submit_text=T('Enable') if enabled else T('Disable'),
        cancel_url=_form_destination,
        )
    if form.process().accepted:
        if enabled:
            cms_extm.enable(module_name)
        else:
            cms_extm.disable(module_name)
        session.flash = T('Module %(module)s %(action)s') % dict(action=T('enabled') if enabled else T('disabled'), module=module_name)
        redirect(_form_destination)
    return dict(form=form)


@cms_auth.requires_permission(auth, "administer", "blocks")
def blocks():
    block_cmp = cms_extm.get_components('block')
    
    all_blocks_data = []
    for block_mgr_id, block_mgr in block_cmp:
        for block_id,block_description in block_mgr(cms).list_blocks():
            _module, _class = block_mgr_id.split('/',1)
            all_blocks_data.append({
                'module':_module,
                'class':_class,
                'id':block_id,
                'uuid':'block--%s--%s--%s' % (_module,_class,block_id),
                'description':block_description,
                })
    
    #edit_form = SQLFORM()
    
    return dict(block_cmp=block_cmp,all_blocks=all_blocks_data)
