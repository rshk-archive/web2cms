'''
Created on Oct 30, 2011
@author: samu
'''

@auth.requires_permission('access development tools')
def status():
    """
    This controller just displays the current status of the CMS:
    - amount of created nodes (per type)
    - amount of users
    """
    
    node_types = [x.type for x in db().select(db.node.type, distinct=True)]
    nodes_per_type = {}
    for t in node_types:
        nodes_per_type[t] = db(db.node.type == t).count()
    
    return dict(
        nodes_count = db(db.node).count(),
        node_types = node_types,
        nodes_per_type = nodes_per_type,
        )

from gluon.contrib.populate import populate
from helpers import use_custom_view

@auth.requires_permission('access development tools')
@use_custom_view('generic/form')
def generate():
    """Content generation function"""
    
    ##@todo: use SQLFORM.factory to generate better form!
    
    generable_items = ['user', 'node']
    
    form = FORM(
        TABLE(TBODY(
                    
        TR(
        TD(T('Items to generate:')),
        TD(SELECT(
            *(
                [OPTION('Choose one', _value='', _style='font-style:italic;color:#888;')] +
                [OPTION(i, _value=i) for i in generable_items]),
            _name='item_type', requires=IS_IN_SET(generable_items))),
        ),
        
        
        TR(
        TD(T('Amount:')),
        TD(INPUT(_name='amount', requires=IS_INT_IN_RANGE(1,1000))),
        ),
        
        TR(
        TD(INPUT(_name='submit', _type='submit')),
        _colspan=2,
        ),
        
        ))
    )
    
    form.process()
    
    if form.accepted:
        response.flash = 'Form accepted. Will generate %(amount)d %(item_type)s(s)' % form.vars
        if form.vars.item_type == 'node':
            response.flash = 'Created %(amount)d %(item_type)ss' % form.vars
            populate(db.node, int(form.vars.amount))
    
    return dict(
        title=T('Generate'),
        form=form,
        )
