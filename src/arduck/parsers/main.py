"""Main argument parser module."""

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


from argparse import (
    ArgumentParser, FileType, Namespace,
)
from collections.abc import Sequence
import itertools
import logging
from typing import Optional, override

from ..arduino.keyboard import LAYOUTS
from ..modules import metadata
from ..modules.parsing.parsers import MainArgumentParserTemplate
from . import types


logger = logging.getLogger(__name__)


def _construct() -> ArgumentParser:
    """Returns an instance of the module's argument parser.

    Invoked by the `argparse` directive in the docs.
    For more information, see https://sphinx-argparse.readthedocs.io/en/stable.
    """

    return MainArgumentParser()


class MainArgumentParser(MainArgumentParserTemplate):
    """Handles the arguments that get passed to the package when its invoked
    directly from the command line (python -m package_name ...).
    """

    @override
    def __init__(self):
        super().__init__(
            prog=metadata.package(),
            description=metadata.summary(),
            prefix_chars='-',
        )

    def _extend_arguments(self) -> None:
        default_keyboard_layout: str = 'us'

        self.add_argument(
            'keystrokes',
            action='store',
            help='sequence of keystrokes with optional delays between them',
            metavar='string | delay',
            nargs='+',
            type=types.key_or_delay,
        )

        self.add_argument(
            '-l', '--layout',
            action='store',
            choices=LAYOUTS.keys(),
            default=default_keyboard_layout,
            help=f'keyboard layout (default: {default_keyboard_layout})',
            type=types.keyboard_layout,
        )

        self.add_argument(
            '-w', '--wpm',
            action='store',
            default=0,
            help=(
                'the average speed at which characters are typed, in words per '
                'minute. A value of zero will add no delay between keystrokes (default)'
            ),
            type=types.words_per_minute,
        )

        self.add_argument(
            '-o', '--outfile',
            action='store',
            default=open('sketch.ino', 'w+'),
            help='the output file (default=sketch.ino)',
            metavar='path',
            required=False,
            type=FileType('w+', encoding='utf-8'),
        )

    def _extend_subparsers(self) -> None:
        pass

    @override
    def parse_args(
            self,
            args: Optional[Sequence[str]] = None,
            namespace: Optional[Namespace] = None
    ) -> Namespace:

        namespace = super().parse_args(args=args, namespace=namespace)

        namespace.keystrokes = list(itertools.chain(*namespace.keystrokes))

        # inclusion in the choices sequence is checked after any type conversions have been performed.
        namespace.layout = LAYOUTS[namespace.layout]

        return namespace
