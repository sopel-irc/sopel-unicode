# sopel-unicode

[Sopel] plugin for information lookup on Unicode codepoints.

This plugin is designed as a drop-in replacement for the built-in `unicode_info` plugin. It provides:

* The [General Category] of each codepoint
* Optional support for Unicode Character Database (UCD) versions newer than the Python release used to run Sopel, if [`unicodedata2`] is available
* Optional support for reporting the Unicode version that introduced each codepoint, if [`unicode_age`] is available

[Sopel]: https://pypi.org/project/sopel/
[General Category]: https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
[`unicodedata2`]: https://pypi.org/project/unicodedata2/
[`unicode_age`]: https://pypi.org/project/unicode-age/

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-unicode
```

### Disable built-in `unicode_info` plugin
<!-- TODO:SnoopJ: remove this section once the built-in is removed from the core. Tracking(ish) issue: https://github.com/sopel-irc/sopel/issues/1291 -->

You should edit your [Sopel core config] to add `unicode_info` to the [`exclude` plugin list], otherwise you will
get duplicated responses from both plugins.

[Sopel core config]: https://sopel.chat/docs/run/configuration
[`exclude` plugin list]: https://sopel.chat/docs/run/configuration#plugins

### Optional features

`sopel-unicode` is designed to act as a drop-in replacement for the original built-in plugin on a basic installation.
To enable all the optional features:

```shell
$ pip install sopel-unicode[all]
```
<!-- TODO:SnoopJ list and explain options for granular extras once CLDR is included -->

## Usage

Note that output given in this section corresponds to `sopel-unicode[all]` except where noted. Output layout may differ
if some optional dependencies are missing.

### Codepoint lookup

The `unicode` (short-form `u`) command provides lookup of codepoints in a provided string. Input characters defined by
the configuration option `ignore_chars` are ignored.

Lookup uses [`unicodedata2`] if it is available, and falls back on [stdlib `unicodedata`] otherwise.

[stdlib `unicodedata`]: https://docs.python.org/3/library/unicodedata.html

```
<SnoopJ> .unicode 🫩
<terribot> [unicode] (🫩): U+1FAE9 v16.0 (So) FACE WITH BAGS UNDER EYES
<SnoopJ> .u 🏴‍☠ 
<terribot> [unicode] (🏴): U+1F3F4 v7.0 (So) WAVING BLACK FLAG
<terribot> [unicode] (‍): U+200D v1.1 (Cf) ZERO WIDTH JOINER
<terribot> [unicode] (☠): U+2620 v1.1 (So) SKULL AND CROSSBONES
```

It is sometimes convenient to discard all ASCII characters from lookup, which can be done with the
`unicode:noascii`(`u:noascii`) command:

```
<SnoopJ> .u:noascii ça va?
<terribot> [unicode] (ç): U+00E7 v1.1 (Ll) LATIN SMALL LETTER C WITH CEDILLA
```

The `unicode:raw` (`u:raw`) command is provided to avoid discarding *any* codepoints when performing lookup.

```
<SnoopJ> .unicode:raw a b
<terribot> [unicode] (a): U+0061 v1.1 (Ll) LATIN SMALL LETTER A
<terribot> [unicode] ( ): U+0020 v1.1 (Zs) SPACE
<terribot> [unicode] (b): U+0062 v1.1 (Ll) LATIN SMALL LETTER B
```

Individual codepoints can also be looked up with hex notation, in either `U+NNNN` form, `0xNNNN` form, or `\uNNNN` form.

```
<SnoopJ> .unicode U+037E
<terribot> [unicode] (;): U+037E v1.1 (Po) GREEK QUESTION MARK
<SnoopJ> .u 0xBEEF
<terribot> [unicode] (뻯): U+BEEF v2.0 (Lo) HANGUL SYLLABLE BBEGS
<SnoopJ> .u \u732b
<terribot> [unicode] (猫): U+732B v1.1 (Lo) CJK UNIFIED IDEOGRAPH-732B
```

Note that the `\u` notation is *not restricted* in the same way as the same notation for Python literals. You may use as
many or as few hex digits as you like.

```
<SnoopJ> .u \u1
<terribot> [unicode] (): U+0001 v1.1 (Cc) START OF HEADING
<SnoopJ> .u \u12345
<terribot> [unicode] (𒍅): U+12345 v5.0 (Lo) CUNEIFORM SIGN URU TIMES KI
```

### Normalization forms

The [Unicode normalization forms] are available to transform input strings.

[Unicode normalization forms]: https://unicode.org/reports/tr15/

Input characters defined by the configuration option `ignore_chars` are ignored.

```
<SnoopJ> .unicode:NFKD ça va
<terribot> [unicode] (c): U+0063 v1.1 (Ll) LATIN SMALL LETTER C
<terribot> [unicode] (◌̧): U+0327 v1.1 (Mn) COMBINING CEDILLA
<terribot> [unicode] (a): U+0061 v1.1 (Ll) LATIN SMALL LETTER A
<terribot> [unicode] (v): U+0076 v1.1 (Ll) LATIN SMALL LETTER V
<terribot> [unicode] (a): U+0061 v1.1 (Ll) LATIN SMALL LETTER A
<SnoopJ> .u:NFKC ça va
<terribot> [unicode] (ç): U+00E7 v1.1 (Ll) LATIN SMALL LETTER C WITH CEDILLA
<terribot> [unicode] (a): U+0061 v1.1 (Ll) LATIN SMALL LETTER A
<terribot> [unicode] (v): U+0076 v1.1 (Ll) LATIN SMALL LETTER V
<terribot> [unicode] (a): U+0061 v1.1 (Ll) LATIN SMALL LETTER A
```

### Codepoint search

A rudimentary search functionality is available. The maximum number of matches reported can be configured, as many
queries produce a large number of results.

```
<SnoopJ> .unicode:search apple
<terribot> [unicode] 3 results:
<terribot> [unicode] 🍍 U+1f34d PINEAPPLE
<terribot> [unicode] 🍎 U+1f34e RED APPLE
<terribot> [unicode] 🍏 U+1f34f GREEN APPLE
```

## Configuring

The easiest way to configure `sopel-unicode` is via Sopel's configuration wizard—simply run
`sopel-plugins configure sopel-unicode` and enter the values for which it prompts you.

<!--[[[cog
from tools.config_attrdoc_helper import generate_config_table
from sopel_unicode.plugin import SopelUnicodeSection
import cog
for line in generate_config_table(SopelUnicodeSection): cog.outl(line)
]]]-->
| Field                       | Description                                                  | Default (if any)   |
| --------------------------- | ------------------------------------------------------------ | ------------------ |
| `max_length`                | Maximum length of Unicode string input                       | `5`                |
| `length_override_channels`  | Channels where max_length does not apply                     | `[]`               |
| `ignore_characters`         | Characters ignored during lookup                             | `[' ']`            |
| `search_max_matches`        | Maximum number of matches for a codepoint search             | `10`               |
| `search_num_public_matches` | Number of matches publicly reported for a codepoint search   | `2`                |
<!-- [[[end]]] -->
