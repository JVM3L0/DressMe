"""Exporta o schema OpenAPI da API para um arquivo JSON.

Usado pelo frontend para gerar os tipos do cliente HTTP. Rode como módulo, a
partir de backend/, para que os pacotes da aplicação sejam encontrados:

    uv run python -m scripts.export_openapi ../frontend/src/lib/api/openapi.json
"""

import json
import os
import sys
from pathlib import Path

# Configuração mínima para importar a aplicação sem `.env` (o schema não
# depende de banco nem de segredos reais)
os.environ.setdefault("MODE", "testing")

from main import app  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("uso: python -m scripts.export_openapi <arquivo de saída>")

    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
