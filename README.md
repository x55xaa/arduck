
# 📦 arduck

[![License: GPL v3](https://img.shields.io/badge/License-GPL_v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
![Python version: 3.12+](https://img.shields.io/badge/python-3.12+-blue)
[![Common Changelog](https://common-changelog.org/badge.svg)](https://common-changelog.org)


## Overview

This package offers an easy way to generate keystroke injection scripts. It supports a variety of [boards](https://docs.arduino.cc/language-reference/en/functions/usb/Keyboard/#Compatible%20Hardware) and [keyboard layouts](https://docs.arduino.cc/language-reference/en/functions/usb/Keyboard/keyboardBegin/#Keyboard%20layouts).

There is no need to get some overpriced usb stick to get the job done (rubberducky _cough cough_); just get an Arduino board that is compatible with the [Keyboard.h](https://docs.arduino.cc/language-reference/en/functions/usb/Keyboard) library, and you are good to go!


## Installation

Install the package from PyPI by running:

```bash
$ pip install arduck
```


## Usage

This package can be used as a library or through the `duck` console script. More information is present in the docs.


## A Word of Caution

Be careful when using and testing arduino scripts that emulate keyboard and mouse presses, because they might make it difficult to program your board.
And please, always ask for permission from the owner of the machine before plugging in any external devices. Keep in mind that, if abused, this tool has the potential to cause serious harm.

This software is distributed ‘as is’ and without warranties of any kind, either express or implied. Use of the software is at your own risk.


## Documentation

- [Official Documentation](https://x55xaa.github.io/arduck)
- [CHANGELOG](https://github.com/x55xaa/arduck/blob/main/CHANGELOG.md)
