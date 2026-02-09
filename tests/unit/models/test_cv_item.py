import pytest
from app.models.cv_item import CvItem
from typing import Callable, List, Union


def test_cv_item_no_id(make_cv_item: Callable[..., CvItem]):
    item = make_cv_item()
    assert item.visible is True
    assert item.schema_version == 1
    assert item.id.startswith("cvi_")


def test_cv_item_with_custom_id(make_cv_item: Callable[..., CvItem]):
    item = make_cv_item(custom_id="custom_id_123")
    assert item.id == "custom_id_123"
    assert item.visible is True
    assert item.schema_version == 1


@pytest.mark.parametrize(
    "invalid_input", ["not a dict", 123, ["list", "not", "dict"], None, True]
)
def test_ensure_id_skips_non_dict(
    invalid_input: Union[str, int, List[str], None, bool],
):
    result: Union[str, int, List[str], None, bool] = CvItem.ensure_id(invalid_input)  # pyright: ignore[reportCallIssue, reportUnknownVariableType]
    assert result == invalid_input
