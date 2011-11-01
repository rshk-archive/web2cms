'''
Created on Oct 30, 2011

@author: samu
'''

import os
from ConfigParser import RawConfigParser

from gluon import *
T = current.T
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
    os.path.join(current.request.folder,'private','settings'),
    ]

def get_config(cfg_file, section, option, default=None):
    """Get a configuration parameter from a configuration file"""
    
    ## Find the configuration file in the path
    _cfg_file = None
    for d in cfg_dir:
        if os.path.isfile(os.path.join(d, cfg_file)):
            _cfg_file = os.path.join(d, cfg_file)
            break
    if _cfg_file is None:
        raise w2cSettingsException("Configuration file %r not found in path." % cfg_file)
    cfp = RawConfigParser()
    cfp.read(_cfg_file)
    try:
        return cfp.get(section, option)
    except (NoSectionError, NoOptionError), e:
        return default
