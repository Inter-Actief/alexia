from django.conf.urls import url

from .views import APIBrowserView, APIv1DocumentationView
from .v1.common import api_v1_site

urlpatterns = [
    url(r'^1/browse/$', APIBrowserView.as_view(site=api_v1_site, mountpoint="api_v1_mountpoint"),
        name="api_v1_browser"),
    url(r'^1/doc/$', APIv1DocumentationView.as_view(site=api_v1_site, mountpoint="api_v1_mountpoint"),
        name="api_v1_doc"),
    url(r'^1/$', api_v1_site.dispatch, name="api_v1_mountpoint"),
]
