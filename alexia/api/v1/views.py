from ..views import APIBrowserView, APIDocumentationView
from .config import api_v1_site


class APIv1BrowserView(APIBrowserView):
    site = api_v1_site
    mountpoint = 'api_v1_mountpoint'
    template_name = 'api/v1/browse.html'


class APIv1DocumentationView(APIDocumentationView):
    site = api_v1_site
    mountpoint = 'api_v1_mountpoint'
    template_name = 'api/v1/doc.html'
    methods = ['authorization.add', 'authorization.end', 'authorization.list', 'login', 'logout', 'order.get',
               'order.marksynchronized', 'order.unsynchronized', 'organization.current.get',
               'organization.current.set', 'rfid.add', 'rfid.list', 'rfid.remove', 'user.add',
               'user.exists', 'user.get']
