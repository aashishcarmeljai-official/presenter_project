from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class SlideType(Enum):
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    BLANK = "blank"
    CUSTOM = "custom"


@dataclass
class Style:
    font_family: str = "Arial"
    font_size: int = 36
    font_color: str = "#FFFFFF"
    bold: bool = False
    italic: bool = False
    alignment: str = "center"


@dataclass
class ContentObject:
    content: str = ""
    style: Style = field(default_factory=Style)


@dataclass
class Background:
    image_path: str = ""
    brightness: int = 0
    contrast: int = 100


@dataclass
class Slide:
    id: str = field(default_factory=lambda: str(uuid4()))
    type: SlideType = SlideType.CUSTOM

    primary: ContentObject = field(default_factory=ContentObject)
    secondary: ContentObject = field(default_factory=ContentObject)

    background: Background = field(default_factory=Background)