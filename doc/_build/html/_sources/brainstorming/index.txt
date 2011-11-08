#############
Brainstorming
#############

Some brainstorming about stuff to be implemented in the web2py CMS.

.. WARNING::
    This page lists features that may be included in the real project,
    but at the moment this is only brainstorming stuff.

.. NOTE::
    We need a name to define the CMS components/modules:
    
    * *module* is already in use for Python modules
    * *component* is a dynamically loadable component, used along with LOAD()
      and ``.load`` views.
    * *plugin* is a web2py extension component, but not structured in a way
      suitable for CMS extension.
    * *add-on* or *extension* are unallocated names that might be used.

.. NOTE::
    A lot of stuff is compared to Drupal_ or using Drupal terms, due to the author's
    experience with that CMS.

.. TODO::
    Make a list of stuff I'm commonly using in Drupal that would be cool to have
    implemented here.

.. TODO::
    Make a list of stuff that in Drupal is missing or not working as it should,
    but it would be useful to have.



Table of Contents
=================

.. toctree::
   :maxdepth: 2

   component-structure
   content-types



Features
========


Multiple content types
----------------------
At least, *page* and *article*, but the best would be to allow plugins
to define their own (as Drupal does).
  
See also: :doc:`content-types`


.. _feature-content-versioning:

Content versioning
------------------
Keep trace of old versions, etc.


.. _feature-custom-fields:

Custom fields
-------------

Generate a schema for each *node*, allow definition of additional fields, etc.

.. NOTE::
   Additional node types and fields may be user-defined.

.. NOTE::
   As for views, content types and fields should be defined in configuration
   files instead that in the database
  
   Many times definition of extension tables would be enough.
   We could make that if a table named ``node_<type>_fields`` exists,
   extra fields will be loaded and merged with the node.


.. _feature-image-manipulation:

Image manipulation
------------------
We need something that handles at least basic, preset-based image
manipulation; for example to create previews / thumbnails.

We should find a good way to generate on-the-fly the images and then
have a static cache from which files are served directly from the web server.

Of course, the cache must be also flushed upon changes in preset / image, etc.


.. _feature-input-formats:

Input formats
-------------
  As in Drupal, different formats that gets converted into HTML.

  Example: HTML, reStructuredText, restricted HTML, bbcode (is this already
  used??), markmin (web2py-specific reST-like markup), wiki markup, ...


.. _feature-taxonomy:

Taxonomy
--------
To manage tree-structured tags / categories / ...
  
.. TODO::
    Make this a ``LOAD()``able component, since everything may be
    tagged/categorized.


.. _feature-flagging:

Flagging
--------
  Flagging is the adding of extra attributes to things.
  Attributes usually are key/value pairs.
  
  .. TODO:: Make this a ``LOAD()``able component.


.. _feature-blocks-regions:

Blocks and regions
------------------
  Both user-defined and component-defined.
  
  .. TODO::
     Make this a ``LOAD()``able component. This way we could also easily
     support something big-pipe-like with dynamic ajax loading of stuff.


.. _feature-comments:

Comments
--------
Everything could potentially be commented, not only nodes.
  
.. TODO:: Make this a ``LOAD()``able component.


.. _feature-users-profiles:

Users + profiles
----------------
  We need users, user profiles, user roles + permissions sets, etc.
  See also: :ref:`feature-access-control`


.. _feature-access-control:

Access control
--------------

While most of this is already handled by web2py, we should also support
more complex **"permissions hierarchy"**, at different granularity/depth
levels: many permissions could be defined and checked in order
to allow an action to be performed.

For example, for the editing of an "article" node, checked permissions
may be:

===========  ====================================  =========
Action       Object                                Id
===========  ====================================  =========
god-like
any          any node
any          own nodes (if own node)
any          any "article" node
any          own "article" nodes (if own node)
edit         any node
edit         own nodes (if own node)
edit         any "article" node
edit         own "article" nodes (if own node)
edit         specific node                         node.id
===========  ====================================  =========
    
.. NOTE::
   **God-like** permission is the one usually granted to user #1

