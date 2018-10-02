#!/usr/local/bin/python3
from html.parser import HTMLParser
import jinja2
import os
import pdb
import pprint
import shutil
import xmltodict

PP = pprint.PrettyPrinter(indent=1)

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

WEAPON_TYPES = {
    0: "SWORD",
    1: "AXE",
    2: "MACE",
    3: "STAFF",
    4: "BOW",
    5: "THROWN",
    6: "BOLT",
    7: "DAGGER",
    8: "POLEARM",
}

PRIMARY_STATS = {
    0: "burliness",
    1: "sagacity",
    2: "nimbleness",
    3: "caddishness",
    4: "stubborness",
    5: "savvy",
}

SECONDARY_STATS = {
    0:  ("life", "Life"),
    1:  ("mana", "Mana"),
    2:  ("meleepower", "Melee Power"),
    3:  ("magicpower", "Magic Power"),
    4:  ("crit", "Crit"),
    5:  ("haywire", "Haywire"),
    6:  ("dodge", "Dodge"),
    7:  ("block", "Block"),
    8:  ("counter", "Counter"),
    9:  ("edr", "Enemy Dodge Reduction"),
    10: ("armourabsorption", "Armour Absorption"),
    11: ("magicresistance", "Magic Resistance"),
    12: ("sneakiness", "Sneakiness"),
    13: ("liferegen", "Life Regen"),
    14: ("manaregen", "Mana Regen"),
    15: ("wandburn", "Wand Affinity"),
    16: ("traplevel", "Trap Affinity"),
    17: ("trapsense", "Trap Sight Radius"),
    18: ("sight", "Sight Radius"),
    19: ("smithing", "Smithing"),
    20: ("tinkerer", "Tinkering"),
    21: ("alchemy", "Alchemy"),
    22: ("reflection", "Magic Reflection"),
    23: ("wandburn", "Wand Crafting"),
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

def change_dict_naming_convention(d, convert_function):
    """
    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        convert_function (func): function that takes the string in one convention and returns it in the other one.
    Returns:
        Dictionary with the new keys.
    """
    new = {}
    for k, v in d.items():
        new_v = v
        if isinstance(v, dict):
            new_v = change_dict_naming_convention(v, convert_function)
        elif isinstance(v, list):
            new_v = list()
            for x in v:
                new_v.append(change_dict_naming_convention(x, convert_function))
        new[convert_function(k)] = new_v
    return new

def normalize_key(key_str):
    if key_str.startswith("@"):
        return key_str[1:].lower()
    else:
        return key_str.lower()

def main():
    itemDBs = []
    for mod in [".", "expansion", "expansion2", "expansion3"]:
        with open(os.path.join(DD_DIR, mod, "game", "itemDB.xml")) as file_:
            itemDB = xmltodict.parse(file_.read())
            itemDB["mod_dir"] = mod

            # Make all keys lowercase
            itemDB = change_dict_naming_convention(itemDB, normalize_key)

            # Make primary/secondarybuff always a list even if there's only one
            for item in itemDB["itemdb"]["item"]:
                if "primarybuff" in item:
                    if not isinstance(item["primarybuff"], list):
                        item["primarybuff"] = [item["primarybuff"]]
                if "secondarybuff" in item:
                    if not isinstance(item["secondarybuff"], list):
                        item["secondarybuff"] = [item["secondarybuff"]]

            itemDBs.append(itemDB)

#    PP.pprint(itemDBs)

    # Templatize!!!
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."),
                                extensions=['jinja2.ext.loopcontrols'],
                                lstrip_blocks=True, trim_blocks=True)
    template = j2_env.get_template("index.html.j2")
    html = template.render(itemDBs=itemDBs,
                           PRIMARY_STATS=PRIMARY_STATS,
                           SECONDARY_STATS=SECONDARY_STATS)
    print(html)

    # Copy over all of the images
    copy_images(html)

if __name__ == "__main__":
    main()
