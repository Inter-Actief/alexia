from django.conf.urls import url
from . import views, perspectives

from apps.scheduling.views import MailTemplateListView, MailTemplateDetailView, MailTemplateUpdateView, \
    AvailabilityListView, AvailabilityCreateView, AvailabilityDetailView, AvailabilityUpdateView

urlpatterns = [
    # Others
    url(r'^$', views.overview),
    url(r'^bartender/$', perspectives.bartender),
    url(r'calendar/$', perspectives.calendar),
    url(r'calendar/fetch$', perspectives.calendar_fetch),
    url(r'ios/$', perspectives.ios),
    url(r'^configuration/edit_standardreservations/$',
        views.edit_standardreservations),

    # Events
    url(r'^event/add/$', views.event_add),
    url(r'^event/(?P<pk>\d+)/$', views.event_show),
    url(r'^event/(?P<pk>\d+)/edit/$', views.event_edit),
    url(r'^event/(?P<pk>\d+)/edit/bartender_availability/(?P<user_pk>\d+)/$',
        views.event_edit_bartender_availability),
    url(r'^event/(?P<pk>\d+)/delete/$', views.event_delete),

    # Mail templates
    url(r'^mailtemplate/$', MailTemplateListView.as_view(), name='mailtemplate_list'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/$', MailTemplateDetailView.as_view(), name='mailtemplate_detail'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/update/$', MailTemplateUpdateView.as_view(), name='mailtemplate_update'),

    # Availabilities
    url(r'^availability/$', AvailabilityListView.as_view(), name='availability_list'),
    url(r'^availability/create/$', AvailabilityCreateView.as_view(), name='availability_create'),
    url(r'^availability/(?P<pk>\d+)/$', AvailabilityDetailView.as_view(), name='availability_detail'),
    url(r'^availability/(?P<pk>\d+)/update/$', AvailabilityUpdateView.as_view(), name='availability_update'),

    # AJAT (Asynchroon Javascript en Tekst... wie gebruikt er nog in
    # hemelsnaam XML!?)
    url(r'^ajax/bartender_availability/$', views.set_bartender_availability),
]
