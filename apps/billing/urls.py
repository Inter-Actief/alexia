from django.conf.urls import patterns, url

from apps.billing.views import PriceGroupListView, PriceGroupCreateView, PriceGroupDetailView, PriceGroupUpdateView, \
    ProductGroupListView, ProductGroupCreateView, ProductGroupDetailView, ProductGroupUpdateView, ProductGroupDeleteView, \
    ProductRedirectView, \
    PermanentProductListView, PermanentProductCreateView, PermanentProductDetailView, PermanentProductUpdateView, \
    PermanentProductDeleteView, TemporaryProductDeleteView, \
    TemporaryProductCreateView, TemporaryProductDetailView, TemporaryProductUpdateView, SellingPriceMatrixView, \
    SellingPriceCreateView, SellingPriceUpdateView, SellingPriceDeleteView

urlpatterns = patterns(
    'apps.billing.views',

    url(r'^order/$', 'order_list'),
    url(r'^order/(?P<pk>\d+)/$', 'order_show'),
    url(r'^stats/(?P<year>\d+)/$', 'stats_year'),
    url(r'^stats/(?P<year>\d+)/(?P<month>\d+)/$', 'stats_month'),
    url(r'^payment/(?P<pk>\d+)/$', 'payment_show'),

    url(r'^pricegroup/$', PriceGroupListView.as_view(), name='pricegroup_list'),
    url(r'^pricegroup/create/$', PriceGroupCreateView.as_view(), name='pricegroup_create'),
    url(r'^pricegroup/(?P<pk>\d+)/$', PriceGroupDetailView.as_view(), name='pricegroup_detail'),
    url(r'^pricegroup/(?P<pk>\d+)/update/$', PriceGroupUpdateView.as_view(), name='pricegroup_update'),

    url(r'^productgroup/$', ProductGroupListView.as_view(), name='productgroup_list'),
    url(r'^productgroup/create/$', ProductGroupCreateView.as_view(), name='productgroup_create'),
    url(r'^productgroup/(?P<pk>\d+)/$', ProductGroupDetailView.as_view(), name='productgroup_detail'),
    url(r'^productgroup/(?P<pk>\d+)/update/$', ProductGroupUpdateView.as_view(), name='productgroup_update'),
    url(r'^productgroup/(?P<pk>\d+)/delete/$', ProductGroupDeleteView.as_view(), name='productgroup_delete'),

    url(r'^product/(?P<pk>\d+)/$', ProductRedirectView.as_view(), name='product_detail'),
    url(r'^product/permanent/$', PermanentProductListView.as_view(), name='permanentproduct_list'),
    url(r'^product/permanent/create/$', PermanentProductCreateView.as_view(), name='permanentproduct_create'),
    url(r'^product/permanent/create/productgroup/(?P<productgroup_pk>\d+)/$', PermanentProductCreateView.as_view(),
        name='permanentproduct_create'),
    url(r'^product/permanent/(?P<pk>\d+)/$', PermanentProductDetailView.as_view(), name='permanentproduct_detail'),
    url(r'^product/permanent/(?P<pk>\d+)/update/$', PermanentProductUpdateView.as_view(),
        name='permanentproduct_update'),
    url(r'^product/permanent/(?P<pk>\d+)/delete/$', PermanentProductDeleteView.as_view(),
        name='permanentproduct_delete'),
    url(r'^product/temporary/create/event/(?P<event_pk>\d+)/$', TemporaryProductCreateView.as_view(),
        name='temporaryproduct_create'),
    url(r'^product/temporary/(?P<pk>\d+)/$', TemporaryProductDetailView.as_view(), name='temporaryproduct_detail'),
    url(r'^product/temporary/(?P<pk>\d+)/update/$', TemporaryProductUpdateView.as_view(),
        name='temporaryproduct_update'),
    url(r'^product/temporary/(?P<pk>\d+)/delete/$', TemporaryProductDeleteView.as_view(),
        name='temporaryproduct_delete'),

    url(r'^sellingprice/matrix/$', SellingPriceMatrixView.as_view(), name='sellingprice_matrix'),
    url(r'^sellingprice/create/$', SellingPriceCreateView.as_view(), name='sellingprice_create'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>\d+)/$', SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/create/pricegroup/(?P<pricegroup_pk>\d+)/productgroup/(?P<productgroup_pk>\d+)/$',
        SellingPriceCreateView.as_view(), name='sellingprice_create'),
    url(r'^sellingprice/create/productgroup/(?P<productgroup_pk>\d+)/$', SellingPriceCreateView.as_view(),
        name='sellingprice_create'),
    url(r'^sellingprice/(?P<pk>\d+)/update/$', SellingPriceUpdateView.as_view(), name='sellingprice_update'),
    url(r'^sellingprice/(?P<pk>\d+)/delete/$', SellingPriceDeleteView.as_view(), name='sellingprice_delete'),
)
