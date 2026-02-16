import pytest
from app.models.skill import Skill
from typing import Callable


@pytest.mark.parametrize(
    "skill_level, expected_value",
    [
        ("Beginner", 1),
        ("Intermediate", 2),
        ("Advanced", 3),
        ("Expert", 4),
    ],
)
def test_skill_level_number(
    make_skill: Callable[..., Skill], skill_level: str, expected_value: int
):
    skill = make_skill(level=skill_level)
    assert skill.level_number == expected_value
