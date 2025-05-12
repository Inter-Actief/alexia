import json

from modernrpc.handlers import JSONRPCHandler
from modernrpc.handlers.jsonhandler import JsonResult, JsonSuccessResult, JsonErrorResult

from alexia.api.v1 import version


class AlexiaJSONRPCHandler(JSONRPCHandler):

    # Override content types because older apps send an initialization request with the content type
    # text/plain, so we need to add that to the allowed content types for JSON-RPC. -- albertskja 2025-05-12
    @staticmethod
    def valid_content_types():
        return [
            "text/plain",
            "application/json",
            "application/json-rpc",
            "application/jsonrequest",
        ]

    def process_single_request(self, request_data, context):
        # Older apps send the jsonrpc version as a float, but the library expects it as a string.
        # So we need to overwrite that attribute to the correct type if it is a float. -- albertskja 2025-05-12
        if request_data and isinstance(request_data, dict) and "jsonrpc" in request_data and isinstance(request_data['jsonrpc'], float):
            request_data['jsonrpc'] = str(request_data['jsonrpc'])

        # Older apps may set the jsonrpc attribute to "1.0", but the library expects "2.0".
        # Because there is no functional difference otherwise, and to maintain backwards compatibility
        # we can just override it to "2.0" in those cases. -- albertskja 2025-05-12
        version_overridden = False
        if request_data and isinstance(request_data, dict) and "jsonrpc" in request_data and request_data['jsonrpc'] == "1.0":
            request_data['jsonrpc'] = "2.0"
            version_overridden = True

        result_data = super().process_single_request(request_data=request_data, context=context)

        # Put back the version "1.0" if it was previously overridden -- albertskja 2025-05-12
        if version_overridden:
            result_data.version = "1.0"

        return result_data

    def dumps_result(self, result: JsonResult) -> str:
        # The old API backend included the "error" attribute set to None, even if the request was successful.
        # Also, it included the "result" attribute set to None, even if the request failed.
        # ModernRPC does not, so we need to add those back to maintain backwards compatibility -- albertskja 2025-05-12
        result_json = json.loads(super().dumps_result(result))
        if isinstance(result, JsonSuccessResult) and "error" not in result_json.keys():
            result_json["error"] = None
        if isinstance(result, JsonErrorResult) and "result" not in result_json.keys():
            result_json["result"] = None
        return json.dumps(result_json)
