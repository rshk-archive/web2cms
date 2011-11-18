'''
Created on Nov 3, 2011

@author: samu
'''

from gluon import *

## Avoid problems with sphinx
try:
    response = current.response
    request = current.request
except: pass

def render_view(view_name, view_args, view_vars, db):
    handlers = {
        'blog' : _render_view_blog,
        'node' : _render_view_node,
    }
    if view_name in handlers:
        return handlers[view_name](view_name, view_args, view_vars, db)
    
    raise HTTP(404, "View %s not found" % view_name)

def _render_view_blog(view_name, view_args, view_vars, db):
    """Displays a paginated list of articles"""
    
    ## Settings
    articles_per_page = 5
    articles_node_types = ['article']
    
    ## Arguments parsing
    page_id = int(view_vars.get('page', 0))
    
    #blog_nodes = db(db.node.type=='article')
    blog_nodes = db(db.node.type.belongs(articles_node_types))
    
    
    _first_node = articles_per_page * page_id
    _last_node = _first_node + articles_per_page
    
    nodes = blog_nodes.select(
        db.node.ALL,
        orderby=~db.node.created|db.node.title,
        limitby=(_first_node, _last_node))
    nodes_count = blog_nodes.count()
    
    #response.view = 'content/page-blog.%s' % request.extension
    return dict(
        _view='content/page-blog.%s' % request.extension,
        nodes=nodes,
        nodes_count=nodes_count,
        page_id=page_id,
        articles_per_page=articles_per_page,
        )
    
#    return response.render(
#        'content/page-blog.%s' % request.extension,
#        dict(nodes=nodes,
#             nodes_count=nodes_count,
#             page_id=page_id,
#             articles_per_page=articles_per_page,
#             ))

def _render_view_node(view_name, view_args, view_vars, db):
    return dict(
        _view='content/page-node.%s' % request.extension,
        node=db.node[int(view_args[0])],
        teaser=False,
        )
