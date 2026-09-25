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
    case: str = "normal"


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

    # When False, this slide's text formatting is not stored on the slide
    # itself -- it always mirrors whatever GlobalDefaults.primary_style /
    # secondary_style currently holds. When True, the slide uses its own
    # primary.style / secondary.style instead.
    use_custom_style: bool = False

    # Same idea as use_custom_style, but for the background (image path,
    # brightness, contrast).
    use_custom_background: bool = False


@dataclass
class GlobalDefaults:
    """The shared 'theme' every non-customized slide follows.

    Any slide with use_custom_style=False renders using primary_style /
    secondary_style from here. Any slide with use_custom_background=False
    renders using `background` from here. Changing these values updates
    every non-customized slide immediately, since they all read from this
    same shared object.
    """

    primary_style: Style = field(default_factory=lambda: Style(font_size=36))
    secondary_style: Style = field(default_factory=lambda: Style(font_size=30))
    background: Background = field(default_factory=Background)