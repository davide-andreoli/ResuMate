import streamlit as st
from pydantic import BaseModel, HttpUrl
from pydantic.fields import FieldInfo
from datetime import date, datetime
from typing import Type, List, Any, Union, get_origin, get_args, Literal, Dict, Optional
from enum import Enum
from app.pages.ui_utils.field_renderers import (
    render_text_area,
    render_text_input,
    render_int_input,
    render_float_input,
)


def is_optional(field: FieldInfo) -> bool:
    """Check if a field is Optional[...]"""
    if get_origin(field.annotation) is Union:
        return type(None) in get_args(field.annotation)
    return False


def extract_literal_choices(annotation: Any) -> List[str]:
    """
    Extract the possible values from a Literal[...] or Optional[Literal[...]] annotation.

    Args:
        annotation: A typing annotation, e.g. Literal["A", "B"] or Optional[Literal["A", "B"]].

    Returns:
        A list of string choices extracted from the Literal.
    """
    args = get_args(annotation)
    if not args:
        return []

    # Case: Optional[Literal[...]] → (Literal[...], NoneType)
    if len(args) == 2 and type(None) in args:
        literal_type = next(a for a in args if a is not type(None))
        return [str(opt) for opt in get_args(literal_type)]

    # Case: plain Literal[...] → ("A", "B", "C")
    if getattr(annotation, "__origin__", None) is Literal:
        return [str(opt) for opt in args]

    return []


def get_field_type(field: FieldInfo) -> str:
    """
    Normalize a Pydantic field into a simple type string.
    Possible outputs:
      "str", "str_long", "int", "float", "bool", "date", "datetime",
      "url", "enum", "literal", "list_str", "unknown"
    """
    field_type = field.annotation

    if get_origin(field_type) is Union:
        non_none_types = [arg for arg in get_args(field_type) if arg is not type(None)]
        if len(non_none_types) == 1:
            field_type = non_none_types[0]

    if field_type is str:
        if "longtext" in (field.description or "").lower():
            return "str_long"
        return "str"
    if field_type is int:
        return "int"
    if field_type is float:
        return "float"
    if field_type is bool:
        return "bool"
    if field_type is date:
        return "date"
    if field_type is datetime:
        return "datetime"
    if field_type is HttpUrl:
        return "url"
    if isinstance(field_type, type) and issubclass(field_type, Enum):
        return "enum"
    if get_origin(field_type) is Literal:
        return "literal"
    if get_origin(field_type) is list and get_args(field_type) == (str,):
        return "list_str"

    return "unknown"


def render_field_widget(
    field_name: str, field: FieldInfo, current_value: Any, widget_key: str
) -> Union[str, int, float, bool, date, datetime, HttpUrl, list[str], None]:
    """Render a widget based on normalized field type."""
    field_type = get_field_type(field)
    field_label = field_name.replace("_", " ").title()

    if current_value is None:
        current_value = field.default if field.default is not ... else None

    if field_type == "str":
        return render_text_input(field_label, current_value or "", widget_key)

    elif field_type == "str_long":
        return render_text_area(field_label, current_value or "", widget_key)

    elif field_type == "int":
        return render_int_input(field, field_label, current_value, widget_key)

    elif field_type == "float":
        return render_float_input(field_label, current_value or 0.0, widget_key)

    elif field_type == "bool":
        return st.checkbox(field_label, value=current_value or False, key=widget_key)

    elif field_type == "date":
        return st.date_input(
            field_label, value=current_value or date.today(), key=widget_key
        )

    elif field_type == "datetime":
        selected_date = st.date_input(
            field_label + " (date)",
            value=(current_value or datetime.now()).date(),
            key=f"{widget_key}_date",
        )
        selected_time = st.time_input(
            field_label + " (time)",
            value=(current_value or datetime.now()).time(),
            key=f"{widget_key}_time",
        )
        return datetime.combine(selected_date, selected_time)

    elif field_type == "url":
        url_value = st.text_input(
            f"{field_label} (URL)", current_value or "", key=widget_key
        )
        try:
            return HttpUrl(url_value) if url_value else None
        except Exception:
            st.warning(f"Invalid URL: {url_value}")
            return current_value

    elif field_type in ["enum", "literal"]:
        if field_type == "enum" and field.annotation is not None:
            options = list(field.annotation.__members__.values())
        else:  # literal
            options = extract_literal_choices(field.annotation)

        if is_optional(field):
            options = [""] + options

        default_index = options.index(current_value) if current_value in options else 0
        selected = st.selectbox(
            field_label, options, index=default_index, key=widget_key
        )
        return None if is_optional(field) and selected == "" else selected

    elif field_type == "list_str":
        text_value = "\n".join(current_value or [])
        text_input = st.text_area(
            f"{field_label} (one per line)", text_value, key=widget_key
        )
        return [line.strip() for line in text_input.split("\n") if line.strip()]

    return st.text_area(
        f"{field_label} (text)", str(current_value or ""), key=widget_key
    )


