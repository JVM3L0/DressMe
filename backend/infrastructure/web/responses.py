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

INVALID_OUTFIT: dict[int | str, dict[str, Any]] = {
    422: {
        "description": "Dados inválidos, ou uma composição que não vale "
        "(peça que não é do usuário, categoria repetida, peça única com parte "
        "de cima ou de baixo). Neste caso, `detail` é um texto e `code` diz o motivo."
    }
}
