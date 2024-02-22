import argparse
import config
import json
import os
import re
import sys
import util

from abc import ABC
from enum import StrEnum
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, WARNING

logger = getLogger(__name__)
handler = StreamHandler()
handler.setFormatter(
    Formatter(
        "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"
    )
)
logger.addHandler(handler)


DESCRIPTION_SEPARATOR = "―――――――――――――"


class Category(StrEnum):
    ITEM = "アイテム"
    WEAPON = "武器"
    ARMOR = "防具"
    CARD = "カード"
    SHADOW = "シャドウ"
    ENCHANT = "エンチャント"
    COSTUME = "衣装"
    AMMUNITION = "弾薬"
    PET = "ペット系"


class Gear(StrEnum):
    HEADGEAR = "兜"
    ARMOR = "鎧"
    WEAPON = "武器"
    SHIELD = "盾"
    GARMENT = "肩にかける物"
    SHOES = "靴"
    ACCESSORY = "アクセサリー"
    ALL = "全ての部位"

    @staticmethod
    def value_of(value):
        try:
            return Gear(value)
        except:
            garments = ["肩にかけるもの", "肩に掛けるもの"]
            if value in garments:
                return Gear.GARMENT


class RoObject(ABC):
    def __init__(self, id: int, name: str, description: list[str]) -> None:
        self.id: int = id
        self.name: str = name
        self.description: list[str] = description


class Enchant(RoObject):
    def __init__(self, id: int, name: str, description: list[str]) -> None:
        super().__init__(id, name, description)
        self.category = Category.ENCHANT


