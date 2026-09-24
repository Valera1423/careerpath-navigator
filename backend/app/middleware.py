from slowapi import Limiter
from slowapi.util import get_remote_address


def employer_key_func(request) -> str:
    """Ключ для rate limit: API-ключ или IP."""
    return request.headers.get("X-API-Key") or get_remote_address(request)


limiter = Limiter(key_func=get_remote_address)
employer_limiter = Limiter(key_func=employer_key_func)