import streamlit as st
from app.frontend.dependencies import get_assistant, get_storage

assistant = get_assistant()
storage = get_storage()

st.title("Chat")

selected = st.selectbox("Choose from your resumes", options=storage.list_resumes())

# TODO: Add resume selection to context

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = assistant.stream(
            request=prompt,
            message_history=st.session_state.messages,
            resume_name=selected,
        )
        message_placeholder = st.empty()
        full_text = ""
        for chunk in stream:
            full_text += chunk
            message_placeholder.markdown(full_text)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_text})
