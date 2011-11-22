'''
Custom authentication functions to be used with web2cms.

**Added features:**

* Cascading, entity-based, permission checking.
  An user is automatically checked for permission on the selected entity
  or some higher-level more-including permission.
* Support for "anonymous user" virtual group + permissions [TODO]
'''

def has_permission(auth, name='any', table_name='', record_id=0, user_id=None, group_id=None,):
    """Custom permission checking, using recursive permissions.
    
    If the user is superuser, return True directly.
    Else, test that user has one of these permissions:
    
    name, table_name, record_id
    '*',  table_name, record_id
    name, '*',        record_id ----> ??? MAKES NO SENSE
    '*',  '*',        record_id ----> ??? MAKES NO SENSE
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

class CMSAuth:
    """Auth wrapper that exposes more convenient methods
    to be used in web2cms
    """
    
    _auth = None
    
    def __init__(self, auth):
        self._auth = auth
    
    def has_permission(self, name='any', table_name='', record_id=0, user_id=None, group_id=None,):
        """Custom permission checking, using recursive permissions.
        
        If the user is superuser, return True directly.
        Else, test that user has one of these permissions:
        
        name, table_name, record_id
        '*',  table_name, record_id
        name, table_name, '*'
        '*',  table_name, '*'
        name, '*',        '*'
        '*',  '*',        '*'
        
        If there is no logged-in user, it should check permissions
        for the virtual group "0" (anonymous users): that is, permissions
        assigned to group 0.
        
        .. NOTE::
            We need to find a way to store such permissions skipping
            the IS_IN_DB() validation on auth_permissions!
        
        """
        
        if user_id is None:
            if self._auth.user:
                user_id = self._auth.user.id
            else:
                user_id = 0 ## Anonymous
        
        
        ## User #1 is the God-Like SuperUser[TM]
        if user_id == 1: return True
        
        if user_id == 0:
            ## Anonymous user -> check permissions for "anonymous" group
            pass
        
        checked_perms = [
            (name, table_name, record_id), ## This action on this exact entity
            ('*', table_name, record_id), ## Any action on this exact entity
            (name, table_name, '*'), ## This action on any entity of this type
            ('*', table_name, '*'), ## Any action on any entity of this type
            (name, '*', '*'), ## This action on any entity
            ('*', '*', '*'), ## Any action on any entity
        ]
        
        for _name, _table_name, _record_id in checked_perms:
            if self._auth.has_permission(_name, _table_name, _record_id, user_id, group_id):
                return True
        return False

    
    def requires_permission(self, name='any', table_name='', record_id=0):
        """Decorator for CMS permissions resolution method"""
        return self._auth.requires(self.has_permission(name, table_name, record_id))
    
