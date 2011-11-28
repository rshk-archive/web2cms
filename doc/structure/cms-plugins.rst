#################
Extension modules
#################

.. TODO::
    "Extension modules" is a non-conflicting name, but we could improve
    by replacing it with something better (a single word would be perfect).
    But (module, component, plugin) are already taken and I don't
    like calling them "add-on".

Each **Extension module** is a Python module (or package), placed
in a given search path.

By default, the search path includes ``cms_modules_core``
and ``cms_modules_extra`` directories in the application folder, where
the first one is meant for modules shipped along with the CMS, and
the second for the extra downloaded modules.


The ``cms_module_info`` dict
============================

In order to be successfully recognized as a valid extension module,
the module must contain a dict named ``cms_module_info``, containing
something like this::

    cms_module_info = dict(
        ## Plugin descriptive label. Defaults to module name
        name='Example Plugin',
        
        ## Short description for this module
        description='Just an example plugin',
        
        ## Version of the extension module
        version='0.1-alpha',
        
        ## Minimum required core version
        core_version='0.1',
        
        ## List of other extension modules this module depends on
        ## In future, will be expanded to something more complex
        dependencies = [],
        
        ## Module metadata
        meta = dict(
            author='Samuele Santi <samuele@santi.co.it>',
            license='GPL',
            website='http://w2cms.com',
        ),
    )
        

**Explanation of keys**

name
    The descriptive name/label of the plugin, to be show
    on administrative pages.

description
    A brief description of the plugin, to be show on
    administrative pages.

version
    The version of the plugin, to be used for comparison.

core_version
    The minimum CMS core version to allow this plugin to be used.
    
    .. NOTE::
        * We might also want to support **maximum** core version, etc..
        * We might also want to add support for the min/max required
          **web2py** versions.

dependencies
    A list of other plugins on which this one depends.
    
    .. NOTE::
        We should add support for defining complex dependencies, such
        as dependency on specific version(s), conflict, ...

.. NOTE::
    We could also add support for "provides", saying a plugin can be
    used in place of another, or to provide some kind of service on
    which other plugins relay (such as user management or mail service)

meta
    Some metadata related to the module. Although this may contain
    anything, currently supported keys are:
    
    author
        Module author's name (and possibly email). Comma-separate
        multiple author names.
    
    license
        Identifier of the license under which the module is released.
        This is not well defined atm.
    
    website
        Homepage of the module
    
    package
        Name of the "package" this module belongs to.
        Packages are used to categorize modules in the administrative
        interface.


Defining extension components
=============================

Extension modules can contain several components that can then be loaded
and used by the core or other modules.

To find such components, a special ``@component`` decorator is used.


Code documentation
==================

Following is developers documentation of the underlying objects and API.

Extension manager
-----------------

The extension manager is instantiated as ``cms_extm`` in the ``db`` model,
and accessible from all controllers that needs to operate on with
extension modules.

.. TODO:: We need a smooth way to make it accessible to modules too..

.. autoclass:: cms_extension.ExtensionsManager
    :members:
    :special-members:
    :member-order: bysource


``@cms_component()`` decorator
------------------------------

.. autofunction:: cms_extension.cms_component


Dynamic block component
-----------------------

This type of extension module component is used to generate dynamic
blocks that can be placed inside the theme regions.

.. autoclass:: cms_extension.DynamicBlock
    :members:
    :special-members:
    :member-order: bysource


Node type manager component
---------------------------

.. autoclass:: cms_extension.NodeTypeManager
    :members:
    :special-members:
    :member-order: bysource


Custom controller component
---------------------------

.. autoclass:: cms_extension.CustomController
    :members:
    :special-members:
    :member-order: bysource
