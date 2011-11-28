#####################
Default content types
#####################

This is a list of content types that should be defined / handled
in order to test / support a wide range of needed features.

.. NOTE::
    We should create modules defining ``NodeTypeController``s, in order
    to allow definition of these content types!
    We don't want content-types to be defined in core.
    Plus, we may need a way to handle user-defined content types -> how to?

Page
====

Standard pages. Should have a ``title`` and ``body``.
May be inserted in menus (by using standard menu items association).


Article
=======

Articles are used for "feed-like" content, such as blog posts, news, etc.
The only additional field might be ``picture`` to allow adding an image
to the post.

The main difference then will be in views / rendering of the content / etc.


Photo
=====

Represents a single photo.
Fields may be: ``photo``, ``title``, ``description``.

.. NOTE::
    To group photos into galleries, use **taxonomy**.

.. NOTE::
    To associate a location, use the **attributes**

.. NOTE::
    We'll need some **image management** to scale photos, apply effects,
    etc. -> write that
