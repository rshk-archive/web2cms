# -*- coding: utf-8 -*-
'''
Miscellaneous tools for the CMS.

This includes mostly CRUD / management for base elements and all the stuff
that needs quick importing from a single module.

Also, we should provide ``__all__`` to limit the amount of imported stuff.

.. WARNING:: Language is being intentionally ignored at the moment!

We need to decide exactly how to handle the language selection mechanism,
so for the moment just one language is used.

'''

## Beware that by using __all__, classes not included here gets undocumented
#__all__ = ['CmsDB', 'CMS_URL']


import gluon.dal
from gluon import *
from gluon.storage import Storage
import cms_settings

##==============================================================================
## Utility functions
##==============================================================================

def CMS_URL(entity_type, entity_id=None, action='read', args=None, vars=None):
    if entity_id is not None:
        args = [entity_id] + (args or [])
    return URL('default', '%s_%s' % (entity_type, action), args=args, vars=vars)

def descend_tree(tree, childrenattr='components', ilev=0):
    """Generator that yields all the children by exploring a tree.
    
    :param tree: The tree of objects to be explored.
        Usually a gluon.storage.Storage
    :param childrenattr: The attribute of the branches containing
        children elements.
    :param ilev: Used internally to track the indentation level
        of the current branch.
    
    :return: ``ilev, element`` for each found element.
    """
    if not isinstance(tree, list):
        tree = [tree]
    for branch in tree:
        yield (ilev, branch)
        if hasattr(branch, childrenattr):
            for elm in getattr(branch, childrenattr):
                for x in descend_tree(elm, childrenattr, ilev+1):
                    yield x

def split_query_varname(varname):
    """Split query variable name"""
    _split = varname.split('[',1)
    if len(_split) < 2:
        return [_split[0]]
    else:
        return [_split[0]] + _split[1][:-1].split('][')

def place_into(container, keys, value):
    """Recursively place stuff into ad dict"""
    if len(keys) == 1:
        container[keys[0]] = value
    else:
        if not container.has_key(keys[0]):
            container[keys[0]] = {}
        place_into(container[keys[0]], keys[1:], value)

def vars_to_tree(vars):
    """Reorganize vars from query string into a tree"""
    vars_new = {}
    for k,v in vars.items():
        ksplit = split_query_varname(k)
        place_into(vars_new, ksplit, v)
    return vars_new

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
            
            row_node_fields_base = {
                'node_version' : version_id,
                'title' : values.get('title', 'Untitled node %d' % node_id),
                'body' : values.get('body', ''),
                'body_format' : values.get('body_format', 'html-full'),
            }
            
            db.node_fields_base.insert(**row_node_fields_base)
        
        except:
            db.rollback()
        else:
            db.commit()
        
        return node_id
    
    def read(self, node_id, revision=None, language=None):
        """Load a given node object, by id.
        
        :return: A ``NodeEntity`` object containing values for the whole node.
        """
        
        return NodeEntity(self.db.node[node_id], self._cmsdb, default_language=language, default_revision=revision)
    
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
    
    ## CRUD functions ==========================================================
    
    def form_create(self, node_type=None, defaults=None):
        return self.edit_form('create', node_type=node_type, defaults=defaults)
    
    def form_update(self, node_id, revision_id=None, language=None):
        return self.edit_form('update', node_id=node_id, revision_id=revision_id, language=language)
    
    def edit_form(self, action, node_type=None, node_id=None, revision_id=None,
                  language=None, defaults=None):
        """Node manipulation form.
        
        :param action: The action to be performed on node:
            create,update,translate
        :param node_type: Only for ``create``, the type of node
            to be created
        :param node_id: Only for ``update|translate``, the id of node
            to be updated
        :param revision_id: Only for ``update|translate``, the id
            of the revision on which to work. Defaults to latest revision.
            Must be a valid revision id for this node.
        :param language: The language in which to write/translate the node.
            Defaults to current language or 'neutral'.
        :param defaults: A dict or dict-like of values to be set as
            defaults for node creation.
        """
        
        db = self.db
        T = current.T
        
        ## Validate arguments
        node_types = cms_settings.list_node_types()
        if node_type not in node_types.keys():
            raise ValueError, "Wrong node type %r must be one of %s" % (node_type, ", ".join(node_types.keys()))
        
        ## To store components of the form
        _form_components = {}
        
        ## Tables to be used to generate form.
        ## TODO: Load all the db.tables matching node_fields_* and node_<type>_fields_*
        _component_tables = ['node', 'node_revision', 'node_fields_base']
        
        ## Set defaults --------------------------------------------------------
        db.node.type.default = node_type
        db.node.type.readable = \
        db.node.type.writable = False
        
        db.node_revision.node.requires = None
        db.node_revision.node.readable = \
        db.node_revision.node.writable = False
        
        db.node_fields_base.node_revision.requires = None
        db.node_fields_base.node_revision.readable = \
        db.node_fields_base.node_revision.writable = False
        
        ##TODO: set defaults from the `defaults` variable.
        
        ## Retrieve components from tables -------------------------------------
        for table in _component_tables:
            _form_components[table] = SQLFORM.factory(db[table], buttons=[],
                formstyle='divs' if table not in ['node','node_revision'] else 'table3cols').components
            for ilev, comp in descend_tree(_form_components[table]):
                if isinstance(comp, INPUT) and comp.attributes.has_key('_name'):
                    comp.attributes['_name'] = '%s--%s' % (table, comp.attributes['_name'])
        
        ## Build the form ------------------------------------------------------
        
        ## TODO: We need a custom SQLFORM to generate this!
        
        form = FORM(
                    
            ## Fields from node_fields_base table
            DIV(*_form_components['node_fields_base'],
                _class='expanding-form'),
            
            ## Standard fields from node/node_revision
            FIELDSET(
                    LEGEND('Node'),
                    DIV(*_form_components['node']),
                    _class='collapsible start-collapsed'),
            FIELDSET(
                    LEGEND('Node revision'),
                    DIV(*_form_components['node_revision']),
                    _class='collapsible start-collapsed'),
            
            ## Other control fields
            FIELDSET(
                LEGEND('Control fields'),
                *SQLFORM.factory(DAL(None).define_table('no_table',
                    Field('create_new_revision', 'boolean', default=False),
                    Field('content_language', 'string',
                          default=cms_settings.content_default_language,
                          requires=IS_IN_SET(cms_settings.content_languages, zero=None)),
                ), buttons=[]).components,
                _class='collapsible start-collapsed'
            ),
            
            ## Submit button
            INPUT(_type='submit', _value=T('Submit')),
            
            ## Hidden fields
            hidden = {
                'action': action,
                'node_id' : node_id,
                'revision_id' : revision_id,
                'language' : language,
            },
            
        )
        
        ## Process the form ----------------------------------------------------
        if form.process().accepted:
            ## Split vars into their original groups
            _var_groups = {}
            
            for var, val in form.vars.items():
                if var.find('--') > 0:
                    group,var = var.split('--', 2)
                else:
                    group='default'
                if not _var_groups.has_key(group):
                    _var_groups[group] = {}
                _var_groups[group][var] = val
            
            ## Here, insert stuff into tables, etc.
            form.components.append(BEAUTIFY(_var_groups))
            
            if action == 'create':
                ## Create a new node
                
                try:
                    ## Create node
                    content_language = _var_groups['default']['content_language']
                    _var_groups['node']['type'] = node_type
                    node_id = db.node.insert(**_var_groups['node'])
                    
                    _var_groups['node_revision']['node'] = node_id
                    _var_groups['node_revision']['translation_base'] = content_language
                    node_revision_id = db.node_revision.insert(**_var_groups['node_revision'])
                    
                    ## Create node revision
                    _var_groups['node_fields_base']['node_revision'] = node_revision_id
                    
                    ## Insert into node_fields_base
                    if content_language:
                        ## Insert data in t9n_node_fields_base too, with new language
                        _vals = {'node_revision':node_revision_id}
                        _t9n_vals = _var_groups['node_fields_base'].copy()
                        
                        ## Create empty record in node_fields_base (language neutral)
                        node_fields_base_id = db.node_fields_base.insert(**_vals)
                        
                        ## Create translated record in t9n_node_fields_base
                        del _t9n_vals['node_revision'] 
                        _t9n_vals['record'] = node_fields_base_id
                        _t9n_vals['language'] = content_language
                        db.t9n_node_fields_base.insert(**_t9n_vals)
                    else:
                        ## Insert just in node_fields_base (language neutral)
                        _vals = _var_groups['node_fields_base'].copy()
                        db.node_fields_base.insert(**_vals)
                except Exception,e:
                    current.response.flash = "Something went wrong!"
                    db.rollback()
                    raise
                else:
                    current.session.flash = "New node was created - id %d" % node_id
                    db.commit()
                    ## Go to node page
                    from gluon.tools import redirect
                    redirect(CMS_URL('node', node_id))
        
        return form
    
    
    