def initialize_section_data(section_key: str, model: Type[BaseModel], resume_obj: Any):
    """Initialize session state data for a section if not already present."""
    if f"{section_key}_data" not in st.session_state:
        current_data = getattr(resume_obj, section_key, [])
        if current_data:
            st.session_state[f"{section_key}_data"] = [
                item.model_dump() if hasattr(item, "model_dump") else item.__dict__
                for item in current_data
            ]
        else:
            st.session_state[f"{section_key}_data"] = []


def get_section_data(section_key: str) -> List[Dict[str, Any]]:
    """Get section data from session state."""
    return st.session_state.get(f"{section_key}_data", [])


def add_section_item(section_key: str, model: Type[BaseModel]):
    """Add a new item to a section."""
    new_instance = model()
    new_data = (
        new_instance.model_dump()
        if hasattr(new_instance, "model_dump")
        else new_instance.__dict__
    )
    st.session_state[f"{section_key}_data"].append(new_data)


def delete_section_item(section_key: str, index: int):
    """Delete an item from a section."""
    st.session_state[f"{section_key}_data"].pop(index)


def section_data_to_pydantic_objects(
    section_key: str, model: Type[BaseModel]
) -> List[BaseModel]:
    """Convert section data from session state back to Pydantic objects."""
    data = get_section_data(section_key)
    return [model(**item_data) for item_data in data]


def render_pydantic_section(
    title: str,
    model: Type[BaseModel],
    resume_obj: Any,
    field_for_title: Optional[str] = None,
    section_key: Optional[str] = None,
):
    st.subheader(title)

    section_key = section_key or title.lower()

    initialize_section_data(section_key, model, resume_obj)

    if st.button(f"➕ Add {title}", key=f"add_{section_key}"):
        add_section_item(section_key, model)
        st.rerun()

    section_data = get_section_data(section_key)

    if not section_data:
        st.info(
            f"No {title.lower()} entries yet. Click the '➕ Add {title}' button to add one."
        )
        setattr(resume_obj, section_key, [])
        return

    for i, item_data in enumerate(section_data):
        if field_for_title and field_for_title in item_data:
            field_value = item_data.get(field_for_title, "")
            expander_title = f"{title} {i+1}: {field_value or 'New'}"
        else:
            expander_title = f"{title} {i+1}"

        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="top")

        with col1:
            with st.expander(expander_title, expanded=False):
                for field_name, field in model.model_fields.items():
                    if field_name == "schema_version":
                        continue

                    widget_key = f"{section_key}_{i}_{field_name}"
                    current_value = item_data.get(field_name)

                    new_value = render_field_widget(
                        field_name, field, current_value, widget_key
                    )

                    st.session_state[f"{section_key}_data"][i][field_name] = new_value

        with col2:
            st.write("")
            if st.button(
                "🗑️",
                key=f"delete_{section_key}_{i}",
                help=f"Delete this {title.lower()}",
            ):
                delete_section_item(section_key, i)
                st.rerun()

    pydantic_objects = section_data_to_pydantic_objects(section_key, model)
    setattr(resume_obj, section_key, pydantic_objects)
