'''
Created on Oct 30, 2011
@author: samu
'''

def status():
    """
    This controller just displays the current status of the CMS:
    - amount of created nodes (per type)
    - amount of users
    """
    
    node_types = [x.type for x in db().select(db.node.type, distinct=True)]
    nodes_per_type = {}
    for t in node_types:
        nodes_per_type[t] = db(db.node.type == t).count()
    
    return dict(
        nodes_count = db(db.node).count(),
        node_types = node_types,
        nodes_per_type = nodes_per_type,
        )
