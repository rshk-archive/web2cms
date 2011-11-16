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

User
    as defined by auth_user

Group
    as defined by auth_group

Node
    Used to represent content.
    Nodes also support versioning, with each version identified by a
    revision number + language.
    
    Node storage is spread over several tables.

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
    Used to organize heterogeneous entities in a tree.
    
    * **entity**
    * **parent**

Menu
    Container for menu links
    
    * **title** [->SHOULD SUPPORT TRANSLATION!]
    * **menu_id**

Menu_link
    * **title** [->SHOULD SUPPORT TRANSLATION!]
    * **parent**
    * **entity_type** An entity type or 'raw'
    * **entity_id** The entity id, or the URL if 'raw' specified.
    

User
====
A CMS user (as defined by ``auth_user``), plus some extra fields
for the user profile.


Group
=====
A group of users (as defined by ``auth_group``)


Node
====
A node is a "document", a piece of content with a type and some
attributes ("fields").

Nodes should support history / revisions.

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

``relationship``
    * ``entity_type``, ``entity_id``
    * ``other_type``, ``other_id``
    * ``relationship`` The relationship from ``entity`` to ``other``

.. TODO:: How to handle mutual vs non-mutual relationships?


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
