'''
Definition stuff for the CMS modules.
'''

__all__ = [
    'CustomController',
    'NodeTypeManager',
    'DynamicBlock',
    ]

class CustomController:
    """Base class for custom controllers.
    
    Custom controllers respond by default on something like
    ``default/plugin/<plugin-name>/<controller-name>``.
    """
    
    controller_name = None
    pass

class NodeTypeManager:
    """Base class for node type managers"""
    
    node_type_name = None
    pass

class DynamicBlock:
    """Base class for dynamic blocks"""
    pass
