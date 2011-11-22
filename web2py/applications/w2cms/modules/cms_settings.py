'''
Settings management for the CMS.

We have different kind of settings:

* CMS-level settings, stored in ini files + database
* User-level settings, stored in database + session

CMS-Level settings naming::

    cms/<file>/<section>/<option>

User-Level settings naming::

    user/<name>

Or, if not the current user:

    user=<id>/<name>

**Database storage:**

settings_cms
    * **name** ``string(255)``
    * **value** ``text``

settings_user
    * **user** ``reference auth_user``
    * **name** ``string(255)``
    * **value** ``text``

'''

import os
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError

from gluon import *

## This is needed to avoid sphinx complaining when importing the module
try:
    T = current.T
    request = current.request
    response = current.response
except:
    class VoidClass(object):
        def __init__(self,*a,**kw): pass
        def __getattr__(self, name): return None
    class T(VoidClass): pass
#    class request(VoidClass): pass
#    class response(VoidClass): pass
    pass

from cms_exceptions import w2cSettingsException


## === MISC SETTINGS ===========================================================
## TODO: Remove from here
content_languages = {
    '' : T('Language neutral'),
    'en':'English',
    'it':'Italian',
    }
content_default_language = 'neutral'


class CMSSettingsManager(object):
    """Main settings manager for the CMS.
    
    This is a dict-like object to quickly manipulate settings,
    both for the CMS-level and the user-level, by accessing ``cms/...``,
    ``user/...`` or ``user=/...`` keys.
    
    .. WARNING::
        This (not yet) supports stuff like ``.keys()``, ``.items()``,
        counting, etc.
    
    CMS-Level settings are stored on the filesystem, in ini files placed
    into ``<settings-dir>/*.ini`` and in the ``settings_cms`` table.
    
    User-level settings are stored in the database (in the ``settings_user``)
    table, but may be overwritten by variables stored in
    ``session.user_settings``.
    
    .. NOTE:: Only variables stored in current user's session may be used.
    
    * CMS variables are read first from database, then from filesystem
    * CMS variables are written only in database; configuration files
      are **never** touched.
    * User variables are read first from session, then from database.
    * User variables are written by default in the database,
      (a part from the case of anonymous user). Then, we should provide
      a function to store them in the session.
    
    """
    
    db = None
    auth = None
    
    _settings_dir_rel = 'settings' # relative to request.folder/private/
    
    def __init__(self, db, auth, define_tables=True):
        self.auth=auth
        self.db=db
        if self.db and define_tables:
            self.define_tables(self.db)
    
    @property
    def settings_dir(self):
        return os.path.join(request.folder, 'private', self._settings_dir_rel or 'settings')
    
    @settings_dir.setter
    def settings_dir(self, value):
        self._settings_dir_rel = value or 'settings'
    
    def define_tables(self, db):
        db.define_table(
            'settings_cms',
            Field('name', 'string', length=255, unique=True),
            Field('value', 'text'),
            )
        _creating_settings_user = ('settings_user' not in db.tables)
        db.define_table(
            'settings_user',
            Field('user', db.auth_user, required=True),
            Field('name', 'string', length=255),
            Field('value', 'text'),
            )
        db.settings_user.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
        
        if _creating_settings_user:
            import urlparse
            dbtype = urlparse.urlparse(db._uri).scheme
            if dbtype == 'sqlite':
                db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS unique_user_name ON settings_user (user, name);')
            elif dbtype == 'mysql':
                db.executesql('CREATE UNIQUE INDEX unique_user_name ON settings_user (user, name);')
            elif dbtype == 'pgsql':
                db.executesql('CREATE UNIQUE INDEX unique_user_name ON settings_user (user, name);')
            else:
                pass # should issue a warning..?
    
    def parse_var_name(self, varname):
        parsed = dict(
            type=None,
            delta=None,
            filename=None,
            section=None,
            option=None,
            varname=None
            )
        
        parts = varname.split('/')
        if '=' in parts[0]:
            var_type,delta = parts[0].split('=',1)
            delta = int(delta)
        else:
            var_type,delta = parts[0],None
        
        if var_type == 'user':
            parsed['delta'] = delta or self.auth.user_id
        elif var_type == 'cms':
            if len(parts) == 4:
                filename,section,option=parts[1],parts[2],parts[3]
            elif len(parts) == 3:
                filename,section,option='cms-settings',parts[1],parts[2]
            elif len(parts) == 2:
                filename,section,option='cms-settings','default',parts[1]
            else:
                raise ValueError, 'Wrong variable identifier %r' % varname
            parsed['filename'] = filename
            parsed['section'] = section
            parsed['option'] = option
        else:
            raise ValueError, 'Undefined variable type %r' % var_type
        
        parsed['type'] = var_type
        parsed['varname'] = "/".join(parts[1:])
        
        return parsed
    
    def get(self, name, default=None):
        try:
            return self.get_var(name)
        except KeyError:
            return default
    
    def keys(self):
        raise NotImplementedError
    
    def items(self):
        raise NotImplementedError
    
    def __len__(self):
        raise NotImplementedError
    
    def __contains__(self):
        raise NotImplementedError
    
    def list_vars(self, var_type, delta=None):
        """List names of variables for a given type/delta"""
        if var_type == 'cms':
            pass
        elif var_type == 'user':
            pass
    
    def _get_cms_var_from_db(self, varname):
        row = self.db(self.db.settings_cms.name==varname).select().first()
        if row: return row.value
        raise KeyError, "Variable not found"
    
    def _set_cms_var_to_db(self, varname, value):
        pass
    
    def _get_cms_var_from_filesystem(self, filename, section, option):
        filename_full = os.path.join(self.settings_dir, '%s.ini' % filename)
        if not os.path.exists(filename_full):
            raise KeyError, 'Configuration file %r not found' % filename_full
        cfp = CustomConfigParser()
        cfp.read(filename_full)
        try:
            value = cfp.get(section, option)
        except (NoSectionError, NoOptionError), e:
            raise KeyError, "Variable not found"
        else:
            return value
    
    def _set_cms_var_to_filesystem(self, filename, section, option, value):
        ## This is disabled intentionally!
        raise NotImplementedError
    
    def _get_user_var_from_db(self, user_id, varname):
        row = self.db(self.db.settings_user.user==user_id)\
            (self.db.settings_user.name==varname).select().first()
        if row:
            return row.value
        else:
            raise KeyError, "Variable not found"
    
    def _set_user_var_to_db(self, user_id, varname, value):
        pass
    
    def _get_user_var_from_session(self, varname):
        pass
    
    def _set_user_var_to_session(self, varname, value):
        pass
    
    def get_var(self, name):
        """Get value of the specified variable"""
        parsed = self.parse_var_name(name)
        
        if parsed['type'] == 'cms':
            try:
                return self._get_cms_var_from_db(parsed['varname'])
            except:
                pass
            
            try:
                return self._get_cms_var_from_filesystem(
                    parsed['filename'], parsed['section'], parsed['option'])
            except:
                pass
            
            raise KeyError, "Configuration variable not found"
        
        elif parsed['type'] == 'user':
            ####################################################################
            ##### TODO : WRITE THIS
            ####################################################################
            
            ## Try in the session
            try:
                return current.session.user_settings[parsed['varname']]
            except:
                pass
            
            ## Try in database
            try:
                return self._get_user_var_from_db(parsed['user_id'], parsed['varname'])
            except:
                pass
            
            raise KeyError, "Configuration variable not found"
        
        else:
            raise ValueError, 'Wrong variable identifier %r' % name
    
    def set_var(self, name, value):
        """Set value of the specified variable"""
        parsed = self.parse_var_name(name)
        if parsed['type'] == 'cms':
            ####################################################################
            ##### TODO : WRITE THIS
            ####################################################################
            pass
        elif parsed['type'] == 'user':
            ####################################################################
            ##### TODO : WRITE THIS
            ####################################################################
            pass
        else:
            raise ValueError, 'Wrong variable identifier %r' % name
    
    def del_var(self, name):
        """Delete the specified variable"""
        parsed = self.parse_var_name(name)
        if parsed['type'] == 'cms':
            ####################################################################
            ##### TODO : WRITE THIS
            ####################################################################
            pass
        elif parsed['type'] == 'user':
            ####################################################################
            ##### TODO : WRITE THIS
            ####################################################################
            pass
        else:
            raise ValueError, 'Wrong variable identifier %r' % name
    
    def get_user_var(self, user_id, name):
        """Get user-level variable for the specified user"""
        return self.get_var('user=%d/%s' % (user_id, name))
    
    def set_user_var(self, user_id, name, value):
        """Update user-level variable for the specified user"""
        return self.set_var('user=%d/%s' % (user_id, name), value)
    
    def del_user_var(self, user_id, name):
        """Delete user-level variable for the specified user"""
        return self.del_var('user=%d/%s' % (user_id, name))
    
    def __getitem__(self,name):
        return self.get_var(name)
    
    def __setitem__(self,name,value):
        return self.set_var(name, value)
    
    def __delitem__(self,name):
        return self.del_var(name)





