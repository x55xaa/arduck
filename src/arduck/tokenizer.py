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
type Keystroke = str
type SleepInterval = int


FORBIDDEN_CHARACTERS: tuple[str, ...] = ('\t', '\n', '\r', '\f', '\v')
TOKENS: dict[str, str] = {
    'COMBO': r'<([A-Z_]+|[^A-Z])(?:\+([A-Z_]+|[^A-Z]))*>',
    'CHARACTER': r'(.)',
}
"""Recognized tokens."""


class Token(NamedTuple):
    """Represents a character of a sequence of characters."""

    type: str
    value: str


def _is_part_of_uppercase_word(c: str) -> bool:
    return (
        not c.islower() and c not in FORBIDDEN_CHARACTERS and len(c) == 1
    )


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
                combo = list(filter(lambda k: k, groups[1:]))

                # handle abbreviated special keys.
                for i, key in enumerate(combo.copy()):
                    if len(key) > 1:
                        combo[i] = SPECIAL_KEYS.get(combo[i], combo[i])

                # flatten one character combos.
                if len(combo) > 1:
                    result.append(tuple(combo))
                else:
                    result.extend(combo)

    i: int = 0
    while i < len(result):
        key = result[i]

        if isinstance(key, tuple):
            i += 1
            continue

        # simulate the use of the `KEY_CAPS_LOCK` key with sequences of
        # uppercase characters that are longer than two letters.
        if key.isupper():
            word = tuple(takewhile(_is_part_of_uppercase_word, result[i:]))

            if len(word) > 1:
                for j in range(len(word)):
                    result[i + j] = result[i + j].lower()

                result.insert(i, SPECIAL_KEYS['CAPS_LOCK'])
                result.insert(i + len(word) + 1, SPECIAL_KEYS['CAPS_LOCK'])

                i += len(word)

        i += 1

    return result


def merge_delays(keystrokes: list[RawKeystroke]) -> list[RawKeystroke]:
    """Merges adjacent delays."""

    result: list[RawKeystroke] = []

    i: int = 0
    while i < len(keystrokes):
        raw_key = keystrokes[i]

        if isinstance(raw_key, str) or isinstance(raw_key, tuple):
            result.append(raw_key)

            i += 1
            continue

        consecutive_delays = tuple(
            takewhile(lambda j: isinstance(j, int), keystrokes[i:])
        )

        result.append(sum(consecutive_delays))
        i += len(consecutive_delays)

    return result


def keystrokes_to_arrays(keystrokes: list[RawKeystroke]) -> tuple[list[Keystroke], list[tuple[int, SleepInterval]]]:
    """Translates a sequence of raw keystrokes into an array of keystrokes and
    a sleep interval mapping.


    ========
    Examples
    ========

    The following sequence:
        [('LEFT_GUI', 'r'), 'c', 'm', 'd', '\n', 200, 'l', 's', '\n']
    Gets translated to:
        ['\0', 'LEFT_GUI', 'r', '\0', 'c', 'm', 'd', '\n', 'l', 's', '\n']
        [(6, 200)]
    """

    keys: list[Keystroke] = []
    interval_mapping: list[tuple[int, SleepInterval]] = []

    shift_correction: int = 0
    for i, raw_key in enumerate(keystrokes):
        if isinstance(raw_key, int):
            interval_mapping.append((i + shift_correction, raw_key))
            shift_correction -= 1

        elif isinstance(raw_key, str):
            keys.append(raw_key)

        elif isinstance(raw_key, tuple):
            keys.extend(('\0', *raw_key, '\0'))
            shift_correction += 3

    return keys, interval_mapping
