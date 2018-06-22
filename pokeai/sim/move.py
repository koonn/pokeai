from enum import Enum, auto


class Move(Enum):
    EMPTY = auto()
    BITE = auto()  # かみつく
    FLAMETHROWER = auto()  # かえんほうしゃ
    THUNDERWAVE = auto()  # でんじは
    AGILITY = auto()  # こうそくいどう
    SPLASH = auto()  # はねる
