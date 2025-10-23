import streamlit as st
from app.frontend.dependencies import get_assistant

st.title("Chat")

assistant = get_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        stream = assistant.stream(prompt=prompt)
        message_placeholder = st.empty()
        full_text = ""
        for chunk in stream:
            full_text += chunk
            message_placeholder.markdown(full_text)

    st.session_state.messages.append(
        {"role": "assistant", "content": message_placeholder}
    )
