import base64
import pytest
from typing import Callable
from app.models.link import Link
from unittest.mock import patch, mock_open


@pytest.mark.parametrize(
    "link_type, expected_rel_path",
    [
        ("website", "icons/website.png"),
        ("github", "icons/github.png"),
        ("linkedin", "icons/linkedin.png"),
    ],
)
def test_link_default_icon(
    make_link: Callable[..., Link], link_type: str, expected_rel_path: str
):
    link = make_link(link_type=link_type)
    with patch("os.path.exists", return_value=False):
        assert link.link_icon == expected_rel_path


def test_link_icon_base64_conversion(make_link: Callable[..., Link]):
    link = make_link(link_type="github")
    fake_image_data = b"fake image data"
    with patch("os.path.exists", return_value=True), patch(
        "os.path.isfile", return_value=True
    ), patch("mimetypes.guess_type", return_value=("image/png", None)), patch(
        "builtins.open", mock_open(read_data=fake_image_data)
    ):
        expected_b64 = base64.b64encode(fake_image_data).decode("ascii")
        expected_data_uri = f"data:image/png;base64,{expected_b64}"
        assert link.link_icon == expected_data_uri


def test_link_icon_exception_handling(make_link: Callable[..., Link]):
    link = make_link(link_type="website")

    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", side_effect=PermissionError
    ):
        assert link.link_icon == "icons/website.png"


def test_link_icon_unknown_type(make_link: Callable[..., Link]):
    link = make_link()
    link.link_type = "unknown"
    assert link.link_icon is None


def test_link_icon_no_mime_type(make_link: Callable[..., Link]):
    link = make_link(link_type="github")
    fake_image_data = b"fake image data"
    with patch("os.path.exists", return_value=True), patch(
        "os.path.isfile", return_value=True
    ), patch("mimetypes.guess_type", return_value=(None, None)), patch(
        "builtins.open", mock_open(read_data=fake_image_data)
    ):
        expected_b64 = base64.b64encode(fake_image_data).decode("ascii")
        expected_data_uri = f"data:application/octet-stream;base64,{expected_b64}"
        assert link.link_icon == expected_data_uri
