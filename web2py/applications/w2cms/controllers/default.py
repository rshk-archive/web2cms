# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


## Node CRUD -------------------------------------------------------------------

#helpers = local_import('helpers')
#helpers.request = request
#helpers.response = response

import helpers
from helpers import use_custom_view

def _node_load(node_id):
    """Load a node from database.
    Raises an exception if no node was found,
    """
    node = db.node[node_id]
    if not node: raise Exception
    return node

def _node_menu(node_id):
    """Generate actions menu for the selected node"""
    menu_items = []
    for label, function in [
        (T('View'), 'node_read'),
        (T('Versions'), 'node_versions'),
        (T('Edit'), 'node_update'),
        (T('Delete'), 'node_delete'),
        ]:
        menu_items.append((
            label,
            request.function == function, # current?
            URL('default', function, args=[node_id]),
            []))
    return menu_items

def _apply_text_format(text, format):
    """Apply text format conversion to some text.
    
    .. TODO:: Improve this to use configurable input formats with multiple
        filters, in a way similar to what Drupal does.
    """
    if format == 'plain_text':
        ## In plain text, quote all tags
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace("\n", '<br/>')
        text = XML(text)
    elif format == 'code':
        ## In code, escape and wrap with <pre> tag
        text = PRE(text)
    elif format == 'full_html':
        ## Prevent escaping for Full HTML content
        text = XML(text.replace("\n", "<br/>"))
    elif format == 'limited_html':
        ##@todo: strip just *some* tags
        pass
    elif format == 'markmin':
        ##@todo: convert markmin into HTML
        pass
    return text

import cms_settings

def node_create():
    """Node creation form.
    
    Here, we need to have:
    
    * Fields for db.node:
    
      * id (0 for creation)
      * type (hidden)
      * published
      * weight
      
    * Fields for db.node_version:
    
      * id (0 for creation)
      * revision_id (0 for creation)
      * language
      * {created,updated} {date,by}
      * published (for the version)
      * is_translation_base -> hidden, locked!
    
    * Fields for db.node_base_fields:
    
      * id (0 for creation)
      * title
      * body
      * body_format
    """
    if len(request.args) > 0:
        ## Return creation form for this node type
        
        node_type = request.args[0]
        node_types = cms_settings.list_node_types()
        if node_type not in node_types.keys():
            raise HTTP(404)
        
        ## Set defaults
        db.node.type.default = node_type
        
        ## Generate form. We can't use CRUD here!
        form = SQLFORM(db.node)
        #form_node_version = SQLFORM(db.node_version)
        
        
        
        response.view = 'generic/form.' + request.extension
        return dict(
            title=T('Create %s', node_types[node_type]['label']),
            form=form)
    
    else:
        ## Return selection menu to choose node type to create
        menu_items = [
            (T('Create "%s" node', type_def['label']), False,
                URL('default','node_create',args=[node_type]), [])
            for node_type, type_def in cms_settings.list_node_types().items()
        ]
        response.view = 'generic/menu_page.%s' % request.extension
        return dict(title=T('Create content'), menu_items=menu_items)
    
@use_custom_view('generic/form')
def node_update():
    """Node update form"""
    try:
        node = _node_load(request.args[0])
    except:
        raise HTTP(404)
    else:
        return dict(
            title=T('Node #%d (%s): update', (node.id, node.title)),
            tabs=_node_menu(node.id),
            form = crud.update(db.node, node)
        )

def node_read():
    """Full-page node display"""
    try:
        node = cmsdb.node.read(int(request.args[0]))
    except:
        raise HTTP(404)
    else:
        return dict(
            node=node,
            tabs=_node_menu(node.id),
            )

@use_custom_view('generic/form')
def node_delete():
    """Node deletion confirm form.
    
    .. WARNING::
        Crud().delete() actually deletes the record without confirmation!
    """
    try:
        node = _node_load(request.args[0])
    except:
        raise HTTP(404)
    else:
        return dict(
            title=T('Node #%d (%s): delete', (node.id, node.title)),
            tabs=_node_menu(node.id),
            form = "Please use the udpate form to delete entries"
        )

def node_versions():
    """Information on node versions"""
    return node_read()

def node_list():
    """List all the content"""
    return dict(nodes=cmsdb.node.search())

def node_search():
    """Content search page"""
    pass

from cms_views import render_view

def view():
    """Expose visualizations of content, in a way similar to what
    Drupal views does.
    
    .. NOTE::
        At the moment, all the code needed to generate views is temporarily
        here. Then, in the future, we'll find a way to move it to
        configuration files. Problem is how to define possibly complex
        database queries in a flexible way inside configuration files.
        
        @todo: find a way to represent and parse ldap-like search filters
    """
    
    view_name = request.args(0)
    view_args = request.args[1:]
    view_vars = request.vars
    
    data = render_view(view_name, view_args, view_vars, db)
    if data.has_key('_view'):
        response.view = data['_view']
    return data

@use_custom_view('generic/form')
def comment_create():
    """Comment creation form"""
    
    if len(request.args) >= 2:
        ## We need object_type,object_delta to create comment
        ##@todo: check that the object we are commenting exists and is commentable!!
        db.comment.object_type.default=request.args[0]
        db.comment.object_delta.default=request.args[1]
        return dict(
            title=T('Add comment'),
            form=crud.create(db.comment),
            )
    else:
        raise HTTP(404)
        


