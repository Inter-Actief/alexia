from django.urls import path

from .v1 import APIv1BrowserView, APIv1DocumentationView, api_v1_site
from .views import APIInfoView

urlpatterns = [
    path('', APIInfoView.as_view(), name='api'),

    path('1/', api_v1_site.dispatch, name='api_v1_mountpoint'),
    path('1/browse/', APIv1BrowserView.as_view(), name='api_v1_browse'),
    path('1/doc/', APIv1DocumentationView.as_view(), name='api_v1_doc'),
]
