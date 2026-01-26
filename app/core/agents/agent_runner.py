from app.core.agents.builder import ModelConfig
from app.core.agents.welcome_agent import WelcomeAgentProvider
from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_ai.messages import ModelRequest, SystemPromptPart, ModelMessage
from pydantic_core import to_jsonable_python
from app.core.memory.base import BaseMemory
from app.core.storage import LocalDocumentStorage
from app.core.agents.common import (
    ResumateAgentProvider,
    SupervisorRuntimeContext,
    ModelHandoff,
)
from app.core.agents.resume_content_editor import ResumeContentEditorAgentProvider
from typing import AsyncGenerator, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResumateAgentRunner:
    def __init__(
        self,
        config: ModelConfig,
        document_storage: LocalDocumentStorage | None = None,
    ):
        self.document_storage = document_storage
        # TODO: Dynamically load agent providers from a registry or plugin system
        self.registered_agents_providers: List[ResumateAgentProvider] = [
            WelcomeAgentProvider(),
            ResumeContentEditorAgentProvider(),
        ]
        self.current_agent: Agent[SupervisorRuntimeContext, str | ModelHandoff] = (
            self.registered_agents_providers[0].build(
                config,
                agents_list="\n".join(
                    [
                        f"{provider.name}: {provider.description}"
                        for provider in self.registered_agents_providers
                    ]
                ),
            )
        )
        self.config = config
        self.pending_handoff: ModelHandoff | None = None

    # TODO: Handle message chunks properly instead of yielding raw strings
    async def stream(
        self,
        user_prompt: str,
        message_history: List[ModelMessage],
        memory: BaseMemory,
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
                    logger.info("Received handoff to %s", text.target_agent)
                    self.pending_handoff = text
                    return
                yield text
            messages = response.new_messages()
            messages_python = to_jsonable_python(messages)
            memory.add_messages(
                conversation_id=conversation_id, messages=messages_python
            )

    def find_agent_provider_by_name(self, name: str) -> Optional[ResumateAgentProvider]:
        for provider in self.registered_agents_providers:
            if provider.name == name:
                return provider
        return None

    def apply_handoff(self) -> bool:
        if not self.pending_handoff:
            return False

        handoff = self.pending_handoff
        self.pending_handoff = None

        new_agent_provider = self.find_agent_provider_by_name(handoff.target_agent)

        if not new_agent_provider:
            logger.error(
                "No agent provider found for target agent: %s", handoff.target_agent
            )
            return False
        else:
            self.current_agent = new_agent_provider.build(
                self.config,
                agents_list="\n".join(
                    [
                        f"{provider.name}: {provider.description}"
                        for provider in self.registered_agents_providers
                    ]
                ),
            )
            logger.info("Switched to agent: %s", handoff.target_agent)
            return True

    def record_handoff(
        self, handoff: ModelHandoff, memory: BaseMemory, conversation_id: str
    ):
        message = ModelRequest(
            parts=[
                SystemPromptPart(
                    content=f"Handoff to {handoff.target_agent} initiated."
                )
            ]
        )

        memory.add_messages(
            conversation_id=conversation_id,
            messages=to_jsonable_python(
                ModelMessagesTypeAdapter.validate_python([message])
            ),
        )

    async def run_conversation(
        self,
        user_prompt: str,
        message_history: List[ModelMessage],
        memory: BaseMemory,
        conversation_id: str,
        resume_name: Optional[str] = None,
        max_handoffs: int = 5,
    ) -> AsyncGenerator[str, None]:
        handoff_count = 0

        while True:
            async for chunk in self.stream(
                user_prompt=user_prompt,
                message_history=message_history,
                memory=memory,
                conversation_id=conversation_id,
                resume_name=resume_name,
            ):
                yield chunk

            if not self.pending_handoff:
                break

            self.record_handoff(self.pending_handoff, memory, conversation_id)

            if not self.apply_handoff():
                break

            handoff_count += 1
            if handoff_count >= max_handoffs:
                logger.error("Max handoff limit exceeded.")
                break
