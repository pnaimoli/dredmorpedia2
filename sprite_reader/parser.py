#!/usr/bin/env python3
# pylint: disable=missing-docstring
import struct
import unittest
import PIL.Image

def read(spr_filename):
    """Read in a .spr file and returns the individual frames.

    Args:
        spr_filename (str): The path to the .spr file

    Returns:
        (:obj:`list` of :obj:`PIL.Image`): List of Pillow Images - one for each frame.

    """
    images = []
    with open(spr_filename, "rb") as file:
        # Read the header:
        # 0-2: "SPR"
        # 3-4: # of frames
        # 5-6: width
        # 7-8: height
        if struct.unpack("<3c", file.read(3)) != (b"S", b"P", b"R"):
            raise ValueError("First 3 bytes of {} must be 'SPR'".format(spr_filename))
        (frames, width, height) = struct.unpack("<3h", file.read(6))

        # Read the frame:
        # 0-1: delay in ms
        # next 768 bytes: color palette
        # next width*height bytes: color data
        for _ in range(frames):
            # delay - don't care about this
            file.read(2) # delay = struct.unpack("<h", file.read(2))[0]
            palette = struct.unpack("768B", file.read(768))
            data_bytes = width*height
            data = struct.unpack(str(data_bytes)+"B", file.read(data_bytes))
            img = PIL.Image.new(mode="P", size=(width, height), color=None)
            img.putpalette(palette)
            img.putdata(data)

            # There's some magic here - the 0th color palette index is
            # the "transparent" color.  Is this Dungeons of Dredmor specific?
            transp_pix = palette[0:3]
            img = img.convert("RGBA")
            pixdata = img.load()
            for y_pixel in range(height):
                for x_pixel in range(width):
                    if pixdata[x_pixel, y_pixel][0:3] == transp_pix:
                        pixdata[x_pixel, y_pixel] = transp_pix + (0,)

            images.append(img)

        # We should have reached the end of the file
        if file.read(1) != b"":
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
