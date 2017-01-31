from jsonrpc.exceptions import Error


class ForbiddenError(Error):
    """ The token was not recognized. """
    code = 403
    status = 403
    message = 'Forbidden.'


class ObjectNotFoundError(Error):
    """ The requested object does not exist. """
    code = 404
    message = 'Object not found.'
    status = 404


class InvalidParamsError(Error):
    """ Invalid method parameters. """
    code = -32602
    message = 'Invalid params.'
    status = 422
