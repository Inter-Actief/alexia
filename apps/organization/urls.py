from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^membership/$', views.membership_list, name='memberships'),
    url(r'^membership/iva/$', views.iva_list, name='iva-memberships'),
    url(r'^membership/add/$', views.membership_add, name='new-membership'),
    url(r'^membership/add/(?P<username>[ms][0-9]{7})/$', views.membership_create_user),
    url(r'^membership/(?P<pk>\d+)/show/$', views.membership_show, name='membership'),
    url(r'^membership/(?P<pk>\d+)/edit/$', views.membership_edit, name='edit-membership'),
    url(r'^membership/(?P<pk>\d+)/delete/$', views.membership_delete, name='delete-membership'),
    url(r'^membership/(?P<pk>\d+)/iva/$', views.membership_iva, name='iva-membership'),
    url(r'^membership/(?P<pk>\d+)/iva_approve/$', views.iva_approve, name='approve-iva-membership'),
    url(r'^membership/(?P<pk>\d+)/iva_decline/$', views.iva_decline, name='decline-iva-membership'),
]
