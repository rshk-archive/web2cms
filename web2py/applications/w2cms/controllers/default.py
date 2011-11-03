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
    """Apply text format conversion to some text."""
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
    """Node creation form"""
    if len(request.args) > 0:
        response.view = 'generic/form.'+request.extension
        node_type = request.args[0]
        node_types = cms_settings.list_node_types()
        if node_type not in node_types.keys():
            raise HTTP(404)
        db.node.type.default = node_type
        return dict(
            title=T('Create %s', node_types[node_type]['label']),
            form=crud.create(db.node),
            )
    else:
        menu_items = [
            (T('Create "%s" node', type_def['label']), False, URL('default','node_create',args=[node_type]), [])
            for node_type, type_def in cms_settings.list_node_types().items()
        ]
        response.view = 'generic/menu_page.'+request.extension
        return dict(
            title=T('Create content'),
            menu_items=menu_items,
            )
    
@helpers.use_custom_view('generic/form')
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
        node = _node_load(request.args[0])
    except:
        raise HTTP(404)
    else:
        
        node.body = _apply_text_format(node.body, node.body_format)
        
        return dict(
            node=node,
            tabs=_node_menu(node.id),
            )

@helpers.use_custom_view('generic/form')
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

def node_list():
    """List all the content"""
    return dict(nodes=db(db.node).select())

def node_search():
    """Content search page"""
    pass

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
    
    if view_name == 'blog':
        ## Return paginated list of articles
        articles_per_page = 5
        page_id = int(view_vars.get('page', 0))
        
        blog_nodes = db(db.node.type=='article')
        
        _first_node = articles_per_page * page_id
        _last_node = _first_node + articles_per_page
        
        nodes = blog_nodes.select(
            db.node.ALL,
            orderby=~db.node.created|db.node.title,
            limitby=(_first_node, _last_node))
        nodes_count = blog_nodes.count()
        
        return response.render(
            'content/page-blog.%s' % request.extension,
            dict(nodes=nodes,
                 nodes_count=nodes_count,
                 page_id=page_id,
                 articles_per_page=articles_per_page,
                 ))

#def get_page_content():
#    import cgi
#    req_path = request.vars.get('path')
#    items = req_path.split('?', 1)
#    path = filter(None, items[0].split('/'))
#    vars = {}
#    if len(items) > 1:
#        for k,v in cgi.parse_qsl(items[1]):
#            vars[k] = v
#    
#    if len(path) < 3:
#        pass ## Cannot serve page
#    
#    content = "page not found: %r" % path
#    
#    if path[0] == request.application \
#        and path[1] == 'default' \
#        and path[2] == 'view' \
#        and path[3] == 'blog':
#        
#        view_vars = vars
#        
#        ## Return paginated list of articles
#        articles_per_page = 5
#        page_id = int(view_vars.get('page', 0))
#        
#        blog_nodes = db(db.node.type=='article')
#        
#        _first_node = articles_per_page * page_id
#        _last_node = _first_node + articles_per_page
#        
#        nodes = blog_nodes.select(
#            db.node.ALL,
#            orderby=~db.node.created|db.node.title,
#            limitby=(_first_node, _last_node))
#        nodes_count = blog_nodes.count()
#        
#        content = "AASDFASDASDASDASDASDASD"
#        
#        content = response.render(
#            'content/page-blog_content.html',
#            dict(nodes=nodes,
#                 nodes_count=nodes_count,
#                 page_id=page_id,
#                 articles_per_page=articles_per_page,
#                 render_full_page=False,
#                 ))
#    
#    return dict(content=content)

