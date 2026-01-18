from app.core.agents.builder import ModelConfig
from app.core.agents.welcome_agent import (
    build_welcome_agent,
    get_welcome_agent_handoff_info,
)
from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python
from app.core.memory import LocalMemory
from app.core.storage import LocalDocumentStorage
from app.core.agents.common import SupervisorRuntimeContext, ModelHandoff
from app.core.agents.resume_content_editor import (
    build_resume_content_editor_agent,
    get_resume_content_editor_handoff_info,
)
from typing import AsyncGenerator, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ResumateAgentRunner:
    def __init__(
        self,
        config: ModelConfig,
        document_storage: LocalDocumentStorage | None = None,
    ):
        self.document_storage = document_storage
        self.registered_agents_handoffs: list[str] = [
            get_resume_content_editor_handoff_info(),
            get_welcome_agent_handoff_info(),
        ]
        self.current_agent: Agent[SupervisorRuntimeContext, str | ModelHandoff] = (
            build_welcome_agent(
                config, agents_list="\n".join(self.registered_agents_handoffs)
            )
        )

    # TODO: Handle message chunks properly instead of yielding raw strings
    async def stream(
        self,
        user_prompt: str,
        message_history: List[Dict[str, str]],
        memory: LocalMemory,
        conversation_id: str,
        resume_name: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        message_history_adapter = ModelMessagesTypeAdapter.validate_python(
            message_history
        )
        async with self.current_agent.run_stream(
            user_prompt=user_prompt,
            message_history=message_history_adapter,
            deps=SupervisorRuntimeContext(
                document_storage=self.document_storage, resume_name=resume_name
            ),
        ) as response:
            async for text in response.stream_output():
                if isinstance(text, ModelHandoff):
                    if text.target_agent == "resume_content_editor":
                        logger.info("Switching to Resume Content Editor agent.")
                        self.current_agent = build_resume_content_editor_agent(
                            ModelConfig(),
                            agents_list="\n".join(self.registered_agents_handoffs),
                        )
                    elif text.target_agent == "welcome_agent":
                        logger.info("Switching to Welcome agent.")
                        self.current_agent = build_welcome_agent(
                            ModelConfig(),
                            agents_list="\n".join(self.registered_agents_handoffs),
                        )
                    else:
                        logger.warning(f"Unknown target agent: {text.target_agent}")
                    # TODO: Restart the conversation with the new agent, should the current prompt be re-sent?
                if isinstance(text, str):
                    yield text
            messages = response.new_messages()
            messages_python = to_jsonable_python(messages)
            memory.add_messages(
                conversation_id=conversation_id, messages=messages_python
            )
