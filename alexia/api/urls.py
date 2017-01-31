from django.conf.urls import url

from .v1 import APIv1BrowserView, APIv1DocumentationView, api_v1_site
from .views import APIInfoView

urlpatterns = [
    url(r'^$', APIInfoView.as_view(), name='api'),

    url(r'^1/$', api_v1_site.dispatch, name='api_v1_mountpoint'),
    url(r'^1/browse/$', APIv1BrowserView.as_view(), name='api_v1_browse'),
    url(r'^1/doc/$', APIv1DocumentationView.as_view(), name='api_v1_doc'),
]
