from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^membership/$', views.MembershipListView.as_view(), name='memberships'),
    url(r'^membership/iva/$', views.IvaListView.as_view(), name='iva-memberships'),
    url(r'^membership/add/$', views.membership_add, name='new-membership'),
    url(r'^membership/add/(?P<username>[ms][0-9]{7})/$', views.membership_create_user, name='add-membership'),
    url(r'^membership/(?P<pk>\d+)/show/$', views.MembershipDetailView.as_view(), name='membership'),
    url(r'^membership/(?P<pk>\d+)/edit/$', views.MembershipUpdate.as_view(), name='edit-membership'),
    url(r'^membership/(?P<pk>\d+)/delete/$', views.MembershipDelete.as_view(), name='delete-membership'),
    url(r'^membership/(?P<pk>\d+)/iva/$', views.MembershipIvaView.as_view(), name='iva-membership'),
    url(r'^membership/(?P<pk>\d+)/iva_upload/$', views.iva_upload, name='upload-iva-membership'),
    url(r'^membership/(?P<pk>\d+)/iva_approve/$', views.iva_approve, name='approve-iva-membership'),
    url(r'^membership/(?P<pk>\d+)/iva_decline/$', views.iva_decline, name='decline-iva-membership'),
]
