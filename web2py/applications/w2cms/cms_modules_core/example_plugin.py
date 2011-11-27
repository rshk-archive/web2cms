'''
Created on Nov 10, 2011
@author: samu
'''

cms_module_info = dict(
    name='Example Plugin', ## Plugin descriptive label
    description='Just an example plugin',
    version='0.1-alpha', ## Version of the cms_plugin
    core_version='0.1', ## Minimum required core version
    dependencies = [], ## Other cms_plugins this plugin depends on
    ## Module metadata
    meta = dict(
        author='Samuele Santi <samuele@santi.co.it>',
        license='GPL',
        website='http://w2cms.com',
        ),
)

from cms_extension import *
#from cms_extension import cms_component

@cms_component('controller')
class MyExampleController(CustomController): pass

@cms_component('node_type')
class MyExampleNode(NodeTypeManager): pass

@cms_component('block')
class MyExampleBlock(DynamicBlock): pass
