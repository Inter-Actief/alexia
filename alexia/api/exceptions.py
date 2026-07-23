from modernrpc.exceptions import RPCException, RPC_INVALID_PARAMS, RPC_CUSTOM_ERROR_BASE


class ForbiddenError(RPCException):
    """ The token was not recognized. """
    def __init__(self, message=None):
        super(ForbiddenError, self).__init__(
            code=(RPC_CUSTOM_ERROR_BASE + 3),
            message='Forbidden.' if message is None else message
        )


class ObjectNotFoundError(RPCException):
    """ The requested object does not exist. """
    def __init__(self, message=None):
        super(ObjectNotFoundError, self).__init__(
            code=404,
            message='Object not found.' if message is None else message
        )


class InvalidParamsError(RPCException):
    """ Invalid method parameters. """
    def __init__(self, message=None):
        super(InvalidParamsError, self).__init__(
            code=RPC_INVALID_PARAMS,
            message='Invalid params.' if message is None else message
        )


class UnregisteredCardError(RPCException):
    """ Invalid method parameters. """
    def __init__(self, card_register_url=None, message=None):
        super(UnregisteredCardError, self).__init__(
            code=RPC_INVALID_PARAMS,
            message='Unregistered card.' if message is None else message,
            data={"card_register_url":card_register_url}
        )
