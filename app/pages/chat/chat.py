from typing import Dict, List
from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter
import streamlit as st
import requests


def from_pydantic_to_openai(messages: List[ModelMessage]) -> List[Dict[str, str]]:
    openai_messages: List[Dict[str, str]] = []
    for message in messages:
        parts = message.parts
        for part in parts:
            if part.part_kind == "user-prompt":
                openai_messages.append({"role": "user", "content": part.content or ""})
            elif part.part_kind == "system-prompt":
                continue
            elif part.part_kind == "text":
                openai_messages.append(
                    {"role": "assistant", "content": part.content or ""}
                )
    return openai_messages


st.title("Chat")

options = requests.get("http://127.0.0.1:8000/resume/list").json()
selected = st.selectbox("Choose from your resumes", options=options)

conversation_id = f"chat_{selected}"
# TODO: Add resume selection to context

if "messages" not in st.session_state:
    messages = requests.get(
        f"http://127.0.0.1:8000/memory/conversations/{conversation_id}/messages"
    ).json()
    pydantic_messages = ModelMessagesTypeAdapter.validate_python(messages)
    openai_messages = from_pydantic_to_openai(pydantic_messages)
    st.session_state.messages = openai_messages

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = requests.post(
            "http://127.0.0.1:8000/chat/",
            json={
                "request": prompt,
                "conversation_id": conversation_id,
                "resume_name": selected,
            },
            stream=True,
        )
        message_placeholder = st.empty()
        full_text = ""
        for chunk in stream.iter_content(decode_unicode=True):
            if chunk:
                if isinstance(chunk, bytes):
                    chunk = chunk.decode("utf-8", errors="replace")
                full_text += chunk
                message_placeholder.markdown(full_text)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_text})
