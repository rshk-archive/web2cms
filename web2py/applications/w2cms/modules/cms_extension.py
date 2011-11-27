'''
Definition stuff for the CMS modules.
'''

__all__ = [
    'CustomController',
    'NodeTypeManager',
    'DynamicBlock',
    'ExtensionsManager',
    'cms_component',
    ]

from gluon import current
import os

class ExtensionsManager:
    """Extensions manager for the CMS"""
    
    _extensions_search_path = None
    db = None
    errors = None
    
    def __init__(self, db):
        self.db = db
        if self.db is not None:
            self.define_tables()
        self._extensions_search_path = [
            os.path.abspath(os.path.join(current.request.folder, 'cms_modules_core')),
            os.path.abspath(os.path.join(current.request.folder, 'cms_modules_extra')),
        ]
    
    def define_tables(self):
        """Define needed tables for the extension manager"""
        from gluon.dal import Field
        db = self.db
        db.define_table(
            'system_modules',
            Field('name', 'string', length=128, required=True, notnull=True, unique=True),
            Field('status', 'boolean', default=False),
            )
    
    def list_available_modules(self):
        """Use ``pkgutil`` to list names of all the available
        extension modules, from _extensions_search_path.
        
        :returns: A list of module names
        """
        import pkgutil
        return [x[1] for x in pkgutil.walk_packages(self._extensions_search_path)]
    
    def list_enabled_modules(self):
        """Lists the enabled modules from database.
        
        :returns: A list of module names
        """
        return [row.name for row in self.db(self.db.system_modules.status==True).select()]
    
    def load_module(self, name):
        """Load and return the specified module from path"""
        import imp
        
        ## Find the module in the search path
        ## Returns (file, pathname, description)
        _found_module = imp.find_module(name, self._extensions_search_path)
        
        ## Get the actual module object
        module = imp.load_module(name, *_found_module)
        
        ## Fetch information and components from the module
        module_info = module.cms_module_info
        components = {}
        for m_object in dir(module):
            obj = getattr(module, m_object)
            c_info = get_component_info(obj)
            if c_info:
                if not components.has_key(c_info['type']):
                    components[c_info['type']] = {}
                components[c_info['type']][m_object] = obj
        return dict(
            name=name,
            module=module,
            info=module_info,
            components=components)
    
    def discover_modules(self):
        """Discover extension modules in the extensions search path.
        
        **How this works**
        
        Extension modules should be placed inside a given search path.
        By default, that path includes the following directories in
        the CMS application directory:
        
            * ``cms_modules_core``
            * ``cms_modules_extra``
        
        Where ``cms_modules_core`` contains the "core" modules shipped
        along with the application itself, and ``cms_modules_extra``
        is there to contain third-party modules.
        
        .. NOTE:: ``cms_modules_extra`` should take the precedence,
            in order to allow overriding of core modules [?]
        
        Then, ``pkgutil.walk_packages()`` is used to explore contents
        of the directories in path.
        
        """
        
        ##----------------------------------------------------------------------
        ## Iterate all the directories in path.
        ## For each directory, list contained modules and packages
        ## Import each module / package and list its content.
        ##----------------------------------------------------------------------
        found_modules = {}
        errors = []
        
        for _module_name in self.list_available_modules():
            try:
                module_def = self.load_module(_module_name)
            except Exception, e:
                errors.append((_module_name, e))
            else:
                found_modules[_module_name] = module_def
        
        self.errors = errors
        return found_modules
    
    def enable(self, name, enabled=True):
        """Enable the specified extension"""
        if self.db(self.db.system_modules.name == name).count():
            self.db(self.db.system_modules.name == name).update(status=enabled)
        else:
            self.db.system_modules.insert(name=name, status=enabled)
        self.db.commit()
    
    def disable(self, name):
        """Disable the specified extension"""
        self.enable(name, False)
    
    def get_components(self, c_type):
        """Get all components of a given type from enabled modules.
        
        :param c_type: The type of interesting component
        :return: A list of tuples: ``('module/component', ComponentObject)``
        """
        _result = []
        for module_name in self.list_enabled_modules():
            module = self.load_module(module_name)
            if module['components'].has_key(c_type):
                for cv,ck in module['components'][c_type].items():
                    _result.append('%s/%s' % (module_name, cv), ck)
        return _result

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

def cms_component(c_type=None, c_name=None, c_module=None):
    def decorator(c):
        c.cms_ext_info = dict(
            type = c_type,
            name = c_name or c.__name__,
            module = c_module or c.__module__,
        )
        return c
    return decorator

def get_component_info(c):
    try:
        return c.cms_ext_info
    except:
        return None

