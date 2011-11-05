"""
Sources to be used to trigger completion
"""

from io import StringIO
import gluon
from gluon import *
import Cookie
import datetime

__all__ = ['request','response'] + gluon.__all__

class SC_Request(gluon.storage.Storage):
    def __init__(self):
        self.cookies = Cookie.SimpleCookie()
        self.env = gluon.storage.Storage()
        self.application = ''
        self.controller = ''
        self.function = ''
        self.extension = ''
        self.folder = ''
        self.now = datetime.datetime.now()
        self.utcnow = datetime.datetime.now()
        self.args = []
        self.vars = gluon.storage.Storage()
        self.get_vars = gluon.storage.Storage()
        self.post_vars = gluon.storage.Storage()
        self.client = ''
        self.is_local = False
        self.is_https = False
        self.body = file()
        self.ajax = False
        self.cid = 0
        
    def restful(self, fun): pass
    def user_agent(self): pass
    def wsgi(self): pass

class SC_Response(gluon.storage.Storage):
    def __init__(self):
        self.body = StringIO()
        self.cookies = Cookie.SimpleCookie()
        self.files = []
        self.flash = ''
        self.headers = {}
        self.menu = []
        self.meta = gluon.storage.Storage()
        self.postprocessing = []
        self.session_file = None
        self.session_file_name = ''
        self.session_id = ''
        self.session_id_name = ''
        self.status = 200
        self.subtitle = ''
        self.title = ''
        self._vars = gluon.storage.Storage()
        self.view = ''
        self.js = ''
    
    def download(self,request,db): pass
    def include_files(self): pass
    def include_meta(self): pass
    def render(self,view,vars): pass
    def stream(self,file,chunk_size,request=None): pass
    def toolbar(self): pass
    def xmlrpc(self,request,methods): pass
    def write(self,text): pass
    
    

request = SC_Request()
response = SC_Response()
session = gluon.storage.Storage()
