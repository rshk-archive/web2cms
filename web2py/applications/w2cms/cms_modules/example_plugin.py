'''
Created on Nov 10, 2011
@author: samu
'''

cms_plugin_info = dict(
    name='Example Plugin', ## Plugin descriptive label
    description='Just an example plugin',
    version='0.1-alpha', ## Version of the cms_plugin
    core_version='0.1', ## Minimum required core version
    dependencies = [], ## Other cms_plugins this plugin depends on
)

from cms_extension import *

class MyExampleController(CustomController): pass
class MyExampleNode(NodeTypeManager): pass
class MyExampleBlock(DynamicBlock): pass
