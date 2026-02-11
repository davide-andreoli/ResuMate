import pytest
from app.core.memory.local_file_memory import LocalFileMemory
from app.core.memory.base import ConversationNotFoundError
from pathlib import Path
from pydantic_ai import ModelRequest, ModelResponse
from typing import Callable


def test_create_get_delete_conversation(tmp_path: Path):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "test_conversation"
    conversation = memory.create_conversation(conversation_id)
    assert conversation.conversation_id == conversation_id
    assert conversation.messages == []
    retrieved_conversation = memory.get_conversation(conversation_id)
    assert retrieved_conversation is not None
    assert retrieved_conversation.conversation_id == conversation_id
    deleted = memory.delete_conversation(conversation_id)
    assert deleted
    retrieved_conversation = memory.get_conversation(conversation_id)
    assert retrieved_conversation is None


def test_add_and_get_messages(
    tmp_path: Path,
    make_model_request: Callable[..., ModelRequest],
    make_model_response: Callable[..., ModelResponse],
):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "test_conversation"
    memory.create_conversation(conversation_id)
    message1 = make_model_request(content="Hello")
    message2 = make_model_response(content="How are you?")
    memory.add_message(conversation_id, message1)
    memory.add_message(conversation_id, message2)
    retrieved_conversation = memory.get_conversation(conversation_id)
    assert retrieved_conversation is not None
    assert len(retrieved_conversation.messages) == 2
    assert isinstance(retrieved_conversation.messages[0], ModelRequest)
    assert isinstance(retrieved_conversation.messages[1], ModelResponse)
    assert retrieved_conversation.messages[0].parts[0].content == "Hello"
    assert retrieved_conversation.messages[1].parts[0].content == "How are you?"


def test_add_messages_bulk_and_get_messages(
    tmp_path: Path,
    make_model_request: Callable[..., ModelRequest],
    make_model_response: Callable[..., ModelResponse],
):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "test_conversation"
    memory.create_conversation(conversation_id)
    messages = [
        make_model_request(content="Hello"),
        make_model_response(content="How are you?"),
        make_model_request(content="What's the weather like?"),
    ]
    memory.add_messages(conversation_id, messages)
    retrieved_conversation = memory.get_conversation(conversation_id)
    assert retrieved_conversation is not None
    assert len(retrieved_conversation.messages) == 3
    assert retrieved_conversation.messages[0].parts[0].content == "Hello"
    assert retrieved_conversation.messages[1].parts[0].content == "How are you?"
    assert (
        retrieved_conversation.messages[2].parts[0].content
        == "What's the weather like?"
    )


def test_add_message_to_nonexistent_conversation(
    tmp_path: Path, make_model_request: Callable[..., ModelRequest]
):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "nonexistent_conversation"
    message = make_model_request(content="Hello")
    with pytest.raises(ConversationNotFoundError):
        memory.add_message(conversation_id, message)


def test_add_messages_to_nonexistent_conversation(
    tmp_path: Path, make_model_request: Callable[..., ModelRequest]
):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "nonexistent_conversation"
    messages = [
        make_model_request(content="Hello"),
        make_model_request(content="How are you?"),
    ]
    with pytest.raises(ConversationNotFoundError):
        memory.add_messages(conversation_id, messages)


def test_get_all_conversations(
    tmp_path: Path, make_model_request: Callable[..., ModelRequest]
):
    memory = LocalFileMemory(str(tmp_path))
    conversation_ids = ["conversation1", "conversation2", "conversation3"]
    for cid in conversation_ids:
        memory.create_conversation(cid)
        message = make_model_request(content=f"Message for {cid}")
        memory.add_message(cid, message)
    conversations = memory.get_all_conversations()
    assert len(conversations) == 3
    retrieved_ids = {conv.conversation_id for conv in conversations}
    assert set(conversation_ids) == retrieved_ids


def test_delete_nonexistent_conversation(tmp_path: Path):
    memory = LocalFileMemory(str(tmp_path))
    conversation_id = "nonexistent_conversation"
    deleted = memory.delete_conversation(conversation_id)
    assert not deleted
