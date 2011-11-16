'''
Miscellaneous tools for the CMS.

This includes mostly CRUD / management for base elements and all the stuff
that needs quick importing from a single module.

Also, we should provide ``__all__`` to limit the amount of imported stuff.

.. WARNING:: Language is being intentionally ignored at the moment!

We need to decide exactly how to handle the language selection mechanism,
so for the moment just one language is used.

'''

__all__ = ['CmsDB']

import gluon.dal
from gluon import *
from gluon.storage import Storage

##==============================================================================
## CMS Database object
##==============================================================================

class CmsDB(object):
    """Wrapper for DB, to be used to access CMS entities.
    """
    
    _db = None
    _managers = None
    
    _current_language = None
    _default_language = None
    _working_user = None
    
    def __init__(self, db, language=None, user=None):
        ##@todo: load default language from configuration
        self._default_language = 'en-en'
        
        self._db = db
        self._current_language = language or self._default_language
        self._working_user = user
        self._managers = {}
        self._managers['node'] = NodeManager(self)
    
    def __getattr__(self, name):
        if self._managers.has_key(name):
            return self._managers[name]
        raise AttributeError('%r object has no attribute %r' % (type(self).__name__, name))
    
    def __getitem__(self, key):
        try:
            return self.__getattr__(key)
        except AttributeError:
            raise KeyError(str(key))
    
    def get_working_user(self):
        if self._working_user is not None:
            return self._working_user
        else:
            return current.user
    
    def set_working_user(self, working_user):
        self._working_user = working_user
    
    def set_current_language(self):
        pass
    
    def get_current_language(self):
        pass


##==============================================================================
## Base classes
##==============================================================================

class ElementManager(object):
    ## To store CMSDB
    _cmsdb = None
    
    def __init__(self, cmsdb):
        self._cmsdb = cmsdb
    
    @property
    def db(self):
        return self._cmsdb._db
    
    @property
    def cmsdb(self):
        return self._cmsdb
    
    @property
    def current_language(self):
        return self._cmsdb.get_current_language()
    
    @current_language.setter
    def current_language(self, value):
        self._cmsdb.set_current_language(value)
    
    @property
    def current_user(self):
        return self._cmsdb.get_working_user()
    
    @current_user.setter
    def current_user(self, value):
        self._cmsdb.set_working_user(value)

class ElementEntity(object):
    
    _db_row = None
    _cmsdb = None
    
    def __init__(self, db_row=None, cmsdb=None):
        self._db_row = db_row
        self._cmsdb = cmsdb
    
    @property
    def db(self):
        return self._cmsdb._db
    
    def __getattr__(self, name):
        if self._db_row.has_key(name):
            return self._db_row[name]
        raise AttributeError("No such attribute: %r" % name)
    
    def __getitem__(self, key):
        try:
            return self.__getattr__(key)
        except AttributeError:
            raise KeyError(str(key))


##==============================================================================
## Entity: node
##==============================================================================

