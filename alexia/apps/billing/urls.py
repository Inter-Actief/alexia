from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^order/$', views.OrderListView.as_view(), name='orders'),
    url(r'^order/(?P<pk>[0-9]+)/$', views.OrderDetailView.as_view(), name='event-orders'),
    url(r'^order/writeoff/(?P<pk>[0-9]+)/$', views.WriteOffExportView.as_view(), name='writeoff_export'),
    url(r'^writeoff/(?P<pk>[0-9]+)/$', views.WriteOffDetailView.as_view(), name='writeoff-order'),
    url(r'^order/export/$', views.OrderExportView.as_view(), name='export-orders'),
    url(r'^stats/(?P<year>[0-9]{4})/$', views.OrderYearView.as_view(), name='year-orders'),
    url(r'^stats/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.OrderMonthView.as_view(), name='month-orders'),
    url(r'^payment/(?P<pk>[0-9]+)/$', views.PaymentDetailView.as_view(), name='order'),

    url(r'^pricegroup/$', views.PriceGroupListView.as_view(), name='pricegroup_list'),
    url(r'^pricegroup/create/$', views.PriceGroupCreateView.as_view(), name='pricegroup_create'),
    url(r'^pricegroup/(?P<pk>[0-9]+)/$', views.PriceGroupDetailView.as_view(), name='pricegroup_detail'),
    url(r'^pricegroup/(?P<pk>[0-9]+)/update/$', views.PriceGroupUpdateView.as_view(), name='pricegroup_update'),
    url(r'^pricegroup/(?P<pk>[0-9]+)/delete/$', views.PriceGroupDeleteView.as_view(), name='pricegroup_delete'),

    url(r'^productgroup/$', views.ProductGroupListView.as_view(), name='productgroup_list'),
    url(r'^productgroup/create/$', views.ProductGroupCreateView.as_view(), name='productgroup_create'),
    url(r'^productgroup/(?P<pk>[0-9]+)/$', views.ProductGroupDetailView.as_view(), name='productgroup_detail'),
    url(r'^productgroup/(?P<pk>[0-9]+)/update/$', views.ProductGroupUpdateView.as_view(), name='productgroup_update'),
    url(r'^productgroup/(?P<pk>[0-9]+)/delete/$', views.ProductGroupDeleteView.as_view(), name='productgroup_delete'),

    url(r'^product/(?P<pk>[0-9]+)/$', views.ProductRedirectView.as_view(), name='product_detail'),

    url(r'^product/permanent/$', views.ProductListView.as_view(), name='product_list'),
    url(r'^product/permanent/create/$', views.ProductCreateView.as_view(), name='product_create'),
    url(r'^product/permanent/create/productgroup/(?P<productgroup_pk>[0-9]+)/$',
        views.ProductCreateView.as_view(), name='product_create'),
    url(r'^product/permanent/(?P<pk>[0-9]+)/$', views.ProductDetailView.as_view(), name='product_detail'),
    url(r'^product/permanent/(?P<pk>[0-9]+)/update/$', views.ProductUpdateView.as_view(), name='product_update'),
    url(r'^product/permanent/(?P<pk>[0-9]+)/delete/$', views.ProductDeleteView.as_view(), name='product_delete'),

    url(r'^product/temporary/create/event/(?P<event_pk>[0-9]+)/$', views.TemporaryProductCreateView.as_view(),
        name='temporaryproduct_create'),
    url(r'^product/temporary/(?P<pk>[0-9]+)/update/$', views.TemporaryProductUpdateView.as_view(),
        name='temporaryproduct_update'),
    url(r'^product/temporary/(?P<pk>[0-9]+)/delete/$', views.TemporaryProductDeleteView.as_view(),
        name='temporaryproduct_delete'),

    url(r'^sellingprice/$', views.SellingPriceListView.as_view(), name='sellingprice_list'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>[0-9]+)/$', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/create/productgroup/(?P<productgroup_pk>[0-9]+)/$', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>[0-9]+)/productgroup/(?P<productgroup_pk>[0-9]+)/$',
        views.SellingPriceCreateView.as_view(), name='sellingprice_create'),
    url(r'^sellingprice/(?P<pk>[0-9]+)/update/$', views.SellingPriceUpdateView.as_view(), name='sellingprice_update'),
    url(r'^sellingprice/(?P<pk>[0-9]+)/delete/$', views.SellingPriceDeleteView.as_view(), name='sellingprice_delete'),
]
