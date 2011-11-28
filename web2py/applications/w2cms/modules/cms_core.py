'''
Core classes for the CMS management.
'''

class CmsCore:
    db=None
    auth=None
    request=None
    response=None
    session=None
    
    cms_db = None
    cms_auth = None
    extm = None
    theme_mgr = None
    
    def __init__(self, db, auth, request, response, session):
        self.db = db
        self.auth = auth
        self.request = request
        self.session = session
        
        ## Initialize other stuff
        from cms_auth import CMSAuth
        self.cms_auth = CMSAuth(self.auth)
        
        from cms_tools import CmsDB, CMS_URL
        self.cms_db = CmsDB(cms=self)
        
        from cms_tools import REGION
        REGION.highlight = False
        REGION.db = db
        
        from cms_extension import ExtensionsManager
        self.ext_mgr = ExtensionsManager(self.db)
        
        from cms_views import CmsThemeManager
        self.theme_mgr = CmsThemeManager(self)

