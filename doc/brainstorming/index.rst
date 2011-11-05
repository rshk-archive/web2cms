Brainstorming
#############

Some brainstorming about stuff to be implemented in the web2py CMS.

.. WARNING::
   This page lists features that may be included in the real project,
   but at the moment this is only brainstorming stuff.

A lot of stuff is compared to Drupal or using Drupal terms, due to the author's
(~redShadow~) experience with that CMS.

.. TODO::
   Make a list of stuff I'm commonly using in Drupal that would be cool to have
   implemented here.

.. TODO::
   Make a list of stuff that in Drupal is missing or not working as it should,
   but it would be useful to have.


Contents
========

.. toctree::
   :maxdepth: 2

   component-structure



Features
========

**Different types of content** [DONE]
  At least, *page* and *article*, but the best would be to allow plugins
  to define their own (as Drupal does).

**Input formats**
  As in Drupal, different formats that gets converted into HTML.

  Example: HTML, reStructuredText, restricted HTML, bbcode (is this already
  used??), markmin (web2py-specific reST-like markup), wiki markup, ...

**Taxonomy**
  To manage categories, tags, etc. etc.

**Blocks**
  Both user-defined and component-defined.

**Comments**
  Everything could potentially be commented, not only nodes.

**Users + profiles**
  We need users, user profiles, user roles + permissions sets, etc.

**Configuration registry**
  Something like Drupal variables, but more advanced.
  We might also use ini files to store some configuration... ?

**Plugins**
  We need to support plugins in order to allow extending the functionality.
  All the stuff that is not the core, must go in a plugin.

**Ajax loading** (Future plan)
  Something like Facebook BigPipe, allow fetching of page components without
  actually reloading the page. This could be seen also as something like
  client-side views rendering.

  .. NOTE::
    We could also experiment with XML + XSL transformations in order
    to do this.

**Web services**
  We should allow the application to expose web services.

  - REST is almost a must-have.

    .. TODO::
       Decide whether to allow also WebDAV methods (copy, move, ...)
       for some stuff or not.

  - XML-RPC can be used to expose API for particular calls that cannot be
    represented using  REST



Nice stuff
==========

These are not "real" features, but nice additions that makes the
user-experience better.

**wysiwyg editor**
  Something like CKEditor; we also need some better file selector
  and custom plugins to integrate with the CMS

**File browser**
  A proper file browser is needed in order to allow users upload and
  manipulate files.
  The only problem is setting ACLs on directories/files -> how to do in a
  clean way?

**Fancy javascript stuff**
  - Custom widgets (extjs?)
  - Lightbox to open images/files/links/..?
  - Overlay for administration stuff, etc.

**mobile version**
  This may be accomplished by allowing views selection to consider also stuff
  like the user-agent, the browser window size, etc.
  Or maybe, selection could also be done by subdomain (``example.com`` is the
  standard version, ``m.example.com`` is the mobile version,
  ``text.example.com`` is the plain-text light version, ``api.example.com``
  is used to make REST API calls, ...)


Stuff similar to Drupal
=======================

**views**
  A mechanism to create custom visualizations for content / stuff.
  This includes everything: standard pages, rss feeds, xml sitemaps, ...

  .. NOTE::
    Views should be defined in *files*, not in the database!	
    We want to keep well separated what is the structure from what is data!

**fields**
  Generate a schema for each *node*, allow definition of additional fields,
  etc...

  .. NOTE::
    As for views, content types and fields should be defined in configuration
    files instead that in the database

**image manipulation**
  Like Drupal imagecache module, allow some image trasformation (preset-based?)
  Also find a good way to serve pre-generated static content.


Useful plugins
==============

- OpenID
- Social network integration (Facebook, twitter, status.net, ...)
- QR Codes generation for each page
