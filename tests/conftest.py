import pytest
from typing import Any, Callable, Dict, Optional
from app.models.cv_item import CvItem
from app.models.link import Link
from app.models.skill import Skill
import pathlib


@pytest.fixture
def make_cv_item() -> Callable[..., CvItem]:
    def _make_cv_item(
        custom_id: Optional[str] = None, **kwargs: Optional[Dict[str, Any]]
    ) -> CvItem:
        data: Dict[str, Any] = {
            "visible": True,
            "schema_version": 1,
        }
        if custom_id:
            data["id"] = custom_id
        data.update(kwargs)
        return CvItem(**data)

    return _make_cv_item


@pytest.fixture
def make_link() -> Callable[..., Link]:
    def _make_link(**kwargs: Optional[Dict[str, Any]]) -> Link:
        url_data = {
            "label": "GitHub",
            "url": "https://github.com",
            "link_type": "github",
        }
        url_data.update(kwargs)
        return Link(**url_data)

    return _make_link


@pytest.fixture
def make_skill() -> Callable[..., Skill]:
    def _make_skill(**kwargs: Optional[Dict[str, Any]]) -> Skill:
        skill_data = {
            "name": "Python",
            "level": "Advanced",
        }
        skill_data.update(kwargs)
        return Skill(**skill_data)

    return _make_skill


@pytest.fixture
def test_resume_file() -> str:
    path = pathlib.Path(__file__).parent / "fixtures" / "test_resume_data.yaml"
    return path.read_text()
