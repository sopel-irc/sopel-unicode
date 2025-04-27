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

