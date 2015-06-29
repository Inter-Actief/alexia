from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.organization.views',

    url(r'^membership/$', 'membership_list'),
    url(r'^membership/iva/$', 'iva_list'),
    url(r'^membership/add/$', 'membership_add'),
    url(r'^membership/add/(?P<username>[ms][0-9]{7})/$', 'membership_create_user'),
    url(r'^membership/(?P<pk>\d+)/show/$', 'membership_show'),
    url(r'^membership/(?P<pk>\d+)/edit/$', 'membership_edit'),
    url(r'^membership/(?P<pk>\d+)/delete/$', 'membership_delete'),

    url(r'^membership/(?P<pk>\d+)/iva/$', 'membership_iva'),
    url(r'^membership/(?P<pk>\d+)/iva_approve/$', 'iva_approve'),
    url(r'^membership/(?P<pk>\d+)/iva_decline/$', 'iva_decline'),
)
