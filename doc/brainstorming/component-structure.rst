####################
Components structure
####################

.. WARNING::
    The "component" term is already used for ``LOAD()``able web2py components
    and so should be changed into something like "add-on" or "extension".

This page describes how components should be structured and work. 

What components should be able to do
====================================

* Add new content types, with custom fields, management, visualization, ..
* Extend existing content types, by adding fields
  * New fields should then be included in the views too
* Define blocks
* Create new controllers
* Create "content views" to display content with a custom render
* Extend the menu to attach new items


How to read components
======================

One way might be:

* Import the component package
* List package members, and depending on their type, use for different
  actions.

Example add-on module::

    ## The import is needed since we don't want to eval() this..
    from cms_addons import NodeDefinitionAddon, CustomControllerAddon
    
    class MyNewNode(NodeDefinitionAddon):
        def define_tables(self, db):
            db.define_table('mynode', ... )
        
        def insert(node, db):
            db.mynode.insert(node)
            super(self).insert(node, db)
    
    class MyCustomController(CustomControllerAddon):
        def my_function(request):
            return "Hello from my controller!"