class NodeManager(ElementManager):
    """Class to be used when interacting with nodes.
    All the node handling / CRUD / .. should pass from this class
    instead of using the DAL directly, in order to correctly handle
    revisions / language and multi-table data storage.
    """
    
    ## Standard CRUD -----------------------------------------------------------
    
    def create(self, values, language=None):
        """Create a new node, using values from the ``values`` object.
        
        If ``values`` is a ``NodeEntity``, multiple versions may be created,
        else, just a first revision containing selected data is created
        and set as translation source.
        
        :param values: Values to be stored for the first version of the node.
        :type values: one of (``NodeEntity``, ``NodeVersion``,
            ``gluon.storage.Storage``, ``dict``)
        :param language: The initial language for the node. Defaults
            to ``values._language``, if set, or to the current language.
        :return: the ID of the newly created node
        """
        
        db = self.db
        
        try:
        
            row_node = {
                'type' : values.get('type', ''),
                'weight' : values.get('weight', 0),
                'published' : values.get('published', True),
            }
            
            node_id = db.node.insert(**row_node)
            
            row_node_version = {
                'node' : node_id,
                'revision_id' : 1, # first revision for this node
                'language' : values.get('language', 'neutral'),
                'published' : values.get('published', True),
                'is_translation_base' : True,
            }
            
            version_id = db.node_version.insert(**row_node_version)
            
            row_node_base_fields = {
                'node_version' : version_id,
                'title' : values.get('title', 'Untitled node %d' % node_id),
                'body' : values.get('body', ''),
                'body_format' : values.get('body_format', 'html-full'),
            }
            
            db.node_base_fields.insert(**row_node_base_fields)
        
        except:
            db.rollback()
        else:
            db.commit()
        
        return node_id
    
    def read(self, node_id, revision=None, language=None):
        """Load a given node object, by id.
        
        :return: A ``NodeEntity`` object containing values for the whole node.
        """
        
        return NodeEntity(self.db.node[node_id], self._cmsdb)
    
    def update(self, values, node_id=None):
        """Update the selected node.
        
        :param values: a ``NodeEntity``
        :param node_id: Id of the node to be updated.
            Defaults to ``values._node_id``
        """
        pass
    
    def delete(self, node_id):
        """Delete a whole node, including all its version / related data.
        
        :param node_id: Id of the node to be deleted
        """
        pass
    
    ## Versions management =====================================================
    
    def create_version(self, values, node_id=None, revision_id=None, language=None):
        """Create a new veersion for the node.
        
        :param values: Values to be stored for the new version.
        :type values: ``NodeVersion`` or ``gluon.storage.Storage`` or ``dict``
        :param node_id: Node for which to create version.
            Defaults to ``values._node_id``. This is **requried**
        :param revision_id: The revision ID for which to create new version.
            * If set to ``None``, defaults to latest revision
            * If set to ``-1``, create a new revision
            * If set to an ``int``, check that is a valid revision_id.
        :param language: The language of the new version.
            Defaults to current language.
        """
        pass
    
    def read_version(self, node_id, revision_id=None, language=None):
        """Gets the selected version for the selected node.
        
        :param node_id: Selected node id.
        :param revision_id: Selected node revision. Defaults to latest
            published version.
        :param language: Selected language. Defaults to the first found in:
            * Current language
            * Default site language (?)
            * Translation source for the revision
        """
        pass
    
    def update_version(self, values, node_id=None, revision_id=None, language=None):
        """Update the selected node/version/translation.
        
        :param values: Values to be set for the node.
        :type values: ``NodeVersion`` or ``gluon.storage.Storage`` or ``dict``
        :param node_id: Id of the node to be updated
            Defaults to ``values.node_id``
        :param revision_id: Node revision to be updated.
            Defaults to ``values._revision_id``.
        :param language: Language to be updated.
             Defaults to values._language
        
        .. WARNING:: Allowing optional ``revision_id`` and ``language`` is
            potentially risky -> should we allow that?
        """
    
    def delete_version(self, node_id, revision_id=None, language=None):
        """Delete the selected node version / revision / translation.
        
        :param node_id: The node for which to delete version(s)
        :param revision_id: Limit deletion to versions for this revision
        :param language: Limit deletion to versions for this language
        """
        pass
    
    ## Querying / searching ====================================================
    
    def search(self, query=None, orderby=None, language=None):
        """Search for nodes.
        """
        db = self.db
        return [
            NodeEntity(row, self._cmsdb)
            for row in db(query).select(db.node.ALL, orderby=orderby)
            ]

