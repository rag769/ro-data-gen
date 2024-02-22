import re


def build_specs(block: str):
    block = block.replace("　", "  ")
    block = re.sub("\\^777777([^ |^\\^]+)  ", "\\^777777\\1\\^000000 ", block)
    s = re.sub("\^000000 +", "\n", block).replace("^777777", "").replace("^000000", "")
    s = re.sub(" *: *", ":\n", s)
    specs = list(
        filter(
            lambda l: l != "",
            s.split("\n"),
        )
    )
    return specs


def exist_parameter(lines: list[str], parameter: str):
    if f"{parameter}:" in lines:
        return True
    return False


def get_parameter_value(lines: list[str], parameter: str, default_value: any = None):
    if not exist_parameter(lines, parameter):
        return default_value
    return lines[lines.index(f"{parameter}:") + 1].strip()


def is_enchant(lines: list):
    return (
        not exist_parameter(lines, "重量")
        and not exist_parameter(lines, "種類")
        and not exist_parameter(lines, "系列")
    )


def is_item(lines: list):
    return (
        exist_parameter(lines, "重量")
        and not exist_parameter(lines, "系列")
        and not exist_parameter(lines, "種類")
    )


def is_card(lines: list):
    return get_parameter_value(lines, "系列") == "カード"


def is_shadow(lines: list):
    return get_parameter_value(lines, "系列") == "シャドウ"


def is_costume(lines: list):
    return get_parameter_value(lines, "系列") == "衣装"


def is_weapon(lines: list):
    weapons = [
        "カタール",
        "ガトリングガン",
        "グレネードガン",
        "ショットガン",
        "ハンドガン",
        "ライフル",
        "両手剣",
        "両手斧",
        "両手杖",
        "両手槍",
        "剣",
        "弓",
        "手裏剣",
        "斧",
        "本",
        "杖",
        "楽器",
        "槍",
        "爪",
        "片手剣",
        "片手斧",
        "片手杖",
        "片手槍",
        "短剣",
        "鈍器",
        "鞭",
        "風魔手裏剣",
    ]
    return get_parameter_value(lines, "系列") in weapons


def is_armor(lines: list):
    armors = [
        "アクセサリー",
        "アクセサリー(1)",
        "アクセサリー(2)",
        "兜",
        "鎧",
        "盾",
        "肩にかけるもの",
        "肩にかける物",
        "肩に掛けるもの",
        "靴",
    ]
    return get_parameter_value(lines, "系列") in armors


def is_ammunition(lines: list):
    ammunition = [
        "矢",
        "投擲",
        "弾",
        "砲弾",
    ]
    return get_parameter_value(lines, "系列") in ammunition


def is_pet(lines: list):
    pet = [
        "モンスターの卵",
        "テイミングアイテム",
        "キューペット装備",
        "キュ－ペット装備",
    ]
    return (
        get_parameter_value(lines, "種類") in pet
        or get_parameter_value(lines, "系列") in pet
    )


# todo: 釣り竿
