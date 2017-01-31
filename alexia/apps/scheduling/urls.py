from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.event_list_view, name='event-list'),
    url(r'^bartender/$', views.EventBartenderView.as_view(), name='bartender-schedule'),
    url(r'^calendar/$', views.EventCalendarView.as_view(), name='calendar-schedule'),
    url(r'^calendar/fetch/$', views.EventCalendarFetch.as_view(), name='fetch-calendar-schedule'),
    url(r'^matrix/$', views.EventMatrixView.as_view(), name='event_matrix'),

    url(r'^event/create/$', views.EventCreateView.as_view(), name='new-event'),
    url(r'^event/(?P<pk>\d+)/$', views.EventDetailView.as_view(), name='event'),
    url(r'^event/(?P<pk>\d+)/update/$', views.EventUpdateView.as_view(), name='edit-event'),
    url(r'^event/(?P<pk>\d+)/update/bartender_availability/(?P<user_pk>\d+)/$',
        views.event_edit_bartender_availability, name='edit-event-bartender-availability'),
    url(r'^event/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='delete-event'),

    url(r'^mailtemplate/$', views.MailTemplateListView.as_view(), name='mailtemplate_list'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/$', views.MailTemplateDetailView.as_view(), name='mailtemplate_detail'),
    url(r'^mailtemplate/(?P<name>[a-z]+)/update/$', views.MailTemplateUpdateView.as_view(),
        name='mailtemplate_update'),

    url(r'^availability/$', views.AvailabilityListView.as_view(), name='availability_list'),
    url(r'^availability/create/$', views.AvailabilityCreateView.as_view(), name='availability_create'),
    url(r'^availability/(?P<pk>\d+)/update/$', views.AvailabilityUpdateView.as_view(), name='availability_update'),

    # AJAT (Asynchroon Javascript en Tekst... wie gebruikt er nog in
    # hemelsnaam XML!?)
    url(r'^ajax/bartender_availability/$', views.set_bartender_availability),
]
