import stat

import pytest

from infrastructure.storage.local_image_storage import LocalImageStorage

pytestmark = pytest.mark.anyio


@pytest.fixture
def storage(tmp_path) -> LocalImageStorage:
    return LocalImageStorage(tmp_path)


async def test_save_creates_folders_and_writes_readable_file(storage, tmp_path):
    await storage.save("photos/a.jpg", b"conteudo")

    path = tmp_path / "photos" / "a.jpg"
    assert path.read_bytes() == b"conteudo"
    assert stat.S_IMODE(path.stat().st_mode) == 0o644
    assert [p.name for p in path.parent.iterdir()] == ["a.jpg"]  # sem temporários


async def test_save_replaces_existing_file(storage):
    await storage.save("photos/a.jpg", b"antigo")
    await storage.save("photos/a.jpg", b"novo")

    assert storage.path("photos/a.jpg").read_bytes() == b"novo"


async def test_delete_removes_file_and_ignores_missing(storage):
    await storage.save("photos/a.jpg", b"x")

    await storage.delete("photos/a.jpg")
    await storage.delete("photos/a.jpg")

    assert not storage.path("photos/a.jpg").exists()


@pytest.mark.parametrize(
    "key", ["../fora.jpg", "photos/../../fora.jpg", "/etc/passwd", ""]
)
async def test_rejects_keys_outside_root(storage, key):
    with pytest.raises(ValueError):
        await storage.save(key, b"x")
