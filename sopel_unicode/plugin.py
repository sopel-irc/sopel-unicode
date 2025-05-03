"""
sopel-unicode

Plugin for information lookup on Unicode codepoints

Distributed under the Eiffel Forum License, version 2, see COPYING
"""
from __future__ import annotations
import logging
from typing import Iterable

from sopel import plugin
from sopel.config import types

from .impl import NAME_TO_CODEPOINT, describe_char, unicodedata


logger = logging.getLogger(__name__)

PREFIX = plugin.output_prefix('[unicode] ')


class SopelUnicodeSection(types.StaticSection):
    max_length = types.ValidatedAttribute('max_length', parse=int, default=5)
    """Maximum length of Unicode string input"""
    length_override_channels = types.ListAttribute('length_override_channels')
    """Channels where max_length does not apply"""
    ignore_characters = types.ListAttribute('ignore_characters', default=[" "])
    """Characters ignored during lookup"""
    search_max_matches = types.ValidatedAttribute('search_max_matches', parse=int, default=10)
    """Maximum number of matches for a codepoint search"""
    search_num_public_matches = types.ValidatedAttribute('search_num_public_matches', parse=int, default=2)
    """Number of matches publicly reported for a codepoint search"""


def configure(config):
    config.define_section('sopel_unicode', SopelUnicodeSection)
    config.sopel_unicode.configure_setting('max_length', 'How many codepoints maximum in an lookup string?')
    config.sopel_unicode.configure_setting('length_override_channels', 'Which channels should bypass the maximum input length? Leave blank for none.')


def setup(bot):
    bot.settings.define_section('sopel_unicode', SopelUnicodeSection)


def too_long(bot, trigger, s: str) -> bool:
    len_overrides = bot.config.sopel_unicode.length_override_channels
    max_len = bot.config.sopel_unicode.max_length

    effective_len = len(drop_uninteresting_chars(bot, s))

    # if the sender is a nick (DM), or an override channel, then it's never too long
    if not trigger.sender.is_nick() and trigger.sender not in len_overrides and effective_len > max_len:
        return True

    return False


def drop_uninteresting_chars(bot, s: str) -> str:
    drop_chars = bot.config.sopel_unicode.ignore_characters
    return "".join(c for c in s if c not in drop_chars)


@PREFIX
@plugin.commands("unicode:search", "u:search")
def unicode_search(bot, trigger):
    cmd = trigger.group(1)
    query = trigger.group(0)[len(cmd)+2:]

    MAX_MATCHES = bot.config.sopel_unicode.search_max_matches
    NUM_PUBLIC_MATCHES = bot.config.sopel_unicode.search_num_public_matches

    is_channel = trigger.sender and not trigger.sender.is_nick()

    matches = [(name, codepoint) for (name, codepoint) in NAME_TO_CODEPOINT.items() if all(term.casefold() in name.casefold() for term in query.split())]
    N_match = len(matches)
    if N_match == 0:
        bot.say("No results")
        return False

    bot.say(f"{N_match} results:")

    names, codepoints = zip(*matches)

    def _say_matches(matches: list[tuple[str, int]], dest=None):
        for (name, codepoint) in matches:
            bot.say(f"{chr(codepoint)} U+{codepoint:04x} {name}", destination=dest)

    if trigger.sender.is_nick():
        _say_matches(matches[:MAX_MATCHES])
        N_excess = N_match - MAX_MATCHES
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
    s = drop_uninteresting_chars(bot, s)

    prefix, rest = s[:2].lower(), s[2:]
    if prefix in ("u+", "0x", r"\u"):
        codept = int(rest.strip(), base=16)
        bot.say(describe_char(chr(codept)))
        return True

    if too_long(bot, trigger, s):
        bot.say(f"Too many input characters (max {bot.config.sopel_unicode.max_length})")
        return False

    if cmd.endswith(":noascii"):
        s = "".join(c for c in s if ord(c) not in range(128))

    for c in s:
        bot.say(describe_char(c))
    return True



@PREFIX
@plugin.commands("unicode:raw", "u:raw")
def summarize_raw(bot, trigger):
    s = trigger.group(2)

    for c in s:
        bot.say(describe_char(c))

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
    normalized = drop_uninteresting_chars(bot, normalized)

    if too_long(bot, trigger, normalized):
        bot.say(f"Can only decompose up to {bot.config.sopel_unicode.max_length} characters at a time")
        return False

    for char in normalized:
        msg = describe_char(char)
        bot.say(msg)
