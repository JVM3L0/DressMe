from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings

# Limita por IP do cliente. Atrás de um proxy (ex.: plataforma de deploy), o IP
# real só é conhecido se o uvicorn confiar no proxy (FORWARDED_ALLOW_IPS);
# caso contrário, todos os clientes compartilham o limite do IP do proxy.
# O armazenamento em memória vale por processo: com várias instâncias, use um
# backend compartilhado em RATE_LIMIT_STORAGE_URI (ex.: redis://).
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    strategy="moving-window",
    enabled=settings.RATE_LIMIT_ENABLED,
)
