from app.core.agents.welcome_agent import list_resumes_tool
from app.core.agents.common import SupervisorRuntimeContext
from pydantic_ai import RunContext
from typing import Callable


def test_list_resumes_tool(
    test_supervisor_runtime_context: Callable[
        ..., RunContext[SupervisorRuntimeContext]
    ],
    test_resume_file: str,
):
    context = test_supervisor_runtime_context(resume_id="res_ndzi76id")
    context.deps.document_storage.save_resume(test_resume_file, "res_ndzi76id")
    resumes = context.deps.document_storage.list_resumes()
    result = list_resumes_tool(context)
    assert result is not None
    assert result == "\n".join([str(resume.get_details()) for resume in resumes])
