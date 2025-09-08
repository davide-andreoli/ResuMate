import streamlit as st
from pydantic import BaseModel, HttpUrl
from datetime import date, datetime
from typing import Type, List, Any, Union, get_origin, get_args, Literal
from enum import Enum

# TODO: Refactor this: all typing logic should stay inside get_field_type, which should return a string or literal
# All renderes should be single functions to be more maintainable


def is_optional(field: BaseModel) -> bool:
    """Check if a field is Optional[...]"""
    if get_origin(field.annotation) is Union:
        args = get_args(field.annotation)
        return type(None) in args
    return False


def get_field_type(field):
    """Extract the actual type from a Pydantic field."""
    field_type = field.annotation

    if get_origin(field_type) is Union:
        args = get_args(field_type)
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            field_type = non_none_types[0]

    return field_type


def render_field_widget(field_name: str, field, current_value: Any, widget_key: str):
    field_type = get_field_type(field)
    field_label = field_name.replace("_", " ").title()

    if current_value is None:
        current_value = field.default if field.default is not ... else None

    if field_type is str:
        if any(
            keyword in field_name.lower()
            for keyword in ["details", "description", "summary", "notes"]
        ):
            return st.text_area(field_label, current_value or "", key=widget_key)
        else:
            return st.text_input(field_label, current_value or "", key=widget_key)

    elif field_type is int:
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
            return st.number_input(
                field_label, value=current_value or 0, step=1, key=widget_key
            )

    elif field_type is float:
        return st.number_input(
            field_label,
            value=current_value or 0.0,
            step=0.01,
            format="%.2f",
            key=widget_key,
        )

    elif field_type is bool:
        return st.checkbox(field_label, value=current_value or False, key=widget_key)

    elif field_type is date:
        default_date = current_value or date.today()
        return st.date_input(field_label, value=default_date, key=widget_key)

    elif field_type is datetime:
        default_datetime = current_value or datetime.now()
        return st.datetime_input(field_label, value=default_datetime, key=widget_key)

    elif field_type is HttpUrl:
        url_value = st.text_input(
            f"{field_label} (URL)", current_value or "", key=widget_key
        )
        try:
            return HttpUrl(url_value) if url_value else None
        except Exception:
            st.warning(f"Invalid URL: {url_value}")
            return current_value

    elif isinstance(field_type, type) and issubclass(field_type, Enum):
        options = list(field_type)

        if is_optional(field):
            options = [""] + options

        default_index = 0
        if current_value in options:
            default_index = options.index(current_value)

        selected = st.selectbox(
            field_label, options, index=default_index, key=widget_key
        )
        if is_optional(field) and selected == "":
            return None
        return selected

    elif get_origin(field_type) is Literal:
        options = list(get_args(field_type))

        if is_optional(field):
            options = [""] + options

        default_index = 0
        if current_value in options:
            default_index = options.index(current_value)

        selected = st.selectbox(
            field_label, options, index=default_index, key=widget_key
        )
        if is_optional(field) and selected == "":
            return None
        return selected

    elif get_origin(field_type) is list:
        list_args = get_args(field_type)
        if list_args and list_args[0] is str:
            text_value = "\n".join(current_value) if current_value else ""
            text_input = st.text_area(
                f"{field_label} (one per line)", text_value, key=widget_key
            )
            return [line.strip() for line in text_input.split("\n") if line.strip()]

    return st.text_area(
        f"{field_label} (text)", str(current_value or ""), key=widget_key
    )


def render_pydantic_section(
    title: str,
    model: Type[BaseModel],
    resume_obj: Any,
    field_for_title: str = None,
    section_key: str = None,
):
    st.subheader(title)

    section_key = section_key or title.lower()

    if section_key not in st.session_state:
        current_data = getattr(resume_obj, section_key, [])
        st.session_state[section_key] = current_data or []

    if st.button(f"➕ Add {title}", key=f"add_{section_key}"):
        new_instance = model()
        st.session_state[section_key].append(new_instance)
        st.rerun()

    items: List[BaseModel] = st.session_state[section_key]

    if not items:
        st.info(
            f"No {title.lower()} entries yet. Click the '➕ Add {title}' button to add one."
        )
        return

    for i, item in enumerate(items):
        if field_for_title and hasattr(item, field_for_title):
            field_value = getattr(item, field_for_title, "")
            expander_title = f"{title} {i+1}: {field_value or 'New'}"
        else:
            expander_title = f"{title} {i+1}"

        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="top")

        with col1:
            with st.expander(expander_title, expanded=False):
                for field_name, field in model.model_fields.items():
                    if field_name == "schema_version":
                        continue
                    current_value = getattr(item, field_name)
                    widget_key = f"{section_key}_{i}_{field_name}"

                    new_value = render_field_widget(
                        field_name, field, current_value, widget_key
                    )
                    setattr(item, field_name, new_value)

        with col2:
            st.write("")
            if st.button(
                "🗑️",
                key=f"delete_{section_key}_{i}",
                help=f"Delete this {title.lower()}",
            ):
                st.session_state[section_key].pop(i)
                st.rerun()

    setattr(resume_obj, section_key, st.session_state[section_key])
