from django.urls import path

from .views import APIInfoView

from modernrpc.core import Protocol
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    path('', APIInfoView.as_view(), name='api'),

    path('1/', RPCEntryPoint.as_view(protocol=Protocol.JSON_RPC, entry_point="v1"), name="jsonrpc_mountpoint"),
    path('1/doc/', RPCEntryPoint.as_view(enable_doc=True, enable_rpc=False, template_name="api/v1/doc.html", entry_point="v1")),
]
