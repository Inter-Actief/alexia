from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^ical_gen/$', views.ical_gen),
    url(r'^edit/$', views.edit),
    url(r'^iva/$', views.iva),
    url(r'^view_iva/$', views.view_iva),
    url(r'^payments/$', views.payments),
]
