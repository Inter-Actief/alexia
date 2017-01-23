from jsonrpc.exceptions import Error


class ForbiddenError(Error):
    """ The token was not recognized. """
    code = 403
    status = 200
    message = 'Forbidden.'


class NotFoundError(Error):
    """ The token was not recognized. """
    code = 404
    status = 200
    message = 'Not Found.'


class InvalidParametersError(Error):
    """ Invalid method parameters.

    Copy of jsonrpc.exceptions.InvalidParamsError with 400 status code.
    """
    code = -32602
    status = 200
    message = 'Invalid params.'
