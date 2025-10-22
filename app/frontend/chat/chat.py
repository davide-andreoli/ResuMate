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

    response = f"Echo: {prompt}"

    with st.chat_message("assistant"):
        stream = assistant.stream(prompt=prompt)
        for chunk in stream:
            print(type(chunk))
            st.write(chunk)

    st.session_state.messages.append({"role": "assistant", "content": response})
