import streamlit as st
from pydantic.fields import FieldInfo


def render_text_area(field_label: str, current_value: str, widget_key: str) -> str:
    return st.text_area(field_label, current_value, key=widget_key)


def render_text_input(field_label: str, current_value: str, widget_key: str) -> str:
    return st.text_input(field_label, current_value, key=widget_key)


def render_int_input(
    field: FieldInfo, field_label: str, current_value: int, widget_key: str
) -> int:
    ge, le = None, None
    for m in field.metadata:
        if hasattr(m, "ge"):
            ge = m.ge
        if hasattr(m, "le"):
            le = m.le
    if ge is not None and le is not None:
        return st.slider(
            field_label,
            min_value=ge,
            max_value=le,
            value=current_value or ge,
            key=widget_key,
        )
    else:
        return st.number_input(field_label, value=current_value, step=1, key=widget_key)


def render_float_input(
    field_label: str, current_value: float, widget_key: str
) -> float:
    return st.number_input(
        field_label,
        value=current_value or 0.0,
        step=0.01,
        format="%.2f",
        key=widget_key,
    )