class NodeEntity(ElementEntity):
    """\
    Class representing a CMS node.
    
    * Each node is a record from db.node
    * Each node have some associated revisions, as a Set inside node_revision
    * Each node revision have some associated fields, mostly inside
      node_fields_base, but in other attributes too.
    * Each node_fields_base has some translations, contained inside
      t9n_node_fields_base.
    """
    
    node_id = None
    
    default_revision = None
    default_language = None
    
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('default_language'):
            self.default_language = kwargs['default_language']
            del kwargs['default_language']
        
        if kwargs.has_key('default_revision'):
            ##TODO: Validate revision id
            self.default_revision = kwargs['default_revision']
            del kwargs['default_revision']
        
        ElementEntity.__init__(self, *args, **kwargs)
    
    @property
    def versions(self):
        return self._db_row.node_revision.select(orderby=
                ~self.db.node_revision.published |
                ~self.db.node_revision.id)
    
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
        return NodeVersion(self._db_row.node_revision.select(
            orderby= ~db.node_revision.published | ~db.node_revision.id
            ).first())
    
    def _get_first_version(self):
        db = self.db
        return self._db_row.node_version.select(
            orderby=db.node_version.revision_id |
            ~db.node_version.is_translation_base |
            db.node_version.id 
            ).first()

class NodeVersion(object):
    search_tables = ['node_fields_base']
    _row=None
    
    def __init__(self, row):
        self._row=row
    
    def __getattr__(self,name):
        if hasattr(self._row, name):
            return getattr(self._row, name)
        for t in self.search_tables:
            _values = getattr(self._row, t).select().first()
            if hasattr(_values, name):
                return getattr(_values, name)
        raise AttributeError('Attribute %r not found' % name)

#    def __getattr__(self, name):
#        ## Fields from db.node
#        if self._db_row.has_key(name):
#            return self._db_row[name]
#        
#        ## Fields from db.node_version, for the latest version
#        _lv = self._get_latest_version()
#        if _lv.has_key(name):
#            return _lv[name]
#        
#        ## Search in all the back-references
#        for k in _lv.keys():
#            ## TODO: Improve this check a bit!
#            if isinstance(_lv[k], gluon.dal.Set):
#                for r in _lv[k].select():
#                    ## All the rows have the same fields!
#                    ## So, the first one will always return
#                    if r.has_key(name):
#                        return r[name]
#        
#        ## Pass to the default
#        return ElementEntity.__getattr__(self, name)
