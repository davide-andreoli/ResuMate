import uuid
import streamlit as st
import requests
import datetime

st.title("Conversations")


def create_new_conversation():
    conversation_id = str(uuid.uuid4())
    status = requests.post(
        f"http://127.0.0.1:8000/memory/conversations/{conversation_id}"
    )
    if status.status_code == 201:
        st.switch_page(
            "chat/chat.py", query_params={"conversation_id": conversation_id}
        )


if st.button("New Conversation", use_container_width=True):
    create_new_conversation()

st.divider()

conversations = requests.get("http://127.0.0.1:8000/memory/conversations").json()

for conversation in conversations:
    with st.container(border=True):
        col1, col2 = st.columns([4, 2])
        with col1:
            title = (
                conversation["title"]
                if conversation.get("title")
                else "Untitled conversation"
            )
            st.subheader(title)
        with col2:
            updated_at = conversation.get("updated_at", "")
            updated_at = datetime.datetime.fromisoformat(updated_at)
            st.caption(f"Last updated: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        col3, col4 = st.columns([4, 2])
        with col3:
            brief = (
                conversation["brief"]
                if conversation.get("brief")
                else "No brief available."
            )
            st.caption(brief)
            st.caption(conversation.get("conversation_id", "No id available."))
        with col4:
            if st.button(
                "Delete",
                key=f"delete_{conversation['conversation_id']}",
                use_container_width=True,
            ):
                requests.delete(
                    f"http://127.0.0.1:8000/memory/conversations/{conversation['conversation_id']}"
                )
                st.rerun()
        if st.button(
            "Open conversation",
            key=conversation["conversation_id"],
            use_container_width=True,
        ):
            st.switch_page(
                "chat/chat.py",
                query_params={"conversation_id": conversation["conversation_id"]},
            )
