############
CMS Elements
############

.. NOTE::
    The term **element** (or sometimes **entity**), refers to one of the
    "base objects" that are used to build the CMS structure.

Each element is identified by its ``(type, id)``.
This way, we can build flexible references, easy-understandable URLs, etc.

By building a schema to limit element interaction, we should be able to build
a quite complex structure. 


.. WARNING::
    All the manipulation of elements must be done only via an entity
    manager, either defined in the ``cms_tools`` module (usually named
    something like ``<Element-name>Manager``, and derived from
    ``EntityManager``).
    All the direct database manipulation must be avoided at any cost.

.. WARNING::
    There could be some issues due to the lack of multi-field unique
    keys definition support from the DAL.
    
    See also: :ref:`issues_multi-field-unique-keys`.


**Elements index**

* :ref:`element-user-group` -- Management of persons, groups and permissions
* :ref:`element-node` -- The actual CMS content
* :ref:`element-comment` -- Short comments associated with other entities
* :ref:`element-taxonomy` -- Taxonomy terms used to categorize entities
* :ref:`element-attribute` -- Additional attributes for entities
* :ref:`element-flag` -- Associate two entities and a key|value pair
* :ref:`element-relationship` -- Associate two entities in a relationship
* :ref:`element-menu` -- Manage lists of links
* :ref:`element-display` -- Display content in custom ways
* :ref:`element-setting` -- Manage configuration values

**Other documentation**

* :ref:`multipurpose-fields` - Fields used in many tables
* :ref:`element-translation` - How multi-language environment is handled

**Current development status**

================  ===========  ===========  ===========
Element           Defined      Implemented  Tested
================  ===========  ===========  ===========
node              YES          PARTIAL      NO
comment           YES          NO           NO
taxonomy          YES          NO           NO
attribute         YES          NO           NO
flag              YES          NO           NO
relationship      YES          NO           NO
menu              YES          NO           NO
display           NO           NO           NO
settings          ALMOST       PARTIAL      NO
================  ===========  ===========  ===========



.. _multipurpose-fields:

Multi-purpose fields
====================

This is a list of standard fields that can be re-used in other tables.

Table: ``signature``
--------------------
Used to store standard author/date signature.

::

    signature = db.Table(db, 'cms_signature',
        Field('created_date', 'datetime', default=request.now),
        Field('created_by', db.auth_user, default=auth.user_id),
        Field('updated_date', 'datetime', update=request.now),
        Field('updated_by', db.auth_user, update=auth.user_id))
    
    signature.created_date.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))    
    signature.updated_date.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))
    signature.created_by.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
    signature.updated_by.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
    signature.created_by.represent = user_name_represent
    signature.updated_by.represent = user_name_represent


.. TODO::
    Replace ``created_by`` and ``updated_by`` with more generic
    ``created_by_type``, ``created_by_id``, ``updated_by_type``,
    ``updated_by_id`` ?


Table: ``t9n_fields``
---------------------
Standard fields for the ``t9n_*`` tables.

::

    t9n_fields = db.Table(db, 'cms_t9n_fields',
        Field('language','string',length=32))


.. _element-translation:

Element translation
===================
All the elements may be translated to support multi-language environments.

This is semi-automatically handled by using ``t9n_<tablename>`` tables
which values are merged with the ones from ``<tablaname>`` when
performing some kind of queries / element retrieval.

That's one reason why all the manipulation **must** pass from
the element managers.



.. _element-user-group:

Users and groups
================
CMS Users and Groups are the standard ones defined by ``Auth``, plus:

* ``anonymous user`` special group
* User profile; additional fields associated with users

.. NOTE::
    User profiles can be accomplished using attributes



.. _element-node:

The ``node`` element
====================

Nodes are the base element used to represent a piece of content.
They support versioning, translation and storage of data in linked tables.

Then, extension modules can define their own ``NodeTypeManager`` objects
that can be used to manage a given node type in a particular way.

Fields: ``author entity``, ``date``, ``content``
Spawn into multiple tables to support versioning



.. _element-comment:

The ``comment`` element
=======================

A comment is an (usually very short) piece of content associated by an user,
on a date, to a specified entity.

Fields:

* ``commented entity``
* ``commenting entity``
* ``parent comment``
* ``date``
* ``content``



.. _element-taxonomy:

Taxonomy and terms
==================
Terms are used to categorize entities.

* Terms could have hierarchical structure
* Terms are grouped into vocabularies
* Vocabularies define some rules on contained terms usage / manipulation
* Terms should support translation.

In database, they are stored as:

* Vocabulary definition
* Term definition
* Term membership: ``term id``, ``entity``



.. _element-attribute:

Additional attributes
=====================
Attributes associate extra values to a given entity.
They might be quite complex and so we need an extension component to
handle special cases.

Fields: ``entity``, ``key``, ``value``



.. _element-flag:

Flagging
========
Flags are used to let an ``entity`` put a ``key|value`` on another ``entity``.

Fields:

* ``flagged entity``
* ``flagging entity``
* ``key|value``

Real-world usage examples
-------------------------

"Like" function::

    entity_type = node
    entity_id = 25
    flag_name = like
    flag_value = ''
    flagged_by_type = user
    flagged_by_id = 13

Fivestar rating::

    entity_type = node 
    entity_id = 25
    flag_name = fivestar
    flag_value = 5
    flagged_by_type = user
    flagged_by_id = 13



.. _element-relationship:

Relationship
============
Relationships are used to link together two entities.
Relationships usually express more interaction that just placement of a flag,
anyways this could be easily implemented for non-mutual relationships
using just a flag.

Fields:

* ``entity``
* ``other entity``
* ``relationship_name``

.. TODO:: Possibly, we could add other fields to relationships [?]
.. TODO:: How to handle mutual vs non-mutual relationships [?]

.. NOTE::
    Tree structure can be well represented using the "child" relationship.

Examples
--------

Tree structure organization of nodes (book, ..):

===========  =========  ==========  ========  =================
entity_type  entity_id  other_type  other_id  relationship_name
===========  =========  ==========  ========  =================
 node         2          node        1         child
 node         3          node        1         child
 node         4          node        3         child
 node         5          node        3         child
 node         6          node        4         child
===========  =========  ==========  ========  =================

This can be used to create a structure like this::

    node 1
    |-- node 2
    '-- node 3
        |-- node 4
        |-- '-- node 6
        '-- node 5

.. WARNING:: Beware that this way we cannot be absolutely sure there aren't
    infinite loops or other problems in the tree, therefore we should
    either enforce checks before inserting, or find a way to handle such cases.



.. _element-tree:

Tree structure
==============

The tree structure can be represented using the ``child``
:ref:`relationship <element-relationship>`.



.. _element-menu:

Menu and links
==============

Menus are used to group links and then be used for navigation,
blocks, drop-down menus, ...

In database, they are stored as **menu** and **menu_item**.

* **Menu** - defines a menu that can contain some links
* **Menu item** - is a single item to be placed in a menu

About menu items
----------------

**Fields:**

* ``menu`` - reference to ``menu.id``

Container for menu links

Table: ``menu``
    * **title** ``string``
    * **menu_name** [UNIQUE,REQUIRED] - The internal name to be used to refer to this menu

Table: ``menu_translation``
    * **menu** ``menu.id``
    * **language** ``string`` [REQUIRED] - The language code
    * **title**



.. _element-display:

The ``display`` element
=======================
Content displays are "advanced" views that define how to pick content
and render it.
They should not be placed in the database but in the configuration.
(Or should we allow both?)



.. _element-setting:

Configuration and settings
==========================

More stuff can be found in the :doc:`modules/cms_settings` module.
