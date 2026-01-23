import streamlit as st
import requests

st.title("Conversations")

conversations = requests.get("http://127.0.0.1:8000/memory/conversations").json()

for conversation in conversations:
    st.subheader(f"Conversation ID: {conversation['conversation_id']}")
    st.write(f"Created at: {conversation['created_at']}")
    st.write(f"Last updated: {conversation['updated_at']}")
    open_chat = st.button("View Messages", key=conversation["conversation_id"])
    if open_chat:
        st.switch_page(
            "chat/chat.py",
            query_params={"conversation_id": conversation["conversation_id"]},
        )
