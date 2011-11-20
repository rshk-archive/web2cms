###################
Translation support
###################

**web2cms** must support translation for all the content, etc.; feature
that's missing or badly implemented in other CMS.

In order to support this, most tables will have a ``<tablename>_translation``
equivalent, containing translation for some fields of the table.

.. WARNING:: Interface langugage and content language should be kept separated,
    since the user may want to visit the content in an other language while
    keeping all the controls etc. in his own language!

.. TODO:: Find a way to use path prefixes for translation
    -> And then avoid controllers named with two-letter names!

.. NOTE::
    Problem with this is: how to implement quickly this database-side
    in order to allow quick searches on content? We need to search on
    the translated table instead of the real one, but only for some
    fields that are translated..
    
    Maybe, can be done by several filtering levels, or by massive indexing.

Desired language discovery
==========================

.. NOTE:: At the moment we consider only two-character language codes,
    such as "en", "it", etc. but then we should add support for
    country-codes too, such as "en_GB", "en_US", "it_IT", "it_CH", etc.
    How to handle this?
    
    * If a user wants "en_US" and we only have "en", we should return that.
    * If a user wants "en_US" and we only have "en_GB", we may return that.
    * What if a user wants "en_US" or "en" and we have only "en_GB" and "en_CA"?
    * Then, a browser may send a list of supported languages instead of just one,
      so should we return the first available, the most matching, or what?

The wanted language is determined this way:

* Forced language: either by path prefix or cookie setting, manually
  selected by the user, takes the absolute precedence.
* User preferred language: configured in the user settings
* One of the languages specified by the browser (contained in
  ``T.accepted_language``).
* Site default language.
* Language neutral -> no translation, pick values directly from the table.


Generic table translation
=========================

Each table ``mytable`` fields values can be translated using a corespondent
``t9n_mytable`` table. Structure is like this:

**mytable**
    * **id** - Serial auto-increment primary key
    * *field0* - Language neutral value for field0
    * *field1* - Language neutral value for field1
    * *field2* - Language neutral value for field2
    * ...
    * *fieldN* - Language neutral value for fieldN

**t9n_mytable**
    * **id** - Serial auto-increment primary key
    * **language** - Language code
    * **record** - Reference to the original table
    * *field0* - Translated value for field0, or NULL if no translation
    * *field1* - Translated value for field1, or NULL if no translation
    * *field2* - Translated value for field2, or NULL if no translation
    * ...
    * *fieldN* - Translated value for fieldN, or NULL if no translation
    
    .. WARNING:: We need an unique key on ``(record, language)``
