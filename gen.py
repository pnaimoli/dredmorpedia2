#!/usr/local/bin/python3
from html.parser import HTMLParser
import jinja2
import os
import pdb
import pprint
import shutil
import xmltodict

DD_DIR = "/Users/peter/Library/Application Support/Steam/steamapps/common/Dungeons of Dredmor/Dungeons of Dredmor.app/Contents/MacOS"

IMAGE_PREFIX = "game_images/"

IMAGE_CORRECTION_MAP = {
        "dmg_asphyxiative_resist.png": "dmg_aphyxiative_resist.png",
        "dmg_asphyxiative.png": "dmg_aphyxiative.png",
        "dmg_blasting_resist.png": "dmg_blast_resist.png",
        "dmg_blasting.png": "dmg_blast.png",
        "dmg_necromantic_resist.png": "dmg_necromatic_resist.png",
        "dmg_necromantic.png": "dmg_necromatic.png",
        }

def write_first_sprite_frame(spr_infilename, png_outfilename):
    pass

def normalize_first_xml_sprite_name(xml_infilename):
    pass

def convert_xml_to_yaml(xml_infilename, yaml_outfilename):
    pass

def prepare_mod(directory):
    # Convert all xml files to yaml and copy them over
    # craftDB, monDB, itemDB, encrustDB, skillDB, and spellDB

    # Copy over all required images and sprite files, making sure everything
    # is a png file
    pass

def get_images(html):
    class MyParse(HTMLParser):
        def __init__(self, *args, **kwargs):
            self.images = set()
            super().__init__()

        def handle_starttag(self, tag, attrs):
            if tag=="img":
                self.images.add(dict(attrs)["src"])

    h=MyParse()
    h.feed(html)

    images = (img for img in h.images if img.startswith(IMAGE_PREFIX))

    return images

def copy_images(html):
    # Copy images over
    for dest_img in get_images(html):
        source = dest_img[len(IMAGE_PREFIX):]
        filename = os.path.basename(source) 

        # Some files are spelled wrong
        if filename in IMAGE_CORRECTION_MAP:
            source = os.path.join(os.path.dirname(source), IMAGE_CORRECTION_MAP[filename])

        # Some files are in the wrong place
        if not os.path.exists(os.path.join(DD_DIR, source)):
            source = source.split("/", 1)[-1]

        # Copy everything over!
        if not os.path.exists(os.path.dirname(dest_img)):
            os.makedirs(os.path.dirname(dest_img))
        shutil.copyfile(os.path.join(DD_DIR, source), dest_img)


def main():
    itemDBs = []
    for mod in [".", "expansion", "expansion2", "expansion3"]:
        with open(os.path.join(DD_DIR, mod, "game", "itemDB.xml")) as file_:
            itemDB = xmltodict.parse(file_.read())
            itemDB["mod_dir"] = mod
            itemDBs.append(itemDB)
    pp = pprint.PrettyPrinter(indent=1)
#    pp.pprint(itemDBs)

    # Templatize!!!
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."),
                                extensions=['jinja2.ext.loopcontrols'],
                                lstrip_blocks=True, trim_blocks=True)
    template = j2_env.get_template("index.html.j2")
    html = template.render(itemDBs=itemDBs)
    print(html)

    # Copy over all of the images
    copy_images(html)

if __name__ == "__main__":
    main()
