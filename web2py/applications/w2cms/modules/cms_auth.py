'''
Custom authentication stuff for CMS.

Created on Nov 10, 2011
@author: samu
'''

def has_permission(auth, name='any', table_name='', record_id=0, user_id=None, group_id=None,):
    """Custom permission checking, using recursive permissions.
    
    If the user is superuser, return True directly.
    Else, test that user has one of these permissions:
    
    name, table_name, record_id
    '*',  table_name, record_id
    name, '*',        record_id
    '*',  '*',        record_id
    name, table_name, '*'
    '*',  table_name, '*'
    name, '*',        '*'
    '*',  '*',        '*'
    
    
    """
    
    if user_id == 1 or (user_id is None and group_id is None and auth.user and auth.user.id == 1):
        return True ## Superuser is user #1
    
    for _name in [name, '*']:
        for _table_name in [table_name, '*']:
            for _record_id in [record_id, '*']:
                if auth.has_permission(_name, _table_name, _record_id, user_id, group_id):
                    return True
    return False

def requires_cms_permission(auth, name='any', table_name='', record_id=0):
    """Decorator for CMS permissions resolution method"""
    return auth.requires(has_permission(auth, name, table_name, record_id))
