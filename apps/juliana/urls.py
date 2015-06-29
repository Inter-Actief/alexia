from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.juliana.views',

    url(r'^(?P<pk>\d+)/$', 'juliana'),
)
