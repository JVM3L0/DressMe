import pytest

from tests.fakes import make_stored_image


@pytest.mark.parametrize(
    ("key", "thumbnail_key"),
    [
        ("photos/abc.jpg", "photos/abc_thumb.jpg"),
        ("garments/0a1b-2c3d.png", "garments/0a1b-2c3d_thumb.png"),
    ],
)
def test_thumbnail_key_is_derived_from_the_image_key(key, thumbnail_key):
    assert make_stored_image(key=key).thumbnail_key == thumbnail_key


def test_thumbnail_key_stays_in_the_same_folder():
    image = make_stored_image(key="photos/abc.jpg")

    assert image.thumbnail_key.startswith("photos/")
    assert image.thumbnail_key != image.key
