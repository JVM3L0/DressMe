import os
import tempfile
from pathlib import Path

from anyio import to_thread


class LocalImageStorage:
    """Imagens em disco, num volume compartilhado com o nginx (ADR-0003)"""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def path(self, key: str) -> Path:
        """Caminho do arquivo. As chaves são geradas pela aplicação, mas a
        checagem impede que uma chave como `../x` saia da pasta."""
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root) or path == self.root:
            raise ValueError("Chave de imagem inválida")
        return path

    async def save(self, key: str, data: bytes) -> None:
        await to_thread.run_sync(self._save, self.path(key), data)

    async def delete(self, key: str) -> None:
        await to_thread.run_sync(self._delete, self.path(key))

    @staticmethod
    def _save(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Grava num arquivo temporário e renomeia: o nginx nunca entrega um
        # arquivo pela metade
        fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".upload-")
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(data)
            os.chmod(temp, 0o644)  # legível pelo nginx
            os.replace(temp, path)
        except BaseException:
            Path(temp).unlink(missing_ok=True)
            raise

    @staticmethod
    def _delete(path: Path) -> None:
        path.unlink(missing_ok=True)
