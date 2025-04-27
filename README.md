# sopel-unicode

[Sopel] plugin for information lookup on Unicode codepoints.

This plugin is designed as a drop-in replacement for the built-in `unicode_info` plugin.

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

### Optional features

`sopel-unicode` is designed to act as a drop-in replacement for the original built-in plugin on a basic installation.
To enable all the optional features:

```shell
$ pip install sopel-unicode[all]
```

<!-- TODO:SnoopJ list and explain options for granular extras once CLDR is included -->

## Configuring

The easiest way to configure `sopel-unicode` is via Sopel's
configuration wizard—simply run `sopel-plugins configure sopel-unicode`
and enter the values for which it prompts you.
