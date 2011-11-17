###########
CMS Plugins
###########

.. TODO:: Find a non-clashing name for the cms plugins/components/pieces/..

Each **CMS plugin** is a Python module (or package), placed in the
``cms_plugins``, inside the w2cms application folder.


The ``cms_plugin_info``
=======================

In order to be successfully recognised as a plugin, and subsequentially
loaded, it is required to contain a dict named ``cms_plugin_info``,
structured like this::

    cms_plugin_info = dict(
        name='Example Plugin', ## Plugin descriptive label
        description='Just an example plugin',
        version='0.1-alpha', ## Version of the cms_plugin
        core_version='0.1', ## Minimum required core version
        dependencies = [], ## Other cms_plugins this plugin depends on
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


Other cms_plugin members
========================

Plugins can contain several objects, to be used to change or enhance
behavior of the CMS or other plugins.
When a plugin is loaded, its content is scanned for sub-classes of some
well-known objects.

Found matching objects can then be instantiated and used.

