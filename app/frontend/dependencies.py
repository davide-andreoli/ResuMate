import streamlit as st
from app.api.deps import (
    get_storage as _get_storage,
    get_yaml_manager as _get_yaml_manager,
    get_assistant as _get_assistant,
)


@st.cache_resource
def get_storage():
    return _get_storage()


@st.cache_resource
def get_yaml_manager():
    return _get_yaml_manager()


@st.cache_resource
def get_assistant():
    return _get_assistant()
