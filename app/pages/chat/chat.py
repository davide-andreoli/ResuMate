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


@st.dialog("Change Resume", on_dismiss="rerun")
def change_resume(options: List[str]):
    st.session_state.selected_resume = st.selectbox(
        "Choose from your resumes",
        options,
        index=options.index(st.session_state.selected_resume),
    )


st.title("Chat")

resume_list = requests.get("http://127.0.0.1:8000/resume/list").json()

if not resume_list:
    st.info("No resumes found. Please create a resume first in the Resume section.")
    st.stop()

if "selected_resume" not in st.session_state:
    st.session_state.selected_resume = resume_list[0] if resume_list else None


conversation_id = f"chat_{st.session_state.selected_resume}"

if "messages" not in st.session_state:
    messages = requests.get(
        f"http://127.0.0.1:8000/memory/conversations/{conversation_id}/messages"
    ).json()
    pydantic_messages = ModelMessagesTypeAdapter.validate_python(messages)
    openai_messages = from_pydantic_to_openai(pydantic_messages)
    st.session_state.messages = openai_messages

chat_messages_container = st.container()


with chat_messages_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

context_container = st.popover("Chat context", width="stretch")
with context_container:
    # TODO: Add a tooltip with last working agent ?
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Selected Resume:** {st.session_state.selected_resume}")
    with col2:
        if st.button("Change Resume"):
            # TODO: The change resume button should open a modal with resume cards to select from
            change_resume(resume_list)


prompt = st.chat_input("Say something")
if prompt:
    with chat_messages_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    with chat_messages_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
    # TODO: try to use st.write_stream, but probably need to adapt the backend to yield in increments properly
    stream = requests.post(
        "http://127.0.0.1:8000/chat/",
        json={
            "request": prompt,
            "conversation_id": conversation_id,
            "resume_name": st.session_state.selected_resume,
        },
        stream=True,
    )

    full_response = ""
    # Using PydanticAI, each chunk contains the whole message so far
    for chunk in stream.iter_content(decode_unicode=True, chunk_size=4096):
        if chunk:
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8", errors="replace")
            full_response = chunk
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_response})
