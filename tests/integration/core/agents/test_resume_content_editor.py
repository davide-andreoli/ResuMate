from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import read_resume_content
from pydantic_ai import RunContext
from typing import Callable


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
