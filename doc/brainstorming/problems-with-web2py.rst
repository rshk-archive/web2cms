#########################
Problems with web2py core
#########################

This is a list of all the issues found with the web2py core and other
framework-related stuff.


.. _issues_multi-field-unique-keys:

Multi-field UNIQUE keys
=======================
In many cases we need to ensure uniqueness on multi-field values,
such as entity references, or ``record,language`` for translations, ..

By default, web2py's ``DAL`` doesn't provide the ability to create
such multi-field UNIQUE keys so, while we try to ensure key uniqueness
on the application side, we should find another way to enforce this
on the database side too.

These are two ways to accomplish this:

* Use ``executesql()`` upon table creation to define unique keys,
  with different queries depending on the in use database type.
* Create a computed field containing values from the fields in the
  unique key group, and place an ``unique=True`` on that field definition.
