from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import (
    read_resume_content,
    edit_resume_content,
)
from pydantic_ai import RunContext
from typing import Callable, cast

from app.models.skill import Skill


def test_read_resume_content(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
    test_resume_file: str,
):
    context = test_supervisor_runtime_context(resume_id="res_ndzi76id")
    context.deps.document_storage.save_resume(test_resume_file, "res_ndzi76id")
    resume = context.deps.document_storage.get_resume("res_ndzi76id")

    content = read_resume_content(context)
    assert content is not None
    assert content == resume.model_dump_json(indent=2)


def test_read_resume_content_no_resume_selected(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
):
    context = test_supervisor_runtime_context(resume_id=None)
    content = read_resume_content(context)
    assert content == "No resume selected."


def test_edit_resume_content(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
    test_resume_file: str,
    make_skill: Callable[..., Skill],
):
    context = test_supervisor_runtime_context(resume_id="res_ndzi76id")
    context.deps.document_storage.save_resume(test_resume_file, "res_ndzi76id")
    skill = make_skill(name="Python", level="Expert")
    result = edit_resume_content(context, "ski_pjfqsp7a", skill)
    assert result == "Resume content updated successfully."
    resume = context.deps.document_storage.get_resume("res_ndzi76id")
    updated_skill: Skill = cast(Skill, resume.get_element_by_id("ski_pjfqsp7a"))
    assert updated_skill is not None
    assert updated_skill.name == "Python"
    assert updated_skill.level == "Expert"


def test_edit_resume_content_no_resume_selected(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
    make_skill: Callable[..., Skill],
):
    context = test_supervisor_runtime_context(resume_id=None)
    skill = make_skill(name="Python", level="Expert")
    result = edit_resume_content(context, "ski_pjfqsp7a", skill)
    assert result == "No resume selected."


def test_edit_resume_content_element_not_found(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
    test_resume_file: str,
    make_skill: Callable[..., Skill],
):
    context = test_supervisor_runtime_context(resume_id="res_ndzi76id")
    context.deps.document_storage.save_resume(test_resume_file, "res_ndzi76id")
    skill = make_skill(name="Python", level="Expert")
    result = edit_resume_content(context, "non_existent_id", skill)
    assert result == "Failed to update resume content."
