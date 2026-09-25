import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path

from models import (
    Background,
    ContentObject,
    GlobalDefaults,
    Slide,
    SlideType,
    Style,
)

from presentation import (
    Presentation,
    PresentationSection,
    SequenceItem,
)


def to_json_data(obj):
    """Convert enums and dataclasses into JSON-compatible data."""
    if isinstance(obj, Enum):
        return obj.value

    if hasattr(obj, "__dataclass_fields__"):
        return to_json_data(asdict(obj))

    if isinstance(obj, dict):
        return {
            key: to_json_data(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [to_json_data(item) for item in obj]

    return obj


def slide_from_dict(data):
    """Rebuild a Slide object from saved JSON data."""
    return Slide(
        id=data["id"],
        type=SlideType(data["type"]),
        primary=ContentObject(
            content=data["primary"]["content"],
            style=Style(**data["primary"]["style"]),
        ),
        secondary=ContentObject(
            content=data["secondary"]["content"],
            style=Style(**data["secondary"]["style"]),
        ),
        background=Background(**data["background"]),
        use_custom_style=data.get("use_custom_style", False),
        use_custom_background=data.get(
            "use_custom_background", False
        ),
    )


def defaults_from_dict(data):
    """Rebuild GlobalDefaults from saved JSON data."""
    return GlobalDefaults(
        primary_style=Style(**data["primary_style"]),
        secondary_style=Style(**data["secondary_style"]),
        background=Background(**data["background"]),
    )


def presentation_from_dict(data):
    """Rebuild the presentation sequence from saved JSON data."""

    def load_section(section_data):
        return PresentationSection(
            name=section_data["name"],
            items=[
                SequenceItem(**item)
                for item in section_data["items"]
            ],
        )

    return Presentation(
        beginning=load_section(data["beginning"]),
        main=load_section(data["main"]),
        end=load_section(data["end"]),
    )


def save_project(
    file_path,
    slides,
    global_defaults,
    presentation,
):
    """Save the complete project to a JSON file."""

    project_data = {
        "version": 1,
        "slides": [to_json_data(slide) for slide in slides],
        "global_defaults": to_json_data(global_defaults),
        "presentation": to_json_data(presentation),
    }

    path = Path(file_path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            project_data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def load_project(file_path):
    """Load a project from a JSON file."""

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        project_data = json.load(file)

    slides = [
        slide_from_dict(item)
        for item in project_data["slides"]
    ]

    global_defaults = defaults_from_dict(
        project_data["global_defaults"]
    )

    presentation = presentation_from_dict(
        project_data["presentation"]
    )

    return slides, global_defaults, presentation