Plus, there might be other custom-defined checks; for example a module
managing workflows might check whether the content editing should
be allowed for content on this state or not.


.. _feature-configuration:

Configuration registry
----------------------
Something like Drupal variables, but more advanced.

.. TODO:: Decide whether and how to mix ini files and database configuration.


.. _feature-expandible-structure:

Plugin-expandible structure
---------------------------
  We need to support plugins in order to allow extending the functionality.
  All the stuff that is not the core, must go in a plugin.


.. _feature-ajax-loading:

Ajax loading (Future plan)
--------------------------
  Something like Facebook BigPipe, allow fetching of page components without
  actually reloading the page. This could be seen also as something like
  client-side views rendering.

  .. NOTE::
    We could also experiment with XML + XSL transformations in order
    to do this.
  
  .. NOTE::
     We could also make benefit of the ``LOAD()`` mechanism to accomplish
     this, at least for regions containing blocks.


.. _feature-webservices:

Web services
------------
We should allow the application to expose web services.

* **REST** is a must-have for any (r|d)ecent web application.

.. TODO::
   Decide whether to allow also WebDAV methods (copy, move, ...)
   for some stuff or not.

* **XML-RPC** can be used to expose API for particular calls that cannot be
  represented using  REST



.. _nice-stuff:

Nice stuff
==========

These are not "real" features, but nice additions that makes the
user-experience better.


WYSIWYG editor
--------------
Something like CKEditor; we also need some better file selector
and custom plugins to integrate with the CMS.

.. NOTE::
   We might support per-input-format editors/editor configurations;
   the editor should be ``LOAD()``ed using a component (also make sure
   all the loading is done only on the JS-side, in order to gracefully
   regress to a simple ``textarea`` if no JS is enabled.)


File browser
------------
A proper file browser is needed in order to allow users upload and
manipulate files.
The only problem is setting ACLs on directories/files -> how to do in a
clean way?

.. NOTE::
   There is also an application called ``file_manager`` that might be
   converted into a plugin/component.


Fancy JavaScript FX and stuff
-----------------------------
* Custom widgets (extjs? or jQuery UI, jQuery-based is better, check
  projects features / statuses)
* Lightbox to open images/files/links/..?
* Overlay for administration stuff, etc.



Theming support
===============

We should support easily re-theming minimizing the needs of views altering
+ handling reasonable defaults for unhandled cases.

.. NOTE::
    Many times a whole theme is unnecessary, as a color change / small layout
    adjustment would be enough. So, we should handle these cases:
    
    * Custom themes that e.g. use different CSS framework, HTML version
      or provide different **structural** features.
    * Themes that provide CSS customization to another structured theme,
      but without need of altering the views.

Mobile version
--------------
  This may be accomplished by allowing views selection to consider also stuff
  like the user-agent, the browser window size, etc.
  Or maybe, selection could also be done by subdomain (``example.com`` is the
  standard version, ``m.example.com`` is the mobile version,
  ``text.example.com`` is the plain-text light version, ``api.example.com``
  is used to make REST API calls, ...)
  
  .. NOTE::
     Probably best thing would be to have custom CSS rules that gets applied
     for the mobile version.
     
     In some other cases, a complete structure change may be wanted.
     How to handle this? -> Custom views, defaulting to the html ones?
     (Something like ``*.mobile`` ?)



Customizable views support
==========================

We need a mechanism to define custom content visualizations, in a way similar
to what the `Views Drupal module`_ does.

  A mechanism to create custom visualizations for content / stuff.
  This includes everything: standard pages, rss feeds, xml sitemaps, ...

  .. NOTE::
    Views should be defined in *files*, not in the database!    
    We want to keep well separated what is the structure from what is data!



Useful plugins
==============

This is a quick list of features that may be nice to see included in
the CMS.

- OpenID
- Social network integration (Facebook, twitter, status.net, ...)
- QR Codes generation for each page



..
    Links should be placed down here
    --------------------------------

.. _`Drupal`: http://drupal.org/
.. _`Views Drupal module`: http://drupal.org/project/views
.. _`Drupal imagecache module`: http://drupal.org/project/imagecache
