'''
Module defining some example blocks, to be used to test modules
functionality.
'''

from cms_extension import cms_component, DynamicBlock

cms_module_info = dict(
    name='Example Blocks',
    description='Defined some example blocks to be placed somewhere',
    version='0.1-alpha',
    core_version='0.1',
    dependencies = [],
    meta = dict(
        author='Samuele Santi <samuele@santi.co.it>',
        license='GPL',
        website='http://w2cms.com',
        ),
)

@cms_component('block')
class ExampleBlocks(DynamicBlock):
    def list_blocks(self):
        return [
            ('block-0', 'Example block #0'),
            ('block-1', 'Example block #1'),
            ('block-2', 'Example block #2'),
        ]
    
    def get_block(self, block_id):
        return dict(
            title='Block %s' % block_id,
            body='Content of block %s' % block_id)
