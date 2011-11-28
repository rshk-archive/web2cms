'''
Miscellaneous helper functions for web2cms.
'''

from gluon import *

def use_custom_view(viewname):
    """Decorator to be used to customize the view to be used
    to render a given controller.
    
    :param viewname: Name of the custom view to be used for the
        decorated function, without extension (will be added
        automatically from ``request.extension``)
    """
    def _use_newcontroller(func):
        def _newcontroller():
            current.response.view = '%s.%s' % (viewname, current.request.extension)
            return func()
        return _newcontroller
    return _use_newcontroller

def recursive_update(d1,d2):
    """Recursively update a dictionary or dict-like object.
    
    :param d1: Dictionary in which to merge values from d2
    :param d2: Dictionary or dict-like from which to read values
    """
    if not hasattr(d2, '__getitem__'):
        raise ValueError, "d2 is not a dict-like"
    for k in d2.keys():
        try:
            recursive_update(d1[k], d2[k])
        except:
            d1[k] = d2[k]

def confirm_form(message=None, submit_text=None, cancel_text=None, cancel_url=None):
    """Generate a standard confirmation form.
    
    :param message: The confirmation message. Defaults to 'Are you sure?'
    :param submit_text: Text of the 'Submit' button. Defaults to 'Confirm'
    :param cancel_text: Text of the 'Cancel' button. Defaults to 'Cancel'
    :param cancel_url: URL where to redirect if the user cancel action
    :return: A FORM() instance with preloaded fields.
    """
    T = current.T
    if message is None:
        message = T('Are you sure?'),
    if submit_text is None:
        submit_text = T('Confirm')
    if cancel_text is None:
        cancel_text = T('Cancel')
    return FORM(
        DIV(message, _class='message'),
        DIV(INPUT(_type='submit', _value=submit_text),
            ' ', A(cancel_text, _href=cancel_url),
            _class='buttons'),
        _class='confirm-form')

def descend_tree(tree, childrenattr='components', ilev=0):
    """Generator that yields all the children by exploring a tree.
    
    :param tree: The tree of objects to be explored.
        Usually a gluon.storage.Storage
    :param childrenattr: The attribute of the branches containing
        children elements.
    :param ilev: Used internally to track the indentation level
        of the current branch.
    
    :return: ``ilev, element`` for each found element.
    """
    if not isinstance(tree, list):
        tree = [tree]
    for branch in tree:
        yield (ilev, branch)
        if hasattr(branch, childrenattr):
            for elm in getattr(branch, childrenattr):
                for x in descend_tree(elm, childrenattr, ilev+1):
                    yield x

def split_query_varname(varname):
    """Split query variable name"""
    _split = varname.split('[',1)
    if len(_split) < 2:
        return [_split[0]]
    else:
        return [_split[0]] + _split[1][:-1].split('][')

def place_into(container, keys, value):
    """Recursively place stuff into ad dict"""
    if len(keys) == 1:
        container[keys[0]] = value
    else:
        if not container.has_key(keys[0]):
            container[keys[0]] = {}
        place_into(container[keys[0]], keys[1:], value)

def vars_to_tree(vars):
    """Reorganize vars from query string into a tree"""
    vars_new = {}
    for k,v in vars.items():
        ksplit = split_query_varname(k)
        place_into(vars_new, ksplit, v)
    return vars_new
