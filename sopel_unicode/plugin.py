from __future__ import annotations
import logging
from typing import Iterable

from sopel import plugin
from sopel.config import types

from .impl import describe_char, unicodedata


logger = logging.getLogger(__name__)

MAX_LEN = 16
PREFIX = plugin.output_prefix('[unicode] ')


class SopelUnicodeSection(types.StaticSection):
    max_length = types.ValidatedAttribute('max_length', parse=int, default=5)
    """Maximum length of Unicode string input"""
    length_override_channels = types.ListAttribute('length_override_channels')
    """Channels where max_length does not apply"""


def setup(bot):
    bot.settings.define_section('sopel_unicode', SopelUnicodeSection)


def too_long(bot, trigger, s: str) -> bool:
    len_overrides = bot.config.sopel_unicode.length_override_channels
    max_len = bot.config.sopel_unicode.max_length

    effective_len = len(drop_uninteresting_chars(s))

    # if the sender is a nick (DM), or an override channel, then it's never too long
    if not trigger.sender.is_nick() and trigger.sender not in len_overrides and effective_len > max_len:
        return True

    return False


def drop_uninteresting_chars(s: str) -> str:
    # TODO: allow users to define uninteresting chars
    UNINTERESTING = (" ",)

    return "".join(c for c in s if c not in UNINTERESTING)


@PREFIX
@plugin.commands("unicode:search", "u:search")
def unicode_search(bot, trigger):
    cmd = trigger.group(1)
    s = trigger.group(0)[len(cmd)+2:].replace(" ", "")
    s = drop_uninteresting_chars(s)

    MAX_MATCHES = 10
    NUM_PUBLIC_MATCHES = 2

    is_channel = trigger.sender and not trigger.sender.is_nick()

    matches = [(name, codepoint) for (name, codepoint) in NAME_TO_CODEPOINT.items() if all(term.casefold() in name.casefold() for term in query.split())]
    N_match = len(matches)
    if N_match == 0:
        bot.say("No results")
        return False
    elif is_channel and N_match > MAX_MATCHES:
        bot.say(f"Maximum number of results ({MAX_MATCHES}) exceeded, got {N_match}, giving up")
        return False
    else:
        bot.say(f"{N_match} results:")

    names, codepoints = zip(*matches)

    def _say_matches(matches: list[tuple[str, int]], dest=None):
        for (name, codepoint) in matches:
            bot.say(f"{chr(codepoint)} U+{codepoint:04x} {name}", destination=dest)

    if trigger.sender.is_nick():
        _say_matches(matches)
    else:
        _say_matches(matches[:NUM_PUBLIC_MATCHES])

        N_excess = N_match - NUM_PUBLIC_MATCHES
        if N_excess > 0:
            bot.say(f"{N_excess} other results")


# TODO: special handling for ZWJ sequences?
@PREFIX
@plugin.commands("unicode", "u", "unicode:noascii", "u:noascii")
def unicode_summarize(bot, trigger):
    cmd = trigger.group(1)
    s = trigger.group(2)

    prefix, rest = s[:2].lower(), s[2:]
    if prefix in ("u+", "0x", r"\u"):
        codept = int(rest.strip(), base=16)
        bot.say(describe_char(chr(codept)))
        return True

    if too_long(bot, trigger, s):
        bot.say(f"Whoa now, that's too many characters, hoss (max {bot.config.sopel_unicode.max_length})")
        return False

    if cmd.endswith(":noascii"):
        s = "".join(c for c in s if ord(c) not in range(128))

    for c in s:
        bot.say(describe_char(c))
    return True



@PREFIX
@plugin.commands(
    "unicode:NFC",
    "unicode:NFD",
    "unicode:NFKC",
    "unicode:NFKD",
    "u:NFC",
    "u:NFD",
    "u:NFKC",
    "u:NFKD",
)
def normalized_forms(bot, trigger):
    *_, form = trigger.group(1).partition(":")
    s = trigger.group(2)

    normalized = unicodedata.normalize(form.upper(), s)
    normalized = drop_uninteresting_chars(normalized)

    if too_long(bot, trigger, normalized):
        bot.say(f"Can only decompose up to {bot.config.sopel_unicode.max_length} characters at a time")
        return False

    for char in normalized:
        msg = describe_char(char)
        bot.say(msg)
