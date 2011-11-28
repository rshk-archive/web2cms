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
from UserDict import DictMixin


##==============================================================================
## Utility functions
## TODO: Move to helpers
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
    _auth = None
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

class ElementEntity(object, DictMixin):
    
    _db_row = None
    _cmsdb = None
    
    def __init__(self, db_row=None, cmsdb=None):
        self._db_row = db_row
        self._cmsdb = cmsdb
    
    @property
    def db(self):
        return self._cmsdb._db
    
    @property
    def row(self):
        return self._db_row
    
    def __getitem__(self, key):
        ## Try to return items from the associated db row
        if self._db_row.has_key(key):
            return self._db_row[key]
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
        raise NotImplementedError
        
    def read(self, node_id, revision=None, language=None):
        """Load a given node object, by id.
        
        :return: A ``NodeEntity`` object containing values for the whole node.
        """
        
        return NodeEntity(
            db_row=self.db.node[node_id],
            cmsdb=self._cmsdb,
            default_language=language,
            default_revision=revision)
    
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
            NodeEntity(db_row=row, cmsdb=self._cmsdb)
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
            one of ``create|update|translate``
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
        
        if not defaults:
            defaults = {}
        
        ## Validate arguments
        node_types = cms_settings.list_node_types()
        
        if action=='create':
            ## We need only a valid node type
            if node_type not in node_types.keys():
                raise ValueError, "Wrong node type %r must be one of %s" % (node_type, ", ".join(node_types.keys()))
        elif action=='update':
            ## node_id must be a valid node
            ## if specified, revision_id must be a valid revision for this node
            ## if specified, language must exist
            node = self.read(node_id=node_id, revision=revision_id, language=language)
            #revision_id = node.get_revision(revision_id, language)
            defaults.update(node.values)
        elif action=='translate':
            ## We need a language in which to translate plus a language
            ## to be used as "translation base" to read values from.
            pass
        
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
            
            ## Prepare default values for fields
            if defaults.has_key(table):
                for field in db[table].fields:
                    try:
                        db[table][field].default = defaults[table][field]
                    except KeyError, e:
                        pass
            
            ## Create SQLFORM from the table
            _form_components[table] = SQLFORM.factory(db[table], buttons=[],
                formstyle='divs' if table not in ['node','node_revision'] else 'table3cols').components
            
            ## Change field names by adding ``<tablename>--`` prefix
            for ilev, comp in descend_tree(_form_components[table]):
                if isinstance(comp, INPUT) and comp.attributes.has_key('_name'):
                    ## Change field name
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
                    ## Error while trying to create node.
                    ## Rollback and display error message
                    ## -> we should present prefilled form to the user!
                    current.response.flash = "Something went wrong!"
                    db.rollback()
                    raise
                else:
                    current.session.flash = "New node was created - id %d" % node_id
                    db.commit()
                    ## Go to node page
                    from gluon.tools import redirect
                    redirect(CMS_URL('node', node_id))
            
            elif action == 'update':
                ## * Ensure the node exists
                ## * Ensure the node revision exists
                ## * Ensure there already is a version for that language!
                ##   -> this may be tricky.. shoud we handle this or just
                ##      add the new translation for the specified language?
                ##   In the latter case, we don't need the 'translate' action
                ##   anymore..
                ## * If the create_new_revision checkbox is checked,
                ##   we should create a new revision.
                
                if _var_groups['default']['create_new_revision']:
                    ## Create a new revision
                    pass
                
                else:
                    ## Just update
                    
                    ## Update the selected node
                    ## Update the node revision record
                    ## Update the extra fields for the selected node
                    
                    pass
                
                pass
            
            elif action == 'translate':
                pass
            
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
    
    node.values, as well as the dict-like interface, returns values for
    the selected version / language, grouped by table name.
    
    We then need a quick way to access fields by name, by looking for
    their values in all the tables. Of course, there might be problems
    in case of duplicate field names, but it would be a lot quicker
    to reference to node title as ``node.title`` instead
    of ``node['node_fields_base']['title']``.
    """
    
    _default_revision = None
    _default_language = None
    
    def __init__(self, default_language=None, default_revision=None, **kwargs):
        ElementEntity.__init__(self, **kwargs)
        
        if default_language is not None:
            self.default_language = default_language
        else:
            self.default_language = 'en'
        
        if default_revision is not None:
            self.default_revision = default_revision
        
        #ElementEntity.__init__(self, *args, **kwargs)
    
    @property
    def node_id(self):
        return self._db_row.id
    
    @property
    def versions(self):
        return self._db_row.node_revision.select(orderby=
                ~self.db.node_revision.published |
                ~self.db.node_revision.id)
    
    @property
    def default_revision(self):
        if self._default_revision:
            ## Return the selected default revision id
            return self._default_revision
        else:
            ## Return the default revision id (latest published)
            return self._db_row.node_revision.select(
                self.db.node_revision.id,
                orderby=~self.db.node_revision.published |
                ~self.db.node_revision.id).first().id
    
    @default_revision.setter
    def default_revision(self, value):
        ##--------------------------------------------------
        ## TODO: Validate that select revision must belong
        ##       to this node!
        ##--------------------------------------------------
        db = self.db
        if db(db.node_revision.node == self.node_id)(db.node_revision.id == value).count():
            self._default_revision = value
        else:
            raise ValueError, "The specified revision is not a valid revision for this node"
    
    @property
    def default_language(self):
        return self._default_language
    
    @default_language.setter
    def default_language(self, value):
        self._default_language = value
    
    def keys(self):
        return self.list_tables()
    
    def __getitem__(self, name):
        if name in self.list_tables():
            ## Look in table names
            if name == 'node':
                return self._db_row.as_dict()
            else:
                return self.get_revision(self.default_revision).get_values()[name]
        
        else:
            ## Look in field names
            try:
                return self._db_row[name]
            except: pass
            
            for table in self.list_tables():
                try:
                    self.get_revision(self.default_revision).get_values()[table][name]
                except: pass
        
        ## Nothing found!
        raise KeyError, str(name)
    
    def __setitem__(self, name, value):
        ## How to handle this? In no way ATM
        raise NotImplementedError
    
    def __delitem__(self, name):
        raise NotImplementedError
    
    def list_tables(self):
        """Return a list of tables this node came from"""
        return sorted(['node', 'node_revision'] + NodeVersion.search_tables)
    
    @property
    def latest_revision(self):
        """:returns: The id of the latest revision for this node"""
        return self._get_latest_revision()

    @property
    def values(self):
        #return self.get_values()
        return self.get_revision()
    
    def get_values(self):
        """Return values for the selected revision"""
        _values = {}
        _values['node'] = dict(self._db_row.as_dict())
        _values.update(self.get_revision(self.default_revision).get_values())
        return _values

    @property
    def translations(self):
        db = self.db
        revisions_for_node = db(db.node_revision.node == self.node_id)._select(db.node_revision.id)
        records_in_basefields = db(db.node_fields_base.node_revision.belongs(revisions_for_node))._select(db.node_fields_base.id)
        languages = db(db.t9n_node_fields_base.record.belongs(records_in_basefields)).select(db.t9n_node_fields_base.language, distinct=True, orderby=db.t9n_node_fields_base.language)
        return [row.language for row in languages]
    
    @property
    def revision_numbers(self):
        """:returns: A list of revision ids associated with this node"""
        return sorted([
            row.id
            for row in self.revisions\
                .select(self.db.node_revision.id, distinct=True)
            ])
    
    @property
    def revisions(self):
        """:returns: a ``Set`` of records from node_revision"""
        return self.db(self.db.node_revision.node == self.node_id)
    
    def _get_latest_revision(self):
        """Returns the latest version for this node, looking for:
        
        * Published version
        * Highest revision number
        * Current language
        * Default site language
        * Translation base
        
        * If a published version exist, it should be preferred over
          non-published versions, even if more recent.
        """
        return self.get_revision(None, self.default_language)
    
    def get_revision(self, revision_id=None, language=None):
        """Returns a specific revision for the node"""
        db = self.db
        if not language:
            language = self.default_language
        if not revision_id:
            revision_id = self.default_revision
        if revision_id is None:
            ## Return latest revision
            results = self._db_row.node_revision.select(
                orderby=(~db.node_revision.published | ~db.node_revision.id)
                ).first()
        else:
            ## Return specified revision
            results = self.db\
                (db.node_revision.node == self.node_id)\
                (db.node_revision.id == revision_id)\
                .select().first()
        return NodeVersion(self._cmsdb, results, language=language)
    

class NodeVersion(object, DictMixin):
    search_tables = ['node_fields_base']
    _row=None
    _language=None
    _cmsdb=None
    
    def __init__(self, cmsdb, row, language=None):
        self._cmsdb=cmsdb
        self._row=row
        ##TODO: Read default language from configuration
        self._language = language or 'en'
    
    @property
    def db(self):
        return self._cmsdb._db
    
    def get_values(self, language=None):
        if language is None:
            language=self._language
        
        db = self.db
        values = {}
        
        values['node_revision'] = self._row.as_dict()
        
        for t in self.search_tables:
            #_values = getattr(self._row, t).select().first()
            _values = self._row[t].select().first()
            values[t] = _values.as_dict()
                
            ## Translate fields
            if _values.has_key('t9n_%s' % t) and language:
                _table_t = db['t9n_%s' % t]
                _row_t = db(_table_t.id.belongs(_values['t9n_%s' % t]._select(_table_t.id)))\
                    (_table_t.language==self._language).select().first()
                if _row_t:
                    _values_t = _row_t.as_dict()
                    for key,val in _values_t.items():
                        if val is not None:
                            values[t][key] = val
        
        return values
    
    @property
    def values(self):
        return self.get_values(self._language)
    
    def __getitem__(self, name):
        if name == 'node':
            ## TODO: Test this
            return self.db(self.db.node.id == self._row.node).select().first().as_dict()
        elif name == 'node_revision':
            return self._row.as_dict()
        else:
            _all_values = self.get_values()
            if _all_values.has_key(name):
                return _all_values[name]
            else:
                for k,v in _all_values.items():
                    try:
                        return _all_values[k][name]
                    except KeyError:
                        pass
        raise KeyError, name
    
    def keys(self):
        return ['node', 'node_revision'] + self.search_tables


##==============================================================================
## Regions / blocks management
##==============================================================================

class BlocksManager(ElementManager):
    """Blocks management class
    """
    
    def define_tables(self):
        db = self.db
        pass
    
    def list_blocks(self):
        db = self.db
        all_blocks = db().select(db.block.ALL)

class REGION(DIV):
    """TODO: Use LOAD() to load region content!
    """
    
    db = None
    name = None
    content = None
    highlight = False
    
    def __init__(self, name, load=False):
        self.name = name
        if load:
            self.content = self.get_content()
        else:
            self.content = None
    
    def xml(self):
        if self.content is None:
            self.content = self.get_content()
        
        _id="region-%s" % self.name
        _classes = ['region-container']
        if self.highlight:
            _classes.append('highlight')
        if not self.content and not self.highlight:
            _classes.append('empty')
        
        if self.highlight:
            _content = [DIV(self.name.replace('_',' ').title(), _class="region-placeholder"), DIV(self.content)]
        else:
            _content = DIV(self.content)
        
        return DIV(*_content, _id=_id, _class=" ".join(_classes)).xml()
    
    def __str__(self):
        return self.xml()

    def get_content(self):
        """Get the content for a given region / page.
        
        :param region_name: An identifier of the region, such as 'left_sidebar' or
            'my_example_region'
        :param request_context: The ``request`` object. Defaults to current.request
        """
        
        db = self.db
        
        blocks = db(db.block.region==self.name).select(db.block.ALL, orderby=db.block.weight)
    
        if blocks:
            return XML("\n".join([
                current.response.render('generic/block.html', dict(block=block))
                for block in blocks
            ]))
    
        return ''
