from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^order/$', views.order_list, name='orders'),
    url(r'^order/(?P<pk>\d+)/$', views.order_show, name='event-orders'),
    url(r'^stats/(?P<year>\d+)/$', views.stats_year, name='year-orders'),
    url(r'^stats/(?P<year>\d+)/(?P<month>\d+)/$', views.stats_month, name='month-orders'),
    url(r'^payment/(?P<pk>\d+)/$', views.payment_show, name='order'),

    url(r'^pricegroup/$', views.PriceGroupListView.as_view(), name='pricegroup_list'),
    url(r'^pricegroup/create/$', views.PriceGroupCreateView.as_view(), name='pricegroup_create'),
    url(r'^pricegroup/(?P<pk>\d+)/$', views.PriceGroupDetailView.as_view(), name='pricegroup_detail'),
    url(r'^pricegroup/(?P<pk>\d+)/update/$', views.PriceGroupUpdateView.as_view(), name='pricegroup_update'),

    url(r'^productgroup/$', views.ProductGroupListView.as_view(), name='productgroup_list'),
    url(r'^productgroup/create/$', views.ProductGroupCreateView.as_view(), name='productgroup_create'),
    url(r'^productgroup/(?P<pk>\d+)/$', views.ProductGroupDetailView.as_view(), name='productgroup_detail'),
    url(r'^productgroup/(?P<pk>\d+)/update/$', views.ProductGroupUpdateView.as_view(), name='productgroup_update'),

    url(r'^product/(?P<pk>\d+)/$', views.ProductRedirectView.as_view(), name='product_detail'),
    url(r'^product/permanent/$', views.PermanentProductListView.as_view(), name='permanentproduct_list'),
    url(r'^product/permanent/create/$', views.PermanentProductCreateView.as_view(), name='permanentproduct_create'),
    url(r'^product/permanent/create/productgroup/(?P<productgroup_pk>\d+)/$',
        views.PermanentProductCreateView.as_view(), name='permanentproduct_create'),
    url(r'^product/permanent/(?P<pk>\d+)/$', views.PermanentProductDetailView.as_view(),
        name='permanentproduct_detail'),
    url(r'^product/permanent/(?P<pk>\d+)/update/$', views.PermanentProductUpdateView.as_view(),
        name='permanentproduct_update'),
    url(r'^product/temporary/create/event/(?P<event_pk>\d+)/$', views.TemporaryProductCreateView.as_view(),
        name='temporaryproduct_create'),
    url(r'^product/temporary/(?P<pk>\d+)/$', views.TemporaryProductDetailView.as_view(),
        name='temporaryproduct_detail'),
    url(r'^product/temporary/(?P<pk>\d+)/update/$', views.TemporaryProductUpdateView.as_view(),
        name='temporaryproduct_update'),

    url(r'^sellingprice/matrix/$', views.SellingPriceMatrixView.as_view(), name='sellingprice_matrix'),
    url(r'^sellingprice/create/$', views.SellingPriceCreateView.as_view(), name='sellingprice_create'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>\d+)/$', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>\d+)/productgroup/(?P<productgroup_pk>\d+)/$',
        views.SellingPriceCreateView.as_view(), name='sellingprice_create'),
    url(r'^sellingprice/create/productgroup/(?P<productgroup_pk>\d+)/$', views.SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/(?P<pk>\d+)/update/$', views.SellingPriceUpdateView.as_view(), name='sellingprice_update'),
    url(r'^sellingprice/(?P<pk>\d+)/delete/$', views.SellingPriceDeleteView.as_view(), name='sellingprice_delete'),
]
