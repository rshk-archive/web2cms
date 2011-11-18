############
CMS Elements
############

This is a description of the base elements that should be managed in order
to build a fully-featured CMS upon it.

By building a schema to limit element interaction, we should be able to build
a quite complex structure. 

* Each entity is identified by ``(type, id)``.
* Entities CRUD must be accessed **only** via an entity manager contained
  in the ``cms_tools`` module. No manipulation should be done on the
  database directly.

Comment (``object (entity), author (user), comment details``)
    Comment attached to an entity.
    
    * **object** (entity)
    * **author** (entity, type=user)
    * **creation/update date**
    * Comment-specific data (usually title and body)

Flag
    * **object** (the flagged object)
    * **author** (the flagging object, usually user)
    * **key/value**
    * Unique key: ``object,author,key``

Relationship
    * **entity**
    * **other**
    * **relationship** An identifier for the relationship
    * Unique key: ``entity,other,relationship``

Attribute
    * **object**
    * **key/value**
    * Unique key: ``object,key``

Vocabulary
    Used to contain tags. Used to provide some constraint + autogeneration
    of terms (eg. for tagging).

Term
    * **vocabulary**
    * **title** [->SHOULD SUPPORT TRANSLATION!]
    * **parent**
    * Definition of constraint on allowed content, etc.

Term_membership
    * **entity**
    * **tag**  

Tree_organization
    The tree organization can be accomplished just using relationships.


Generic, re-used fields
=======================

These are virtual tables, to be re-used where needed.

Table: ``signature``
    * Field('created_date', 'datetime', default=request.now),
    * Field('created_by', db.auth_user, default=auth.user_id),
    * Field('updated_date', 'datetime', update=request.now),
    * Field('updated_by', db.auth_user, update=auth.user_id))


    
User
==========
A CMS user (as defined by ``auth_user``), plus some extra fields
for the user profile.



Group
==========
A group of users (as defined by ``auth_group``)



Node
==========
A node is a "document", a piece of content with a type and some
attributes ("fields").

The node is the most complex object to be handled in the CMS, since
it must support revisions, custom fields and of course translation.

Database model
--------------

Table: ``node``
    Metadata information on the node.
    
    * **type** ``string(64)`` - Identifier of the node type
    * **published** ``boolean`` - Whether the node is published or not
    * **weight** ``integer`` - Weight is used to reorder nodes in lists.
    * -> signature

Table: ``node_revision``
    Information about node revisions.

    * **node** ``reference node``
    * **published** - Whether the revision is published or not
    * **translation_base** - Language this revision was first written in
    * ->signature

Table: ``node_fields_base``
    Base fields, shared between all the node types.
    
    * **id**
    * **node_revision** ``reference node_revision``
    * **title** ``string(128)``
    * **body** ``text``
    * **body_format** ``string(64)``

Table: ``t9n_node_fields_base``
    Translation for ``node_fields_base``.
    
    * **record** ``reference node_fields_base`` - The record to be translated
    * **language** ``string(32)`` - Language code
    * Node revision is fixed, cannot be translated!
    * **title** ``string(128)``
    * **body** ``text``
    * **body_format** ``string(64)``

Table: ``node_fields_<name>``

Table: ``node_<type>_fields_<name>``
    Where usually ``<name>`` is the name of the CMS Plugin defining
    the extra fields for all nodes / a given node type.
    
    Minimum fields are:
    
    * **version** ``reference node_translation``

Then, of course, ``node_fields_<name>`` and ``node_<type>_fields_<name>``
tables can have their ``t9n_<tablename>`` translations.

.. NOTE::
    Each node version is uniquely identified by ``node_version.id`` or,
    better, by a tuple of the ``node_version`` fields ``node``,
    ``revision_id``, ``language``.

.. WARNING::
    Beware that for ``version_id``, ``node_version.id`` is meant;
    ``version_id`` uniquely identifies that exact revision/translation
    for the node.
    
    To indicate the document **revision**, the term ``revision_id``
    is used instead. Revisions owns multiple translations, versions not.

Database model
--------------

.. TODO::
   Use this structure, or something with ``node`` plus ``node_revision``?
   And, how to store revisions for other node types?
   Use "groups" to group revisions of the same node? -> not very cool!
   Plus, we should find a cool way to manage content translations!

* ``node_id`` This is *not* the table id!
* ``node_type``
* ``revision_id``
* ``title``, ``body``


Taxonomy/tags
=============
A "tag" is a category that may contain entities, and have a hierarchical
tree structure.


Database model
--------------

``taxonomy_term``
    * ``id`` is the Term ID used in references
    * ``parent`` Self-references ``taxonomy_term``
    * ``label`` Label to identify the term

``taxonomy_term_membership``
    * ``term_id``
    * ``entity_type``, ``entity_id``


Comment
=======
A comment is a short text associated to another entity.

* Usually contains title,body,author and date.
* Comments should support nesting

Database model
--------------

``comment``
    * ``entity_type``, ``entity_id``
    * ``title``, ``body``
    * ``author``, ``created_date``, ``updated_date``

.. TODO:: Support revisions for comments too?


Flag
====
Flags are used to let ``entity`` put a ``key|value`` on ``entity``.

Flags should always be placed by their ``flagged_by_type``, ``flagged_by_id``
user or entity.

Database model
--------------

``flag``
    * ``entity_type``, ``entity_id`` Flagged entity
    * ``flag_name``, ``flag_value`` Name and value of the placed flag
    * ``flagged_by_type``, ``flagged_by_id`` Entity that put the flag
    * Extra stuff, such as set date, ... may be added.
    * Comments should be added using comments only.

Examples
--------

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


Relationship
============
Relationships are used to link together two entities.
Relationships usually express more interaction that just placement of a flag,
anyways this could be easily implemented for non-mutual relationships
using just a flag.

Table: ``relationship``
    * ``entity_type``, ``entity_id``
    * ``other_type``, ``other_id``
    * ``relationship_name`` The relationship from ``entity`` to ``other``

.. TODO:: Possibly, we could add other fields to relationships -> ?
.. TODO:: How to handle mutual vs non-mutual relationships?

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


Menu
====
Container for menu links

Table: ``menu``
    * **title** ``string``
    * **menu_name** [UNIQUE,REQUIRED] - The internal name to be used to refer to this menu

Table: ``menu_translation``
    * **menu** ``menu.id``
    * **language** ``string`` [REQUIRED] - The language code
    * **title**


Menu link
=========

Menu link spawns over two tables: ``menu_link`` and ``menu_link_translation``.

Table: ``menu_link``
    * **id** The usual ID
    * **title** ``string``
    * **parent** ``menu_link.id`` (self-reference)
    * **entity_type** An entity type or literal 'raw'.
    * **entity_id** The entity id, or the URL if 'raw' specified.

Table: ``menu_link_translation``
    * **menu_link** ``menu_link.id`` [REQUIRED]
    * **language** ``string`` [REQUIRED] - The language code
    * **entity_type** (Possible rewrite for this language)
    * **entity_id** (Possible rewrite for this language)

Content display
===============
Content displays are "advanced" views that define how to pick content
and render it.
They should not be placed in the database but in the configuration.
(Or should we allow both?)


Configuration
=============
Configuration is structured in a "registry" way, and stored on filesystem
and/or database.


