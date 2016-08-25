from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.profile.views',

    url(r'^$', 'index'),
    url(r'^ical_gen/$', 'ical_gen'),
    url(r'^edit/$', 'edit'),
    url(r'^iva/$', 'iva'),
    url(r'^view_iva/$', 'view_iva'),
    url(r'^expenditures/$', 'expenditures'),
    url(r'^expenditures/(?P<pk>\d+)/$', 'expenditures_event')
)
