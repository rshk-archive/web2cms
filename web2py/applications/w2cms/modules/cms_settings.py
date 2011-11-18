'''
Created on Oct 30, 2011

@author: samu
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
#    class VoidClass(object):
#        def __init__(self,*a,**kw): pass
#        def __getattr__(self, name): return None
#    class T(VoidClass): pass
#    class request(VoidClass): pass
#    class response(VoidClass): pass
    pass

from cms_exceptions import w2cSettingsException

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


########## WORK IN PROGRESS BEGIN ##############################################
class CustomConfigParser(RawConfigParser):
    def getd(self,section,option,default=None):
        try:
            return self.get(section,option)
        except (NoSectionError,NoOptionError),e:
            return default
    
    def getbooleand(self,section,option,default=None):
        try:
            return self.getboolean(section,option)
        except (NoSectionError,NoOptionError),e:
            return default
        
    def getintd(self,section,option,default=None):
        try:
            return self.getint(section,option)
        except (NoSectionError,NoOptionError),e:
            return default
    
    def getfloatd(self,section,option,default=None):
        try:
            return self.getfloat(section,option)
        except (NoSectionError,NoOptionError),e:
            return default

##### WORK IN PROGRESS
class CfgManager(object):
    filename=None
    parser=None
    def __init__(self, filename=None):
        self.__dict__['filename']=filename
        self.__dict__['parser']=RawConfigParser()
        self.__dict__['parser'].read(filename)
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return CfgSectionManager(self.filename, self.parser, key)
    def __setattr__(self,key,value):
        if key in self.__dict__.keys():
            self.__dict__[key] = value
    def __delattr__(self,name,value):
        pass

##### WORK IN PROGRESS
class CfgSectionManager(object):
    parser=None
    section=None
    def __init__(self,filename,parser,section):
        self.__dict__['parser']=parser
        self.__dict__['section']=section
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        #print "=> GET %s -> %s" % (self.section,key)
        return CfgOptionManager(self.parser,self.section,key)
    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            self.__dict__[key] = value
        #print "=> SET %s -> %s = %r" % (self.section,key,value)
        #return CfgOptionManager(self.parser,section,key)
        if not self.parser.has_section(self.section):
            self.parser.add_section(self.section)
        self.parser.set(self.section,key,value)
        self.parser.write(open(self.filename,'w'))
    def __delattr__(self, key):
        #print "=> DEL %s -> %s" % (self.section,key)
        pass

##### WORK IN PROGRESS
class CfgOptionManager(object):
    parser=None
    section=None
    option=None
    def __init__(self,parser,section,option):
        self.parser=parser
        self.section=section
        self.option=option
    def value(self):
        try:
            return self.parser.get(self.section,self.option)
        except:
            return None
    def __bool__(self):
        try:
            return self.parser.getboolean(self.section,self.option)
        except:
            return None
    def __int__(self):
        try:
            return self.parser.getint(self.section,self.option)
        except:
            return None
    def __float__(self):
        try:
            return self.parser.getfloat(self.section,self.option)
        except:
            return None
    def __str__(self):
        try:
            return self.parser.get(self.section,self.option)
        except:
            return None
########## WORK IN PROGRESS END ################################################


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
