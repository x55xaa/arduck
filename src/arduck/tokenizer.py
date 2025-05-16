"""Tokenizer that transforms a string into a series of key inputs."""

# Copyright (C) 2025  Stefano Cuizza

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


from itertools import takewhile
import re
from typing import NamedTuple

from .arduino.keyboard import SPECIAL_KEYS


type RawKeystroke = str | tuple[str, ...]


SPECIAL_CHARACTERS: tuple[str, ...] = ('\t', '\n', '\r', '\f', '\v')
TOKENS: dict[str, str] = {
    'COMBO': r'<([A-Z_]+|[^A-Z])(?:\+([A-Z_]+|[^A-Z]))*>',
    'CHARACTER': r'(.)',
}
"""Recognized tokens."""


class Token(NamedTuple):
    """Represents a character of a sequence of characters."""

    type: str
    value: str


def to_keystrokes(string: str) -> list[RawKeystroke]:
    """Transforms a string of characters into a sequence of key presses.

    ==============
    Interpretation
    ==============

    Combos should have this form: <CONSTANT_or_single_key+...>.
    All other characters including line termination characters are interpreted as
    one character. All occurrences of two or more uppercase letters get enclosed
    in `KEY_CAPS_LOCK` key presses.


    ===========
    Translation
    ===========

    Keys that are supposed to be pressed at the same time are stored in tuples.
    Keys that are more than one letter long are special constants defined by the
    `Keyboard.h` library, and should be interpreted as such.
    """

    result: list[RawKeystroke] = []

    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS.items())
    for match in re.finditer(token_regex, string, flags=re.S):
        groups = match.groups()

        match match.lastgroup:
            case 'CHARACTER':
                result.append(groups[-1])
            case 'COMBO':
                result.append(tuple(filter(lambda i: i, groups[1:])))

    i: int = 0
    while i < len(result):
        key = result[i]

        if isinstance(key, tuple):
            i += 1
            continue

        if key.isupper():
            word = tuple(takewhile(
                lambda c: not c.islower() and c not in SPECIAL_CHARACTERS,
                result[i:],
            ))

            if len(word) > 1:
                for j in range(len(word)):
                    result[i + j] = result[i + j].lower()

                result.insert(i, SPECIAL_KEYS['CAPS_LOCK'])
                result.insert(i + len(word) + 1, SPECIAL_KEYS['CAPS_LOCK'])

                i += len(word)

        i += 1

    return result
