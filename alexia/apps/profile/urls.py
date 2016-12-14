from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='profile'),
    url(r'^ical_gen/$', views.ical_gen, name='ical-gen-profile'),
    url(r'^edit/$', views.edit, name='edit-profile'),
    url(r'^iva/$', views.iva, name='iva-profile'),
    url(r'^view_iva/$', views.view_iva, name='view-iva-profile'),
    url(r'^expenditures/$', views.expenditures, name='expenditures-profile'),
    url(r'^expenditures/(?P<pk>\d+)/$', views.expenditures_event, name='event-expenditures-profile')
]
