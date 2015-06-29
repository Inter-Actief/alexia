from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.stock.views',

    # Hoofdpagina
    url(r'^$', 'stock_list'),

    url(r'^stockcount/edit_stockcount/((?P<stockcount_id>\d+)/)?$', 'edit_stockcount'),
    url(r'^stockproduct/((?P<product_id>\d+)/)?$', 'edit_stockproduct'),

    url(r'^event/list_event_consumptions/((?P<event_id>\d+)/)?$', 'list_event_consumptions'),
    url(r'^event/event_consumption/(?P<event_id>\d+)/new/', 'new'),
    url(r'^event/event_consumption/(?P<event_id>\d+)/(?P<event_consumption_id>\d+)', 'open'),
)
