from django.urls import re_path, path

from . import views

urlpatterns = [
    path('membership/', views.MembershipListView.as_view(), name='memberships'),
    path('membership/iva/', views.IvaListView.as_view(), name='iva-memberships'),
    path('membership/create/', views.MembershipCreateView.as_view(), name='new-membership'),
    re_path(r'^membership/create/(?P<username>[ms][0-9]{7})/$', views.UserCreateView.as_view(), name='add-membership'),
    path('membership/<int:pk>/', views.MembershipDetailView.as_view(), name='membership'),
    path('membership/<int:pk>/update/', views.MembershipUpdate.as_view(), name='edit-membership'),
    path('membership/<int:pk>/delete/', views.MembershipDelete.as_view(), name='delete-membership'),
    path('membership/<int:pk>/iva/', views.MembershipIvaView.as_view(), name='iva-membership'),
    path('membership/<int:pk>/iva/upload/', views.MembershipIvaUpdate.as_view(), name='upload-iva-membership'),
    path('membership/<int:pk>/iva/approve/', views.MembershipIvaApprove.as_view(),
        name='approve-iva-membership'),
    path('membership/<int:pk>/iva/decline/', views.MembershipIvaDecline.as_view(),
        name='decline-iva-membership'),
]
