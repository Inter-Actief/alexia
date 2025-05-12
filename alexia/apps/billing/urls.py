from django.urls import re_path, path

from . import views

urlpatterns = [
    path('order/', views.OrderListView.as_view(), name='orders'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='event-orders'),
    path('order/writeoff/<int:pk>/', views.WriteOffExportView.as_view(), name='writeoff_export'),
    path('writeoff/<int:pk>/', views.WriteOffDetailView.as_view(), name='writeoff-order'),
    path('order/export/', views.OrderExportView.as_view(), name='export-orders'),
    re_path(r'^stats/(?P<year>[0-9]{4})/$', views.OrderYearView.as_view(), name='year-orders'),
    re_path(r'^stats/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.OrderMonthView.as_view(), name='month-orders'),
    path('payment/<int:pk>/', views.PaymentDetailView.as_view(), name='order'),

    path('pricegroup/', views.PriceGroupListView.as_view(), name='pricegroup_list'),
    path('pricegroup/create/', views.PriceGroupCreateView.as_view(), name='pricegroup_create'),
    path('pricegroup/<int:pk>/', views.PriceGroupDetailView.as_view(), name='pricegroup_detail'),
    path('pricegroup/<int:pk>/update/', views.PriceGroupUpdateView.as_view(), name='pricegroup_update'),
    path('pricegroup/<int:pk>/delete/', views.PriceGroupDeleteView.as_view(), name='pricegroup_delete'),

    path('productgroup/', views.ProductGroupListView.as_view(), name='productgroup_list'),
    path('productgroup/create/', views.ProductGroupCreateView.as_view(), name='productgroup_create'),
    path('productgroup/<int:pk>/', views.ProductGroupDetailView.as_view(), name='productgroup_detail'),
    path('productgroup/<int:pk>/update/', views.ProductGroupUpdateView.as_view(), name='productgroup_update'),
    path('productgroup/<int:pk>/delete/', views.ProductGroupDeleteView.as_view(), name='productgroup_delete'),

    path('product/<int:pk>/', views.ProductRedirectView.as_view(), name='product_detail'),

    path('product/permanent/', views.ProductListView.as_view(), name='product_list'),
    path('product/permanent/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/permanent/create/productgroup/<int:productgroup_pk>/',
        views.ProductCreateView.as_view(), name='product_create'),
    path('product/permanent/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/permanent/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/permanent/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    path('product/temporary/create/event/<int:event_pk>/', views.TemporaryProductCreateView.as_view(),
        name='temporaryproduct_create'),
    path('product/temporary/<int:pk>/update/', views.TemporaryProductUpdateView.as_view(),
        name='temporaryproduct_update'),
    path('product/temporary/<int:pk>/delete/', views.TemporaryProductDeleteView.as_view(),
        name='temporaryproduct_delete'),

    path('sellingprice/', views.SellingPriceListView.as_view(), name='sellingprice_list'),
    path('sellingprice/create/pricegroup/<int:pricegroup_pk>/', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    path('sellingprice/create/productgroup/<int:productgroup_pk>/', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    path('sellingprice/create/pricegroup/<int:pricegroup_pk>/productgroup/<int:productgroup_pk>/',
        views.SellingPriceCreateView.as_view(), name='sellingprice_create'),
    path('sellingprice/<int:pk>/update/', views.SellingPriceUpdateView.as_view(), name='sellingprice_update'),
    path('sellingprice/<int:pk>/delete/', views.SellingPriceDeleteView.as_view(), name='sellingprice_delete'),
]
