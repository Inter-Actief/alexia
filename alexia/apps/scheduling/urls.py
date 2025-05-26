from django.urls import re_path, path

from . import views

urlpatterns = [
    path('', views.event_list_view, name='event-list'),
    path('bartender/', views.EventBartenderView.as_view(), name='bartender-schedule'),
    path('calendar/', views.EventCalendarView.as_view(), name='calendar-schedule'),
    path('calendar/fetch/', views.EventCalendarFetch.as_view(), name='fetch-calendar-schedule'),
    path('matrix/', views.EventMatrixView.as_view(), name='event_matrix'),

    path('event/create/', views.EventCreateView.as_view(), name='new-event'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='edit-event'),
    path('event/<int:pk>/update/bartender_availability/<int:user_pk>/',
        views.event_edit_bartender_availability, name='edit-event-bartender-availability'),
    path('event/<int:pk>/delete/', views.EventDelete.as_view(), name='delete-event'),

    path('mailtemplate/', views.MailTemplateListView.as_view(), name='mailtemplate_list'),
    re_path(r'^mailtemplate/(?P<name>[a-z]+)/$', views.MailTemplateDetailView.as_view(), name='mailtemplate_detail'),
    re_path(r'^mailtemplate/(?P<name>[a-z]+)/update/$', views.MailTemplateUpdateView.as_view(),
        name='mailtemplate_update'),

    path('availability/', views.AvailabilityListView.as_view(), name='availability_list'),
    path('availability/create/', views.AvailabilityCreateView.as_view(), name='availability_create'),
    path('availability/<int:pk>/update/', views.AvailabilityUpdateView.as_view(), name='availability_update'),

    # AJAT (Asynchroon Javascript en Tekst... wie gebruikt er nog in hemelsnaam XML!?)
    path('ajax/bartender_availability/', views.set_bartender_availability),
    path('ajax/bartender_availability/comment/', views.set_bartender_availability_comment),
]
