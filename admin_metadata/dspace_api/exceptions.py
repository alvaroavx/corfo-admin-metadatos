class DSpaceAPIError(Exception):
    """Error genérico para la API de DSpace."""
    pass


class AuthenticationError(DSpaceAPIError):
    """Error relacionado con la autenticación."""
    pass


class RequestError(DSpaceAPIError):
    """Error relacionado con las solicitudes a la API."""
    pass
