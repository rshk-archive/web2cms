'''
Created on Nov 1, 2011

@author: samu
'''

class w2cException(Exception): pass
class w2cSettingsException(w2cException): pass
class EntityNotFound(w2cException): pass