class Item(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.ITEM
        self.weight = float(util.get_parameter_value(specs, "重量"))


class Card(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.CARD
        self.weight = float(util.get_parameter_value(specs, "重量"))
        self.location = Gear.value_of(util.get_parameter_value(specs, "装備"))
        if util.exist_parameter(specs, "装着"):
            self.location = Gear.value_of(util.get_parameter_value(specs, "装着"))
        self.prefix = ""
        self.postfix = ""


class Weapon(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.WEAPON
        self.type = util.get_parameter_value(specs, "系列")
        self.attack = int(util.get_parameter_value(specs, "攻撃", 0))
        if util.exist_parameter(specs, "Atk"):
            self.attack = int(util.get_parameter_value(specs, "Atk"))
        self.weight = float(util.get_parameter_value(specs, "重量"))
        self.weapon_level = int(util.get_parameter_value(specs, "武器レベル"))
        v = util.get_parameter_value(specs, "要求レベル")
        self.required_level = int(1 if v in [None, "無し", "なし"] else v)
        self.equippable = util.get_parameter_value(specs, "装備").split(" ")
        self.magic_attack = int(util.get_parameter_value(specs, "Matk", 0))
        for line in description:
            r = re.match("^Matk \+ (\d)+$", line)
            if r:
                self.magic_attack = int(r.group(1))
        self.slot = int(util.get_parameter_value(specs, "スロット", 0))
        self.elemental = util.get_parameter_value(specs, "属性", "無")
        self.refining = util.get_parameter_value(specs, "精錬", "可")
        self.destruction = util.get_parameter_value(specs, "破損", "する")


class Armor(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.ARMOR
        self.type = util.get_parameter_value(specs, "系列")
        self.position = util.get_parameter_value(specs, "位置", "-")
        self.defense = int(util.get_parameter_value(specs, "防御", 0))
        if util.exist_parameter(specs, "Def"):
            self.defense = int(util.get_parameter_value(specs, "Def"))
        self.magic_defense = int(util.get_parameter_value(specs, "Mdef", 0))
        self.weight = float(util.get_parameter_value(specs, "重量"))
        v = util.get_parameter_value(specs, "要求レベル")
        self.required_level = int(1 if v in [None, "無し", "なし"] else v)
        self.equippable = util.get_parameter_value(specs, "装備", "").split(" ")
        if util.exist_parameter(specs, "装備職業"):
            self.equippable = util.get_parameter_value(specs, "装備職業").split(" ")
        if util.exist_parameter(specs, "装着"):
            self.equippable = util.get_parameter_value(specs, "装着").split(" ")
        self.slot = int(util.get_parameter_value(specs, "スロット", 0))
        self.elemental = "-"
        if self.type == "鎧":
            self.elemental = util.get_parameter_value(specs, "属性", "無")
            for line in description:
                r = re.match("^鎧に(.+)属性を付与する$", line)
                if r:
                    self.elemental = r.group(1)
                    break
        self.refining = util.get_parameter_value(specs, "精錬", "可")
        self.destruction = util.get_parameter_value(specs, "破損", "する")


class Shadow(Armor):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description, specs)
        self.category = Category.SHADOW


class Costume(Armor):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description, specs)
        self.category = Category.COSTUME


class Ammunition(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.AMMUNITION
        self.type = util.get_parameter_value(specs, "系列")
        self.weight = float(util.get_parameter_value(specs, "重量"))
        self.attack = int(util.get_parameter_value(specs, "攻撃", 0))
        if util.exist_parameter(specs, "Atk"):
            self.attack = int(util.get_parameter_value(specs, "Atk"))
        self.magic_attack = int(util.get_parameter_value(specs, "Matk", 0))
        for line in description:
            r = re.match("^Matk \+ (\d)+$", line)
            if r:
                self.magic_attack = int(r.group(1))
        self.elemental = util.get_parameter_value(specs, "属性", "無")
        v = util.get_parameter_value(specs, "要求レベル")
        self.required_level = int(1 if v in [None, "無し", "なし"] else v)


class Pet(RoObject):
    def __init__(
        self, id: int, name: str, description: list[str], specs: list[str]
    ) -> None:
        super().__init__(id, name, description)
        self.category = Category.PET
        self.weight = float(util.get_parameter_value(specs, "重量", 0))
        v = util.get_parameter_value(specs, "系列", "")
        self.type = util.get_parameter_value(specs, "種類", v).replace("－", "ー")
        if util.exist_parameter(specs, "餌"):
            self.feed = util.get_parameter_value(specs, "餌")
        if util.exist_parameter(specs, "アクセサリー"):
            self.accessory = util.get_parameter_value(specs, "アクセサリー")
        if util.exist_parameter(specs, "装備"):
            self.equippable = util.get_parameter_value(specs, "装備")


def load_names() -> dict[str, str]:
    names: dict[str, str] = dict()
    with open(
        os.path.join(config.file_dir, "idnum2itemdisplaynametable.txt"),
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("//"):
            continue
        terms = line.split("#")
        if len(terms) <= 2:
            continue
        names[terms[0].strip()] = terms[1].strip()
    return names


def load_slots() -> dict[str, int]:
    slots: dict[str, int] = dict()
    with open(
        os.path.join(config.file_dir, "itemslotcounttable.txt"),
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("//"):
            continue
        terms = line.split("#")
        if len(terms) <= 2:
            continue
        slots[terms[0].strip()] = int(terms[1].strip())
    return slots


def load_cards_affix() -> dict[str, tuple[str, str]]:
    cards: dict[str, (str, str)] = dict()
    postfix: list[str] = list()
    with open(
        os.path.join(config.file_dir, "cardpostfixnametable.txt"),
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("//"):
            continue
        terms = line.split("#")
        postfix.append(terms[0].strip())

    with open(
        os.path.join(config.file_dir, "cardprefixnametable.txt"),
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("//"):
            continue
        terms = line.split("#")
        if len(terms) <= 2:
            continue
        if terms[0].strip() in postfix:
            cards[terms[0].strip()] = ("", terms[1].strip())
        else:
            cards[terms[0].strip()] = (terms[1].strip(), "")
    return cards


def load_description(
    names: dict[str, str], slots: dict[str, int], cards: dict[str, str]
):
    items = dict()
    with open(
        os.path.join(config.file_dir, "idnum2itemdesctable.txt"), encoding="utf-8"
    ) as f:
        lines = f.readlines()
    note: list[str] = list()
    for line in lines:
        line = line.strip("\n")
        if line.startswith("//") or line == "":
            continue
        if line == "#":
            blocks = "\n".join(note[1:]).split(DESCRIPTION_SEPARATOR)
            specs = util.build_specs(blocks[-1])
            id = note[0][:-1]
            description = DESCRIPTION_SEPARATOR.join(blocks).split("\n")
            name = names.get(id)
            if name:
                if name == "-" or util.get_parameter_value(specs, "重量") == "-":
                    logger.debug(f"missiong item [{id}]")
                    note = list()
                    continue

                o = None
                if util.is_item(specs):
                    o = Item(int(id), name, description, specs)
                elif util.is_card(specs):
                    o = Card(int(id), name, description, specs)
                    if id in cards:
                        o.prefix = cards[id][0]
                        o.postfix = cards[id][1]
                    if o.location is None:
                        logger.debug(f"card affix not found [{id}]")
                elif util.is_enchant(specs):
                    o = Enchant(int(id), name, description)
                elif util.is_shadow(specs):
                    o = Shadow(int(id), name, description, specs)
                    if id in slots:
                        o.slot = slots[id]
                elif util.is_weapon(specs):
                    o = Weapon(int(id), name, description, specs)
                    if id in slots:
                        o.slot = slots[id]
                elif util.is_armor(specs):
                    o = Armor(int(id), name, description, specs)
                    if id in slots:
                        o.slot = slots[id]
                elif util.is_costume(specs):
                    o = Costume(int(id), name, description, specs)
                    if id in slots:
                        o.slot = slots[id]
                elif util.is_ammunition(specs):
                    o = Ammunition(int(id), name, description, specs)
                elif util.is_pet(specs):
                    o = Pet(int(id), name, description, specs)
                else:
                    logger.warning(f"Not supported [{[id, specs]}]")
                    ...
                if o:
                    items[id] = vars(o)
            else:
                logger.debug(f"name not found [{id}]")
            note = list()
        else:
            if line == "^ffffff_^000000":
                line = DESCRIPTION_SEPARATOR
            note.append(line)
    return items


def save(items):
    with open(
        os.path.join(config.dist_dir, "items.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

def prepare():
    data = [
        "cardpostfixnametable.txt",
        "cardprefixnametable.txt",
        "idnum2itemdesctable.txt",
        "idnum2itemdisplaynametable.txt",
        "itemslotcounttable.txt"
    ]
    for d in data:
        path = os.path.join(config.file_dir, d)
        if not os.path.exists(path):
            logger.fatal(f"File not found [{path}]")
            sys.exit(404)
    os.makedirs(config.dist_dir, exist_ok=True)

def gen():
    names: list[str, str] = load_names()
    slots: list[str, int] = load_slots()
    cards: list[str, str] = load_cards_affix()
    items = load_description(names, slots, cards)
    save(items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="loglevel",
        const=DEBUG,
        default=WARNING,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_const", dest="loglevel", const=INFO
    )
    args = parser.parse_args()
    logger.setLevel(args.loglevel)
    prepare()
    gen()