def list_node_types():
    return {
        'page' : {'label' : T('Page')},
        'article' : {'label' : T('Article')},
        'my_new_type' : {'label' : T('My New Type')},
    }

def list_text_formats():
    return {
    'plain_text': {'label': T('Plain text')},
    'full_html': {'label': T('Full HTML')},
    'limited_html': {'label': T('Limited HTML')},
    'markmin': {'label': T('Markmin')},
    'code': {'label': T('Code')},
    }

cfg_parsers = {}
cfg_dir = [
#    os.path.join(request.folder,'private','settings'),
    ]


class CustomConfigParser(RawConfigParser):
    """Custom configuration parser, implementing ``get*d(..., default=None)``
    methods that add direct support for returning a default value
    in case a given section/option is not found.
    """
    
    def getd(self,section,option,default=None):
        """
        :return: ``RawConfigParser.get(section, option)``
        or ``default`` if :exc:`NoSectionError` or :exc:`NoOptionError`
        is raised.
        """
        try:
            return self.get(section,option)
        except (NoSectionError,NoOptionError),e:
            return default
    
    def getbooleand(self,section,option,default=None):
        """
        :return: ``RawConfigParser.getboolean(section, option)``
        or ``default`` if :exc:`NoSectionError` or :exc:`NoOptionError`
        is raised.
        """
        try:
            return self.getboolean(section, option)
        except (NoSectionError, NoOptionError), e:
            return default
        
    def getintd(self,section,option,default=None):
        """
        :return: ``RawConfigParser.getint(section, option)``
        or ``default`` if :exc:`NoSectionError` or :exc:`NoOptionError`
        is raised.
        """
        try:
            return self.getint(section, option)
        except (NoSectionError, NoOptionError), e:
            return default
    
    def getfloatd(self,section,option,default=None):
        """
        :return: ``RawConfigParser.getfloat(section, option)``
        or ``default`` if :exc:`NoSectionError` or :exc:`NoOptionError`
        is raised.
        """
        try:
            return self.getfloat(section, option)
        except (NoSectionError, NoOptionError), e:
            return default



## @@@@@ DEPRECATED BEGIN @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def cfg_parser(cfg_file, force_reload=False):
    global cfg_parsers,cfg_dir
    
    cfg_dir = [
    os.path.join(current.request.folder,'private','settings'),
    ]
    
    if not force_reload and cfg_parsers.has_key(cfg_file):
        return cfg_parsers[cfg_file]
    
    ## Find the configuration file in the path
    _cfg_file = None
    for d in cfg_dir:
        if os.path.isfile(os.path.join(d, "%s.ini" % cfg_file)):
            _cfg_file = os.path.join(d, "%s.ini" % cfg_file)
            break
    if _cfg_file is None:
        raise w2cSettingsException("Configuration file %r not found in path." % cfg_file)
    
    cfp = CustomConfigParser()
    cfp.read(_cfg_file)
    
    cfg_parsers[cfg_file] = cfp
    
    return cfp
## @@@@@ DEPRECATED END @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


