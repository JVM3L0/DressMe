"""Respostas de erro comuns, para documentar as rotas no OpenAPI"""

from typing import Any

UNAUTHORIZED: dict[int | str, dict[str, Any]] = {
    401: {"description": "Sem sessão ou com sessão expirada."}
}

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    404: {"description": "Não existe, ou pertence a outro usuário."}
}

IMAGE_RESPONSES: dict[int | str, dict[str, Any]] = {
    413: {"description": "A imagem passa de 10 MB."},
    415: {"description": "O arquivo não é uma imagem JPEG ou PNG válida."},
    429: {"description": "Limite de envios por IP atingido."},
}
