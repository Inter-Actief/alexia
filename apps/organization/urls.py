from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^membership/$', views.membership_list),
    url(r'^membership/iva/$', views.iva_list),
    url(r'^membership/add/$', views.membership_add),
    url(r'^membership/add/(?P<username>[ms][0-9]{7})/$', views.membership_create_user),
    url(r'^membership/(?P<pk>\d+)/show/$', views.membership_show),
    url(r'^membership/(?P<pk>\d+)/edit/$', views.membership_edit),
    url(r'^membership/(?P<pk>\d+)/delete/$', views.membership_delete),

    url(r'^membership/(?P<pk>\d+)/iva/$', views.membership_iva),
    url(r'^membership/(?P<pk>\d+)/iva_approve/$', views.iva_approve),
    url(r'^membership/(?P<pk>\d+)/iva_decline/$', views.iva_decline),
]
