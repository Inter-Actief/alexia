from django.conf.urls import url

from .v1.common import api_v1_site
from .views import APIBrowserView, APIv1DocumentationView

urlpatterns = [
    url(r'^1/browse/$', APIBrowserView.as_view(site=api_v1_site, mountpoint="api_v1_mountpoint"),
        name="jsonrpc_browser"),
    url(r'^1/doc/$', APIv1DocumentationView.as_view(site=api_v1_site, mountpoint="api_v1_mountpoint"),
        name="jsonrpc_doc"),
    url(r'^1/$', api_v1_site.dispatch, name="api_v1_mountpoint"),
]
