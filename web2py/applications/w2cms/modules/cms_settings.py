'''
Created on Oct 30, 2011

@author: samu
'''

from gluon import *
T = current.T

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
