from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ConsumptionProductListView.as_view(), name='consumptionproduct_list'),
    path('products/new/', views.ConsumptionProductCreateView.as_view(), name='consumptionproduct_create'),
    path('products/new/weight/', views.WeightConsumptionProductCreateView.as_view(),
        name='weightconsumptionproduct_create'),
    path('products/<int:pk>/edit/', views.ConsumptionProductUpdateView.as_view(),
        name='consumptionproduct_update'),
    path('products/<int:pk>/edit/weight/', views.WeightConsumptionProductUpdateView.as_view(),
        name='weightconsumptionproduct_update'),

    path('forms/', views.ConsumptionFormListView.as_view(), name='consumptionform_list'),
    path('forms/export/', views.ConsumptionFormExportView.as_view(), name='consumptionform_export'),
    path('forms/<int:pk>/', views.ConsumptionFormDetailView.as_view(), name='consumptionform_detail'),
    path('forms/<int:pk>/pdf/', views.ConsumptionFormPDFView.as_view(), name='consumptionform_pdf'),
]