class NodeEntity(ElementEntity):
    """\
    Class representing a CMS node.
    
    * A __getattr__ (+ __getitem__) should return the current fields
    * versions contain the versions -> lazy property
    * Language resolution works checks for:
    
      * Requested language or current language or site default
      * Node translation source
    
    * Versions are structured in a tree, with ``revision_id``
      -> ``list`` of ``versions``.
    * We should use lazy loaders for the node entities, in order to
      minimize queries and memory usage
    * We should mark modified fields / versions in order to minimize
      queries on update, sice possibily a node may have quite a lot of
      revisions + external tables and it's not a good idea to always
      update them all!
    
    
    Values retrieval + dict-like behavior.
    All the values for the node will be retrieved from:
    
    * self._db_row
    * self._db_row.node_version.select() --> for the current version [AKA self.latest_version]
    * For each self.latest_version, all the fields that are a gluon.dal.Set
      will be select()ed and the field searched inside.
    
    .. TODO:: How to get a list of available fields without actually running
        queries? (-> Exploring the DAL, that's how)
    """
    
    node_id = None
    versions = None
    revision_numbers = None
    languages = None
    
    _current_language = None
    
    @property
    def versions(self):
        """Returns all the versions for this node, as database rows.
        """
        return self._db_row.node_version.select(orderby=
                self.db.node_version.revision_id |
                ~self.db.node_version.is_translation_base |
                self.db.node_version.language)
    
    @property
    def latest_version(self):
        return self._get_latest_version()
    
    @property
    def first_version(self):
        return self._get_first_version()
    
    def _get_latest_version(self):
        """Returns the latest version for this node, looking for:
        
        * Published version
        * Highest revision number
        * Current language
        * Default site language
        * Translation base
        
        * If a published version exist, it should be preferred over
          non-published versions, even if more recent.
        """
        db = self.db
        
        ## TODO: Make the orderby configurable, even on a per-node-type basis
        
        return self._db_row.node_version.select(
            orderby=~db.node_version.published |
            ~db.node_version.revision_id |
            ~(db.node_version.language=='en-en') | ## TODO: Replace 'en-en' with current language(s)!
            ~(db.node_version.language=='en-en') | ## TODO: Replace 'en-en' with default language!
            ~db.node_version.is_translation_base 
            ).first()

        ## If we want to do something more complex:
        #return db(db.node_version.node==self._db_row)(db.node_version.published==True).select(
        #    orderby=~self.db.node_version.revision_id | self.db.node_version.language,
        #    ).first()
    
    def _get_first_version(self):
        db = self.db
        return self._db_row.node_version.select(
            orderby=db.node_version.revision_id |
            ~db.node_version.is_translation_base |
            db.node_version.id 
            ).first()
    
    def __getattr__(self, name):
        ## Fields from db.node
        if self._db_row.has_key(name):
            return self._db_row[name]
        
        ## Fields from db.node_version, for the latest version
        _lv = self._get_latest_version()
        if _lv.has_key(name):
            return _lv[name]
        
        ## Search in all the back-references
        for k in _lv.keys():
            ## TODO: Improve this check a bit!
            if isinstance(_lv[k], gluon.dal.Set):
                for r in _lv[k].select():
                    ## All the rows have the same fields!
                    ## So, the first one will always return
                    if r.has_key(name):
                        return r[name]
        
        ## Pass to the default
        return ElementEntity.__getattr__(self, name)


#class NodeVersion(object):
#    """Class representing a CMS node version.
#    
#    .. TODO:: Is this needed anymore?
#    """
#    
#    _node_meta = None
#    _node_values = None
#    
#    def __init__(self, node_id, revision_id, language, version_id, values):
#        self.__dict__['_node_meta'] = {
#            'node_id' : node_id,
#            'revision_id' : revision_id,
#            'language' : language,
#            'version_id' : version_id,
#        }
#        self.__dict__['_node_values'] = {}
#        self.__dict__['_node_values'].update(values)
#    
#    def __getattr__(self, name):
#        if name.startswith('_'):
#            _name = name[1:]
#            return self.__dict__['_node_meta'][_name]
#        else:
#            return self.__dict__['values'][name]
#    
#    def __setattr__(self, name, value):
#        if name.startswith('_'):
#            _name = name[1:]
#            self.__dict__['_node_meta'][_name] = value
#        else:
#            self.__dict__['values'][name] = value
#    
#    def __delattr__(self, key):
#        if name.startswith('_'):
#            _name = name[1:]
#            del self.__dict__['_node_meta'][_name]
#        else:
#            del self.__dict__['values'][name]
#    
#    def __getitem__(self, key):
#        return self.__getattr__(key)
#    
#    def __setitem__(self, key, value):
#        return self.__setattr__(key, value)
#    
#    def __delitem__(self, key):
#        return self.__delattr__(key)
#    
#    def keys(self):
#        return map(lambda x: "_%s" % x, self.__dict__['_node_meta'].keys()) \
#            + self.__dict__['_node_values'].keys()
#    
#    def has_key(self, key):
#        return (key in self.keys())
#    
#    def update(self, values):
#        self.__dict__['_node_values'].update(values)
#    
#    @classmethod
#    def from_dict(cls, values, *args, **kwargs):
#        """**Constructor** Instantiate a new node version
#        from the passed-in values"""
#        node_version = cls(*args, **kwargs)
#        node_version.update(values)
#        return node_version
