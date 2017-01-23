from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^membership/$', views.MembershipListView.as_view(), name='memberships'),
    url(r'^membership/iva/$', views.IvaListView.as_view(), name='iva-memberships'),
    url(r'^membership/create/$', views.MembershipCreateView.as_view(), name='new-membership'),
    url(r'^membership/create/(?P<username>[ms][0-9]{7})/$', views.UserCreateView.as_view(), name='add-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/$', views.MembershipDetailView.as_view(), name='membership'),
    url(r'^membership/(?P<pk>[0-9]+)/update/$', views.MembershipUpdate.as_view(), name='edit-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/delete/$', views.MembershipDelete.as_view(), name='delete-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/iva/$', views.MembershipIvaView.as_view(), name='iva-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/iva/upload/$', views.MembershipIvaUpdate.as_view(), name='upload-iva-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/iva/approve/$', views.MembershipIvaApprove.as_view(),
        name='approve-iva-membership'),
    url(r'^membership/(?P<pk>[0-9]+)/iva/decline/$', views.MembershipIvaDecline.as_view(),
        name='decline-iva-membership'),
]
