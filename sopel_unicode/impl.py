from __future__ import annotations
import logging
import sys


logger = logging.getLogger(__name__)


try:
    import unicodedata2 as unicodedata
except ImportError:
    import unicodedata
    logger.warning(
        "Could not load unicodedata2, using built-in unicodedata. "
        "Unicode database will likely be out of date"
    )
    logger.debug("Exception details:", exc_info=True)


try:
    from unicode_age import version as unicode_version
except ImportError:
    def unicode_version(codept: int) -> tuple[int, int]:
        raise RuntimeError("Codepoint age functionality is not available")
    logger.warning(
        "Could not load unicode_age, codepoint UCD version information will not be available."
    )
    logger.debug("Exception details:", exc_info=True)


def isprintable(s: str) -> bool:
    """
    Replacement for str.isprintable() that supports a newer UCD
    """
    # NOTE: CPython Objects/unicodectype.c:_PyUnicode_IsPrintable() lists
    # all of the nonprintable categories explicitly, but the actual UCD flag
    # is set only in terms of the major category in Tools/unicode/makeunicodedata.py
    return all(unicodedata.category(c)[0] not in "CZ" for c in s)


def describe_char(char: str) -> str:
    codept = ord(char)
    notation = f"U+{codept:0>4x}".upper()
    category = unicodedata.category(char)
    try:
        major, minor = unicode_version(codept)
        ver_str = f"v{major}.{minor} "
    except RuntimeError:
        ver_str = ""

    try:
        char_sym, name = _char_name(char)
        if category.startswith('M'):
            char_sym = f"\N{DOTTED CIRCLE}{char_sym}"
        return f"({char_sym}): {notation} {ver_str}({category}) {name}"
    except ValueError:
        return f"No info for {notation} in Unicode {unicodedata.unidata_version}"


NAME_TO_CODEPOINT = {unicodedata.name(chr(n), ''): n for n in range(sys.maxunicode)}
NAME_TO_CODEPOINT.pop('')


def _char_name(char: str) -> tuple[str, str]:
    """
    Lookup the name of the given single-character string

    This is more complex than `unicodedata.name()` because many codepoints
    fall into ranges that may not be supported by the stdlib name functionality,
    especially in the case of newly-added ranges.

    TODO: is it possible to derive this information from UCD data files? Blocks.txt lists
    all block names but it isn't clear which ones need to be referred to this way. Is it
    okay to refer to an unfamiliar codepoint by the name of its block and some offset?
    """
    codept = ord(char)
    notation = f"U+{codept:0>4x}".upper()
    category = unicodedata.category(char)

    try:
        name = unicodedata.name(char)
    except ValueError:
        # NOTE:CPython's representation of the UCD does not account for the names of
        # some codepoints and will raise in some cases when a reasonable name can be
        # reported. This generally applies to entire contiguous blocks, so here we
        # test if the codepoint falls in one of these blocks
        if codept in UNICODE_V1_NAMES:
            name = UNICODE_V1_NAMES[codept]
        elif category == "Co":
            name = "PRIVATE USE AREA"
        elif codept in NPUA_HI_SURR:
            name = "NON PRIVATE USE HIGH SURROGATE"
        elif codept in PUA_HI_SURR:
            name = "PRIVATE USE HIGH SURROGATE"
        elif codept in LO_SURR:
            name = "LOW SURROGATE"
        elif codept in TANGUT_IDEO or codept in TANGUT_IDEO_SUPP:
            name = "TANGUT IDEOGRAPH-" + notation[2:]
        else:
            name = "<NO NAME>"

    return char, name


UNICODE_V1_NAMES = {
    0x0000: "NULL",
    0x0001: "START OF HEADING",
    0x0002: "START OF TEXT",
    0x0003: "END OF TEXT",
    0x0004: "END OF TRANSMISSION",
    0x0005: "ENQUIRY",
    0x0006: "ACKNOWLEDGE",
    0x0007: "BELL",
    0x0008: "BACKSPACE",
    0x0009: "CHARACTER TABULATION",
    0x000A: "LINE FEED (LF)",
    0x000B: "LINE TABULATION",
    0x000C: "FORM FEED (FF)",
    0x000D: "CARRIAGE RETURN (CR)",
    0x000E: "SHIFT OUT",
    0x000F: "SHIFT IN",
    0x0010: "DATA LINK ESCAPE",
    0x0011: "DEVICE CONTROL ONE",
    0x0012: "DEVICE CONTROL TWO",
    0x0013: "DEVICE CONTROL THREE",
    0x0014: "DEVICE CONTROL FOUR",
    0x0015: "NEGATIVE ACKNOWLEDGE",
    0x0016: "SYNCHRONOUS IDLE",
    0x0017: "END OF TRANSMISSION BLOCK",
    0x0018: "CANCEL",
    0x0019: "END OF MEDIUM",
    0x001A: "SUBSTITUTE",
    0x001B: "ESCAPE",
    0x001C: "INFORMATION SEPARATOR FOUR",
    0x001D: "INFORMATION SEPARATOR THREE",
    0x001E: "INFORMATION SEPARATOR TWO",
    0x001F: "INFORMATION SEPARATOR ONE",
    0x007F: "DELETE",
    0x0082: "BREAK PERMITTED HERE",
    0x0083: "NO BREAK HERE",
    0x0085: "NEXT LINE (NEL)",
    0x0086: "START OF SELECTED AREA",
    0x0087: "END OF SELECTED AREA",
    0x0088: "CHARACTER TABULATION SET",
    0x0089: "CHARACTER TABULATION WITH JUSTIFICATION",
    0x008A: "LINE TABULATION SET",
    0x008B: "PARTIAL LINE FORWARD",
    0x008C: "PARTIAL LINE BACKWARD",
    0x008D: "REVERSE LINE FEED",
    0x008E: "SINGLE SHIFT TWO",
    0x008F: "SINGLE SHIFT THREE",
    0x0090: "DEVICE CONTROL STRING",
    0x0091: "PRIVATE USE ONE",
    0x0092: "PRIVATE USE TWO",
    0x0093: "SET TRANSMIT STATE",
    0x0094: "CANCEL CHARACTER",
    0x0095: "MESSAGE WAITING",
    0x0096: "START OF GUARDED AREA",
    0x0097: "END OF GUARDED AREA",
    0x0098: "START OF STRING",
    0x009A: "SINGLE CHARACTER INTRODUCER",
    0x009B: "CONTROL SEQUENCE INTRODUCER",
    0x009C: "STRING TERMINATOR",
    0x009D: "OPERATING SYSTEM COMMAND",
    0x009E: "PRIVACY MESSAGE",
    0x009F: "APPLICATION PROGRAM COMMAND",
}

NPUA_HI_SURR = range(0xD800, 0xDB74 + 1)  # Non Private Use High Surrogate
PUA_HI_SURR = range(0xDB80, 0xDBFF + 1)  # Private Use High Surrogate
LO_SURR = range(0xDC00, 0xDFFF + 1)  # Low Surrogate

TANGUT_IDEO = range(0x17000, 0x187F7 + 1)  # TANGUT IDEOGRAPH-N
TANGUT_IDEO_SUPP = range(0x18D00, 0x18D08 + 1)  # TANGUT IDEOGRAPH-N

