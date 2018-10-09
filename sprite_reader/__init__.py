#!/usr/bin/env python3
"""Convert Cosmigo Pro Motion SPR parser.

This module takes a .spr created by Cosmigo Pro Motion and parses out
the individual frames.  Useful for games like Dungeons of Dredmor.

See
https://www.cosmigo.com/promotion/docs/onlinehelp/TechnicalInfos.htm
for information on this file format

Usage:
    sprite_reader.read("file.spr")

"""

from .parser import read
