'''
Created on Oct 30, 2011
@author: samu
'''

from gluon import current, URL

def use_custom_view(viewname):
    """Decorator to be used to customize the view to be used
    to render a given controller.
    """
    def _use_newcontroller(func):
        def _newcontroller():
            current.response.view = '%s.%s' % (viewname, current.request.extension)
            return func()
        return _newcontroller
    return _use_newcontroller
