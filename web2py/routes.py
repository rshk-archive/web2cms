#!/usr/bin/python
# -*- coding: utf-8 -*-

# default_application, default_controller, default_function
# are used when the respective element is missing from the
# (possibly rewritten) incoming URL
#
default_application = 'w2cms'    # ordinarily set in base routes.py
default_controller = 'default'  # ordinarily set in app-specific routes.py
default_function = 'index'      # ordinarily set in app-specific routes.py

## Experimental router for w2cms
#routers = dict(
#    BASE = dict(
#        default_application = 'w2cms',
#        w2cms = dict(languages=['en', 'it', 'jp'], default_language='en'),                                                                                                                            #    ),
#)

# routes_app is a tuple of tuples.  The first item in each is a regexp that will
# be used to match the incoming request URL. The second item in the tuple is
# an applicationname.  This mechanism allows you to specify the use of an
# app-specific routes.py. This entry is meaningful only in the base routes.py.
#
# Example: support welcome, admin, app and myapp, with myapp the default:


#routes_app = ((r'/(?P<app>welcome|admin|app)\b.*', r'\g<app>'),
#              (r'(.*)', r'myapp'),
#              (r'/?(.*)', r'myapp'))

# routes_in is a tuple of tuples.  The first item in each is a regexp that will
# be used to match the incoming request URL. The second item in the tuple is
# what it will be replaced with.  This mechanism allows you to redirect incoming
# routes to different web2py locations
#
# Example: If you wish for your entire website to use init's static directory:
#
#   routes_in=( (r'/static/(?P<file>[\w./-]+)', r'/init/static/\g<file>') )
#

routes_in = ((r'.*:/favicon.ico', r'/w2cms/static/favicon.ico'),
             (r'.*:/robots.txt', r'/w2cms/static/robots.txt'))

# routes_out, like routes_in translates URL paths created with the web2py URL()
# function in the same manner that route_in translates inbound URL paths.
#

#routes_out = ((r'.*http://otherdomain.com.* /app/ctr(?P<any>.*)', r'\g<any>'),
#              (r'/app(?P<any>.*)', r'\g<any>'))

# Error-handling redirects all HTTP errors (status codes >= 400) to a specified
# path.  If you wish to use error-handling redirects, uncomment the tuple
# below.  You can customize responses by adding a tuple entry with the first
# value in 'appName/HTTPstatusCode' format. ( Only HTTP codes >= 400 are
# routed. ) and the value as a path to redirect the user to.  You may also use
# '*' as a wildcard.
#
# The error handling page is also passed the error code and ticket as
# variables.  Traceback information will be stored in the ticket.
#
# routes_onerror = [
#     (r'init/400', r'/init/default/login')
#    ,(r'init/*', r'/init/static/fail.html')
#    ,(r'*/404', r'/init/static/cantfind.html')
#    ,(r'*/*', r'/init/error/index')
# ]

# specify action in charge of error handling
#
# error_handler = dict(application='error',
#                      controller='default',
#                      function='index')

# In the event that the error-handling page itself returns an error, web2py will
# fall back to its old static responses.  You can customize them here.
# ErrorMessageTicket takes a string format dictionary containing (only) the
# "ticket" key.

# error_message = '<html><body><h1>%s</h1></body></html>'
# error_message_ticket = '<html><body><h1>Internal error</h1>Ticket issued: <a href="/admin/default/ticket/%(ticket)s" target="_blank">%(ticket)s</a></body></html>'

# specify a list of apps that bypass args-checking and use request.raw_args
#
#routes_apps_raw=['myapp']
#routes_apps_raw=['myapp', 'myotherapp']

