import streamlit as st
import requests

st.title("Chat")

options = requests.get("http://127.0.0.1:8000/resume/list").json()
selected = st.selectbox("Choose from your resumes", options=options)

conversation_id = f"chat_{selected}"
# TODO: Add resume selection to context

if "messages" not in st.session_state:
    messages = requests.get(
        f"http://127.0.0.1:8000/memory/conversations/{conversation_id}/messages"
    ).json()
    st.session_state.messages = messages

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
