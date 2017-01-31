from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import APIInfoView
from .v1 import api_v1_site, APIv1BrowserView, APIv1DocumentationView

urlpatterns = [
    url(r'^$', APIInfoView.as_view(), name='api'),

    url(r'^1/$', api_v1_site.dispatch, name='api_v1_mountpoint'),
    url(r'^1/browse/$', APIv1BrowserView.as_view(), name='api_v1_browse'),
    url(r'^1/doc/$', APIv1DocumentationView.as_view(), name='api_v1_doc'),
]
