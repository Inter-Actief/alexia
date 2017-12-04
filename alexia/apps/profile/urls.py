from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('update/', views.ProfileUpdate.as_view(), name='edit-profile'),
    path('ical/', views.GenerateIcalView.as_view(), name='ical-gen-profile'),
    path('iva/', views.IvaView.as_view(), name='view-iva-profile'),
    path('iva/update/', views.IvaUpdate.as_view(), name='iva-profile'),
    path('expenditures/', views.ExpenditureListView.as_view(), name='expenditures-profile'),
    path('expenditures/<int:pk>/', views.ExpenditureDetailView.as_view(), name='event-expenditures-profile')
]
