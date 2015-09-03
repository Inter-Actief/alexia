from django.conf.urls import patterns, url
from apps.scheduling.views import MailTemplateListView, MailTemplateDetailView, MailTemplateUpdateView

urlpatterns = patterns(
    'apps.scheduling',

    # Others
    url(r'^$', 'views.overview'),
    url(r'^bartender/$', 'perspectives.bartender'),
    url(r'calendar/$', 'perspectives.calendar'),
    url(r'calendar/fetch$', 'perspectives.calendar_fetch'),
    url(r'ios/$', 'perspectives.ios'),
    url(r'^configuration/edit_standardreservations/$',
        'views.edit_standardreservations'),

    # Events
    url(r'^event/add/$', 'views.event_add'),
    url(r'^event/(?P<pk>\d+)/$', 'views.event_show'),
    url(r'^event/(?P<pk>\d+)/edit/$', 'views.event_edit'),
    url(r'^event/(?P<pk>\d+)/edit/bartender_availability/(?P<user_pk>\d+)/$',
        'views.event_edit_bartender_availability'),
    url(r'^event/(?P<pk>\d+)/delete/$', 'views.event_delete'),

    # Mail templates
    url(r'^mailtemplate/$', MailTemplateListView.as_view(), name='mailtemplate_list'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/$', MailTemplateDetailView.as_view(), name='mailtemplate_detail'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/update/$', MailTemplateUpdateView.as_view(), name='mailtemplate_update'),

    # AJAT (Asynchroon Javascript en Tekst... wie gebruikt er nog in
    # hemelsnaam XML!?)
    url(r'^ajax/bartender_availability/$', 'views.set_bartender_availability'),
)
