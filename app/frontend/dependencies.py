import streamlit as st
from app.core.yaml_manager import YamlManager
from app.core.storage import LocalDocumentStorage


@st.cache_resource
def get_yaml_manager():
    return YamlManager()


@st.cache_resource
def get_storage():
    return LocalDocumentStorage()
