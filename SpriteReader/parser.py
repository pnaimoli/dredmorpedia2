#!/usr/bin/env python3
import PIL.Image
import struct
import sys
import unittest

# https://www.cosmigo.com/promotion/docs/onlinehelp/TechnicalInfos.htm

def read(spr_filename):
    images = []
    with open(spr_filename, "rb") as f:
        # Read the header:
        # 0-2: "SPR"
        # 3-4: # of frames
        # 5-6: width
        # 7-8: height
        (magic_1, magic_2, magic_3, frames, width, height) = struct.unpack("<3chhh", f.read(9))
        if (magic_1, magic_2, magic_3) != (b"S", b"P", b"R"):
            raise ValueError("First 3 bytes of {} must be 'SPR'".format(spr_filename))

        # Read the frame:
        # 0-1: delay in ms
        # next 768 bytes: color palette
        # next width*height bytes: color data
        for i in range(frames):
            delay = struct.unpack("<h", f.read(2))[0]
            palette = struct.unpack("768B", f.read(768))
            data_bytes = width*height
            data = struct.unpack(str(data_bytes)+"B", f.read(data_bytes))
            img = PIL.Image.new(mode="P", size=(width, height), color=None)
            img.putpalette(palette)
            img.putdata(data)

            # There's some magic here - the 0th color palette index is
            # the "transparent" color
            transp_pix = palette[0:3]
            img = img.convert("RGBA")
            pixdata = img.load()
            for y in range(height):
                for x in range(width):
                    if pixdata[x, y][0:3] == transp_pix:
                        pixdata[x, y] = transp_pix + (0,)

            images.append(img)

        # We should have reached the end of the file
        if f.read(1) != b"":
            raise ValueError("Unexpected frame found")

    return images

###############################################################################
# Begin unit tests
###############################################################################

class SpriteReaderTest(unittest.TestCase): # pylint: disable=missing-docstring
    def test_read(self):
        images = read("test.spr")
        self.assertEqual(len(images), 6)
        for img in images:
            self.assertEqual(img.size, (64, 64))
