from dataclasses import dataclass, field
from enum import Enum
from typing import List

from models import Slide, SlideType


class SequenceToken(Enum):
    """
    An item that can be inserted into a presentation section.
    """

    VERSE_N = "Verse N"
    VERSE = "Verse"
    CHORUS = "Chorus"
    BRIDGE = "Bridge"
    BLANK = "Blank"
    CUSTOM = "Custom"


@dataclass
class SequenceItem:
    """
    One instruction inside Beginning/Main/End.

    Examples:

        Verse N
        Chorus
        Verse 1
        Blank
    """

    token: str


@dataclass
class PresentationSection:
    """
    One section of the worship presentation.

    Example:

        Main
        [
            Verse N,
            Chorus
        ]
    """

    name: str
    items: List[SequenceItem] = field(
        default_factory=list
    )


@dataclass
class Presentation:
    """
    Complete worship presentation.

    Beginning -> Main -> End
    """

    beginning: PresentationSection = field(
        default_factory=lambda:
        PresentationSection("Beginning")
    )

    main: PresentationSection = field(
        default_factory=lambda:
        PresentationSection("Main")
    )

    end: PresentationSection = field(
        default_factory=lambda:
        PresentationSection("End")
    )


class SequenceResolver:

    def __init__(self, slides: List[Slide]):
        self.slides = slides

    # =========================================================
    # RESOLVE COMPLETE PRESENTATION
    # =========================================================

    def resolve_presentation(
        self,
        presentation: Presentation,
    ) -> List[Slide]:

        result = []

        result.extend(
            self.resolve_section(
                presentation.beginning
            )
        )

        result.extend(
            self.resolve_section(
                presentation.main
            )
        )

        result.extend(
            self.resolve_section(
                presentation.end
            )
        )

        return result

    # =========================================================
    # RESOLVE SECTION
    # =========================================================

    def resolve_section(
        self,
        section: PresentationSection,
    ) -> List[Slide]:

        result = []

        i = 0

        while i < len(section.items):

            item = section.items[i]

            # =====================================================
            # VERSE N + FOLLOWING ITEM = REPEATING PATTERN
            # =====================================================

            if item.token.strip().lower() == "verse n":

                verses = self._get_verses()

                # The item immediately after Verse N is the
                # repeated companion item.
                companion = None

                if i + 1 < len(section.items):

                    companion = section.items[i + 1]

                # Repeat the pattern for every verse
                for _, verse_slide in verses:

                    # Add current verse
                    result.append(
                        verse_slide
                    )

                    # Add companion
                    if companion is not None:

                        result.extend(
                            self.resolve_item(
                                companion
                            )
                        )

                # We already consumed the companion,
                # so skip over it.
                if companion is not None:
                    i += 2
                else:
                    i += 1

                continue

            # =====================================================
            # NORMAL ITEM
            # =====================================================

            result.extend(
                self.resolve_item(item)
            )

            i += 1

        return result

    # =========================================================
    # RESOLVE ITEM
    # =========================================================

    def resolve_item(
        self,
        item: SequenceItem,
    ) -> List[Slide]:

        token = item.token.strip()

        # -----------------------------------------------------
        # Verse N
        # -----------------------------------------------------

        if token.lower() == "verse n":

            return self._resolve_all_verses()

        # -----------------------------------------------------
        # Explicit Verse number
        # -----------------------------------------------------

        if token.lower().startswith("verse "):

            number_text = token[6:].strip()

            if number_text.isdigit():

                number = int(number_text)

                return self._resolve_verse(
                    number
                )

        # -----------------------------------------------------
        # Chorus
        # -----------------------------------------------------

        if token.lower() == "chorus":

            return self._find_type(
                SlideType.CHORUS
            )

        # -----------------------------------------------------
        # Bridge
        # -----------------------------------------------------

        if token.lower() == "bridge":

            return self._find_type(
                SlideType.BRIDGE
            )

        # -----------------------------------------------------
        # Blank
        # -----------------------------------------------------

        if token.lower() == "blank":

            return self._find_type(
                SlideType.BLANK
            )

        # -----------------------------------------------------
        # Custom
        # -----------------------------------------------------

        return self._find_custom(
            token
        )

    # =========================================================
    # VERSES
    # =========================================================

    def _resolve_all_verses(self):

        verses = self._get_verses()

        result = []

        for _, slide in verses:

            result.append(slide)

        return result

    def _resolve_verse(
        self,
        number: int,
    ):

        verses = self._get_verses()

        for verse_number, slide in verses:

            if verse_number == number:

                return [slide]

        return []

    def _get_verses(self):

        """
        Find all slides whose type is VERSE.

        They are numbered according to their order
        in the slide list.
        """

        result = []

        verse_number = 1

        for slide in self.slides:

            if slide.type == SlideType.VERSE:

                result.append(
                    (
                        verse_number,
                        slide,
                    )
                )

                verse_number += 1

        return result

    # =========================================================
    # STANDARD TYPES
    # =========================================================

    def _find_type(
        self,
        slide_type: SlideType,
    ):

        for slide in self.slides:

            if slide.type == slide_type:

                return [slide]

        return []

    # =========================================================
    # CUSTOM
    # =========================================================

    def _find_custom(
        self,
        token: str,
    ):

        token_lower = token.lower()

        for slide in self.slides:

            # Match slide ID
            if slide.id.lower() == token_lower:

                return [slide]

        return []


# =============================================================
# HELPER
# =============================================================

def available_sequence_tokens(
    slides: List[Slide],
) -> List[str]:

    tokens = [
        "Verse N",
        "Chorus",
        "Bridge",
        "Blank",
    ]

    verse_count = sum(
        1
        for slide in slides
        if slide.type == SlideType.VERSE
    )

    for number in range(
        1,
        verse_count + 1,
    ):

        tokens.append(
            f"Verse {number}"
        )

    return tokens