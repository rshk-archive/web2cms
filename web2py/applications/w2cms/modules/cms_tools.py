'''
Miscellaneous tools for the CMS.

This includes mostly CRUD / management for base elements and all the stuff
that needs quick importing from a single module.

Also, we should provide ``__all__`` to limit the amount of imported stuff.
'''

__all__ = ['CmsDB']

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
    ## This allows working as a separate user, for example
    ## when an administrative task is required to be run by the *system*
    ## with high privileges, even if the current user will otherways
    ## unable to perform that action.
    _working_user = None
    
    ## To store CMSDB
    _cmsdb = None
    
    def __init__(self, cmsdb):
        self._cmsdb = cmsdb
    
    @property
    def db(self):
        return self._cmsdb._db
    
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
    
    ## Working user management =================================================
    def get_working_user(self):
        if self._working_user is not None:
            return self._working_user
        else:
            return current.user
    
    def set_working_user(self, working_user):
        self._working_user = working_user


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
        
        row_node = {
            'type' : values.get('type', ''),
            'weight' : values.get('weight', 0),
            'published' : values.get('published', True),
        }
        
        row_node_version = {
            'node' : None, # updated later
            'revision_id' : 1, # first revision for this node
            'language' : values.get('language', 'neutral'),
            'published' : values.get('published', True),
            'is_translation_base' : True,
        }
        
        row_node_base_fields = {
            'node_version' : None, # updated later
            'title' : values.get('title', 'Untitled node %d' % node_id),
            'body' : values.get('body', ''),
            'body_format' : values.get('body_format', 'html-full'),
        }
        
        node_id = db.node.insert(row_node)
        row_node_version['node'] = node_id
        version_id = db.node_version.insert(row_node_version)
        row_node_base_fields['node_version'] = version_id
        db.node_base_fields.insert(row_node_base_fields)
        return node_id
    
    def read(self, node_id, revision=None, language=None):
        """Load a given node object, by id.
        
        :return: A ``NodeEntity`` object containing values for the whole node.
        """
        
        node = Storage()
        
        pass
    
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
        
        #return db(query).select(db.node.ALL, orderby=orderby)
        all_nodes = []
        for row in db().select(db.node.ALL):
            #max = db.node_version.revision_id.max()
            #latest_revision = db(db.node_version.node==row.id).select(max).first()[max]
            _versions = db(db.node_version.node==row).select(db.node_version.ALL)
            row.versions = {}
            for _ver in _versions:
                if not row.versions.has_key(_ver.revision_id):
                    row.versions[_ver.revision_id] = {}
                row.versions[_ver.revision_id][_ver.language] = _ver
            all_nodes.append(row)
        return all_nodes


class NodeEntity(object):
    """\
    Class representing a CMS node.
    
    * Versions are structured in a tree, with ``revision_id``
      -> ``list`` of ``versions``.
    * We should use lazy loaders for the node entities, in order to
      minimize queries and memory usage
    * We should mark modified fields / versions in order to minimize
      queries on update, sice possibily a node may have quite a lot of
      revisions + external tables and it's not a good idea to always
      update them all!
    """
    
    node_id = None
    versions = None
    revision_numbers = None
    languages = None
    
    def __init__(self):
        pass
    
    @classmethod
    def from_db(cls, db, node_id):
        """**Constructor:** build the node entity by loading from database"""
        _node_obj = db.node[node_id]
        if not _node_obj:
            return None
        node = cls()
        node.node_id = node_id
        return node
    
    def list_versions(self):
        """List all the versions for this node."""
        pass
    
    def list_languages(self, version_id=None):
        """List all the languages for this node."""
        pass
    
    def add_version(self, revision_id, language, values):
        """Add a version to this node.
        Versions are placed in ``self.versions[revision_id][language]``.
        """
        
        self.versions[revision_id][language] = NodeVersion.from_dict(
            values,
            node_id=self.node_id,
            revision_id=revision_id,
            language=language)
        
        pass


class NodeVersion(object):
    """Class representing a CMS node version."""
    
    _node_meta = None
    _node_values = None
    
    def __init__(self, node_id, revision_id, language, version_id, values):
        self.__dict__['_node_meta'] = {
            'node_id' : node_id,
            'revision_id' : revision_id,
            'language' : language,
            'version_id' : version_id,
        }
        self.__dict__['_node_values'] = {}
        self.__dict__['_node_values'].update(values)
    
    def __getattr__(self, name):
        if name.startswith('_'):
            _name = name[1:]
            return self.__dict__['_node_meta'][_name]
        else:
            return self.__dict__['values'][name]
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            _name = name[1:]
            self.__dict__['_node_meta'][_name] = value
        else:
            self.__dict__['values'][name] = value
    
    def __delattr__(self, key):
        if name.startswith('_'):
            _name = name[1:]
            del self.__dict__['_node_meta'][_name]
        else:
            del self.__dict__['values'][name]
    
    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __delitem__(self, key):
        return self.__delattr__(key)
    
    def keys(self):
        return map(lambda x: "_%s" % x, self.__dict__['_node_meta'].keys()) \
            + self.__dict__['_node_values'].keys()
    
    def has_key(self, key):
        return (key in self.keys())
    
    def update(self, values):
        self.__dict__['_node_values'].update(values)
    
    @classmethod
    def from_dict(cls, values, *args, **kwargs):
        """**Constructor** Instantiate a new node version
        from the passed-in values"""
        node_version = cls(*args, **kwargs)
        node_version.update(values)
        return node_version
