from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProfileView.as_view(), name='profile'),
    url(r'^ical_gen/$', views.GenerateIcalView.as_view(), name='ical-gen-profile'),
    url(r'^edit/$', views.ProfileUpdate.as_view(), name='edit-profile'),
    url(r'^iva/$', views.iva, name='iva-profile'),
    url(r'^view_iva/$', views.IvaView.as_view(), name='view-iva-profile'),
    url(r'^expenditures/$', views.ExpenditureListView.as_view(), name='expenditures-profile'),
    url(r'^expenditures/(?P<pk>\d+)/$', views.ExpenditureDetailView.as_view(), name='event-expenditures-profile')
]