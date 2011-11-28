'''
Definition stuff for the CMS modules.
'''

__all__ = [
    'cms_component',
    'ExtensionsManager',
    'CustomController',
    'NodeTypeManager',
    'DynamicBlock',
]


from gluon import current
import os

class ExtensionsManager:
    """Extensions manager for the CMS"""
    
    _extensions_search_path = None
    db = None
    errors = None
    
    def __init__(self, db):
        """ExtensionsManager class constructor.
        
        :param db: A valid ``DAL()`` connection object.
        """
        self.db = db
        if self.db is not None:
            self.define_tables()
        self._extensions_search_path = [
            os.path.abspath(os.path.join(current.request.folder, 'cms_modules_core')),
            os.path.abspath(os.path.join(current.request.folder, 'cms_modules_extra')),
        ]
    
    def define_tables(self):
        """Define needed tables for the extension manager.
        This is automatically called by constructor if a valid ``db``
        is passed.
        """
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
        
        :returns: Names of modules found in path
        :rtype: list of strings
        """
        import pkgutil
        return [x[1] for x in pkgutil.walk_packages(self._extensions_search_path)]
    
    def list_enabled_modules(self):
        """Lists the enabled modules from database.
        
        :returns: Names of the enabled modules
        :rtype: list of strings
        """
        return [row.name for row in self.db(self.db.system_modules.status==True).select()]
    
    def load_module(self, name):
        """Load and return the specified module from path.
        
        :param name: The module name
        :type name: string
        """
        import imp
        from helpers import recursive_update
        
        ## Find the module in the search path
        ## Returns (file, pathname, description)
        _found_module = imp.find_module(name, self._extensions_search_path)
        
        ## Get the actual module object
        module = imp.load_module(name, *_found_module)
        
        ## Fetch information and components from the module
        module_info = dict(
            name = name,
            description = '',
            version = '',
            core_version = '',
            dependencies = [],
            meta = dict(
                package = 'Misc',
                ),
            )
        
        #module_info.update(module.cms_module_info)
        recursive_update(module_info, module.cms_module_info)
        
        ## Retrieve components
        components = {}
        for m_object in dir(module):
            obj = getattr(module, m_object)
            c_info = get_component_info(obj)
            if c_info:
                if not components.has_key(c_info['type']):
                    components[c_info['type']] = {}
                components[c_info['type']][m_object] = obj
        
        ## Return information about the module
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
        """Enable the specified extension module.
        
        :param name: The module name
        :type name: string
        :param enabled: Whether to mark the module as enabled or disabled
        :type enabled: boolean
        """
        if self.db(self.db.system_modules.name == name).count():
            self.db(self.db.system_modules.name == name).update(status=enabled)
        else:
            self.db.system_modules.insert(name=name, status=enabled)
        self.db.commit()
    
    def disable(self, name):
        """Disable the specified extension module, by calling
        ``self.enable(name, False)``.
        """
        self.enable(name, False)
    
    def get_components(self, c_type):
        """Get all components of a given type from the enabled modules.
        
        :param c_type: The type of interesting component
        :return: A list of tuples: ``('module/component', ComponentObject)``
        """
        _result = []
        for module_name in self.list_enabled_modules():
            module = self.load_module(module_name)
            if module['components'].has_key(c_type):
                for cv,ck in module['components'][c_type].items():
                    _result.append(('%s/%s' % (module_name, cv), ck))
        return _result

def cms_component(c_type=None, label=None):
    """Decorator to be used to mark an extension module component.
    
    To mark the component, an additional ``cms_ext_info`` attribute
    will be added to it.
    It is a dict, with the following keys:
    
    type
        The value passed as ``c_type``
    label
        The value passed as ``label``
    name
        The component ``__name__``
    module
        The component ``__module__``
    
    :param c_type: The component type
    :param label: An optional label to be attached to this component.
        Defaults to ``module.name``.
    """
    def decorator(c):
        c.cms_ext_info = dict(
            type = c_type,
            name = c.__name__,
            module = c.__module__,
            label = label or ("%s.%s" % (c.__module__, c.__name__))
        )
        return c
    return decorator

##==============================================================================
## Base classes to be used for some components.
##
## Warning: their use is not mandatory, it is just useful to have
##          some base classes defining common methods, etc.
##==============================================================================

class CmsExtensionBase:
    """Base for CMS extension components"""
    cms=None
    def __init__(self, cms):
        self.cms=cms

class CustomController(CmsExtensionBase):
    """Base class for "custom controllers".
    
    .. NOTE::
        Custom controllers are used like standard web2py controllers,
        but they should respond on: ``plugin_ctl/<plugin_name>/<controller_name>``
    
    .. WARNING:: This component behavior is not yet defined!
    """
    
    controller_name = None
    pass

class NodeTypeManager(CmsExtensionBase):
    """Base class for node type managers.
    
    .. WARNING:: This component behavior is not yet defined!
    """
    
    node_type_name = None
    pass

class DynamicBlock(CmsExtensionBase):
    """Class to define a "dynamic block" extension module component.
    """
    
    def list_blocks(self):
        """This method should return a list of defined blocks.
        
        :rtype: list of ``(id, description)`` tuples
        """
        raise NotImplementedError
    
    def get_block(self, block_id):
        """This method should return the content of the specified block.
        
        :rtype: ``dict(title='...', body='...')``
        """
        raise NotImplementedError


def get_component_info(c):
    try:
        return c.cms_ext_info
    except:
        return None

