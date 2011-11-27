# -*- coding: utf-8 -*-

## Avoid warnings from eclipse
if False: from web2py_globals import *

## Automatically track changes and reload modules ------------------------------
from gluon.custom_import import track_changes
track_changes(True)

################################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
################################################################################

from cms_settings import cfg_parser
main_cfg = cfg_parser('cms-settings', force_reload=True)

if not request.env.web2py_runtime_gae:     
    db_connection_url = main_cfg.getd('database','connection_url')
    db = DAL(db_connection_url)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore') 
    ## store sessions and tickets there
    session.connect(request, response, db = db) 
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
#response.generic_patterns = ['*'] if request.is_local else []
response.generic_patterns = []

################################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
################################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key()) 
crud, service, plugins = Crud(db), Service(), PluginManager()

## @see: http://www.web2py.com/book/default/chapter/08#Authorization-and-CRUD
## "Another way to implement access control is to always use CRUD
## (as opposed to SQLFORM) to access the database and to ask CRUD to enforce
## access control on database tables and records."
## This is done by linking Auth and CRUD with the following statement: 
#crud.settings.auth = auth

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
##TODO: Read from configuration
mail=auth.settings.mailer
#mail.settings.server = 'logging' or 'smtp.gmail.com:587'
#mail.settings.sender = 'you@gmail.com'
#mail.settings.login = 'username:password'
mail.settings.server = main_cfg.getd('mail','server')
mail.settings.sender = main_cfg.getd('mail','sender')
mail.settings.login = main_cfg.getd('mail','login')

## configure auth policy
##TODO: Read from configuration
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth,filename='private/janrain.key')

################################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
################################################################################

#db.auth_user.format = lambda x: '%(first_name)s %(last_name)s' % x

import cms_settings



## Field representation functions ==============================================
def user_name_represent(value, row=None):
    """Used to represent user names"""
    if value:
        try:
            return '%(first_name)s %(last_name)s' % value
        except:
            return "FMTERROR"
    else:
        return 'unknown'


# Standard signature fields ===================================================
# This signature table is slightly different from the one defined
# by Auth inside auth.signature, so we redefine it here.
signature = db.Table(db, 'cms_signature',
    Field('created_date', 'datetime', default=request.now),
    Field('created_by', db.auth_user, default=auth.user_id),
    Field('updated_date', 'datetime', update=request.now),
    Field('updated_by', db.auth_user, update=auth.user_id))

signature.created_date.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))    
signature.updated_date.requires = IS_DATETIME(T('%Y-%m-%d %H:%M:%S'))
signature.created_by.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
signature.updated_by.requires = IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s [#%(id)d]')
signature.created_by.represent = user_name_represent
signature.updated_by.represent = user_name_represent


t9n_fields = db.Table(db, 'cms_t9n_fields',
    #Field('record','reference...'),
    Field('language','string',length=32))


## Table: node =================================================================
db.define_table(
    'node',
    Field('type', 'string', length=128, required=True),
    Field('published', 'boolean', default=True),
    Field('weight', 'integer', default=0),
    signature,
    )

##TODO: Add IS_IN_SET() validator for type!
db.node.type.requires = IS_NOT_EMPTY()
db.node.weight.requires = IS_INT_IN_RANGE(-50, 50)

## Table: node_version =========================================================
db.define_table(
    'node_revision',
    Field('node', db.node, required=True),
    Field('published', 'boolean', default=True),
    
    ## Base language for the translation
    Field('translation_base', 'string', length=32, required=True),
    
    ## Comment about the revision
    Field('log_message', 'text'),
    
    signature,
    )

db.node_revision.node.requires = IS_IN_DB(db, db.node.id, "Node %(id)d [%(type)s]")

###TODO: Improve these virtual fields management
#class Node_revision_VirtualFields:
#    def base_fields(self):
#        #print "@@@CALLED@@@ Node_version_VirtualFields.base_fields"
#        ##TODO: modify this so that this method is called only when
#        ##      the attribute is actually required!
#        ##      (Improvements to core needed?)
#        return self.node_revision.node_fields_base.select().first()
#
#db.node_revision.virtualfields.append(Node_version_VirtualFields())

## Table: node_fields_base =====================================================
db.define_table(
    'node_fields_base',
    Field('node_revision', db.node_revision, required=True),
    Field('title', 'string', length=256),
    Field('body', 'text'),
    Field('body_format', 'string', length=128),
    )

db.node_fields_base.node_revision.requires = \
    IS_IN_DB(db, db.node_revision.id, "VERSION %(id)d of node %(node)s")
db.node_fields_base.body_format.requires = IS_IN_SET(
    dict([(k,v['label']) for k,v in cms_settings.list_text_formats().items()]))

db.define_table(
    't9n_node_fields_base',
    
    ## Standard language fields
    Field('record', db.node_fields_base,
          requires=IS_IN_DB(db, db.node_fields_base.id, "node_fields_base[%(id)d]")),
    t9n_fields,
    
    ## Fields to be translated
    db.node_fields_base.title,
    db.node_fields_base.body,
    db.node_fields_base.body_format,
    )

## Table: block ================================================================
db.define_table(
    'block',
    Field('type', 'string', length=128, required=True, default='custom'),
    Field('title', 'string', length=256, required=True, requires=IS_NOT_EMPTY()),
    Field('body', 'text'),
    Field('body_format', 'string', length=128),
    Field('weight', 'integer', default=0),
    Field('region', 'string', length=128),
    )

db.block.body_format.requires = IS_IN_SET(
    dict([(k,v['label']) for k,v in cms_settings.list_text_formats().items()]))


## CMS-Specific ================================================================

from cms_auth import CMSAuth
cms_auth = CMSAuth(auth)

from cms_tools import CmsDB, CMS_URL
cmsdb = CmsDB(db=db)

from cms_tools import REGION
REGION.highlight = False
REGION.db = db

from cms_extension import ExtensionsManager
cms_extm = ExtensionsManager(db)
