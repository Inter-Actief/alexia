from django.conf.urls import url

from apps.scheduling.views import MailTemplateListView, MailTemplateDetailView, MailTemplateUpdateView, \
    AvailabilityListView, AvailabilityCreateView, AvailabilityDetailView, AvailabilityUpdateView
from . import views, perspectives

urlpatterns = [
    # Others
    url(r'^$', views.overview, name='schedule'),
    url(r'^bartender/$', perspectives.bartender, name='bartender-schedule'),
    url(r'^calendar/$', perspectives.calendar, name='calendar-schedule'),
    url(r'^calendar/fetch$', perspectives.calendar_fetch, name='fetch-calendar-schedule'),
    url(r'^configuration/edit_standardreservations/$',
        views.edit_standardreservations, name='standard-reservations'),

    # Events
    url(r'^event/add/$', views.event_add, name='new-event'),
    url(r'^event/(?P<pk>\d+)/$', views.event_show, name='event'),
    url(r'^event/(?P<pk>\d+)/edit/$', views.event_edit, name='edit-event'),
    url(r'^event/(?P<pk>\d+)/edit/bartender_availability/(?P<user_pk>\d+)/$',
        views.event_edit_bartender_availability, name='edit-event-bartender-availability'),
    url(r'^event/(?P<pk>\d+)/delete/$', views.event_delete, name='delete-event'),

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
