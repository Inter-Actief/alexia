from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProfileView.as_view(), name='profile'),
    url(r'^update/$', views.ProfileUpdate.as_view(), name='edit-profile'),
    url(r'^ical/$', views.GenerateIcalView.as_view(), name='ical-gen-profile'),
    url(r'^iva/$', views.IvaView.as_view(), name='view-iva-profile'),
    url(r'^iva/update/$', views.IvaUpdate.as_view(), name='iva-profile'),
    url(r'^expenditures/$', views.ExpenditureListView.as_view(), name='expenditures-profile'),
    url(r'^expenditures/(?P<pk>\d+)/$', views.ExpenditureDetailView.as_view(), name='event-expenditures-profile')
]
