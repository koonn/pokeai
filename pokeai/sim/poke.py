"""
ポケモンの動的な状態
"""
import warnings
from typing import List, TypeVar

import pokeai.sim
from pokeai.sim.poke_static import PokeStatic
from pokeai.sim.move import Move
from pokeai.sim.poke_type import PokeType


class PokeMoveStatus:
    """
    ポケモンの覚えている技とその状態（PP等）
    """
    move: Move
    pp: int
    # TODO: かなしばり状態


class Rank:
    """
    ランクパラメータ
    """
    _value: int
    min: int
    max: int

    def __init__(self, min: int = -6, max: int = 6):
        self._value = 0
        self.min = min
        self.max = max

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        assert self.min <= value <= self.max
        self._value = value

    def reset(self):
        self._value = 0

    def incr(self, diff: int):
        """
        パラメータを指定した数変動させる。最大値・最小値でクリッピングする。
        :param diff:
        :return:
        """
        self._value = max(min(self.value + diff, self.max), self.min)

    def can_incr(self, diff: int) -> bool:
        """
        ランクを指定した値だけ移動可能かどうかを返す。
        一部だけ移動できる場合もTrue。ランク5から+2 -> True
        :param diff:
        :return:
        """
        assert diff != 0
        if diff > 0:
            return self.value < self.max
        elif diff < 0:
            return self.value > self.min


class Poke:
    """
    ポケモンの動的な状態
    """

    _poke_st: PokeStatic
    """
    基本ステータス
    """
    max_hp: int
    _hp: int
    st_a: int
    st_b: int
    st_c: int
    st_s: int
    base_s: int
    lv: int
    moves: List[PokeMoveStatus]
    poke_types: List[PokeType]
    """
    ランク補正
    """
    rank_a: Rank
    rank_b: Rank
    rank_c: Rank
    rank_s: Rank
    rank_evasion: Rank  # 回避
    rank_accuracy: Rank  # 命中
    multi_turn_move_info: TypeVar("pokeai.sim.multi_turn_move_info.MultiTurnMoveInfo")

    def __init__(self, poke_st: PokeStatic):
        self._poke_st = poke_st
        self.reset()

    def reset(self):
        # 静的パラメータをすべてコピー
        # 「へんしん」「テクスチャー」等でバトル中に書き換わりうる
        st = self._poke_st
        self.max_hp = st.max_hp
        self._hp = st.max_hp
        self.base_s = st.base_s
        self.st_a = st.st_a
        self.st_b = st.st_b
        self.st_c = st.st_c
        self.st_s = st.st_s
        self.lv = st.lv
        self.moves = []
        self.multi_turn_move_info = None
        for move in st.moves:
            pms = PokeMoveStatus()
            pms.move = move
            pms.pp = 5
            self.moves.append(pms)
        self.poke_types = self._poke_st.poke_types.copy()

        self.rank_a = Rank()
        self.rank_b = Rank()
        self.rank_c = Rank()
        self.rank_s = Rank()
        self.rank_accuracy = Rank(-6, 0)
        self.rank_evasion = Rank(0, 6)

    def on_change(self):
        """
        交代で戻ったときの処理
        :return:
        """
        self.rank_a.reset()
        self.rank_b.reset()
        self.rank_c.reset()
        self.rank_s.reset()
        self.rank_accuracy.reset()
        self.rank_evasion.reset()
        # 連続技途中での交代を想定していない（2世代以降の吹き飛ばし等、そういう技はないはず）
        assert self.multi_turn_move_info is None, "Poke.on_change called while continuous_move_info is not None"

    def on_turn_end(self):
        """
        ターン終了時の処理
        :return:
        """

    def is_faint(self):
        return self.hp == 0

    @property
    def hp(self) -> int:
        return self._hp

    def hp_incr(self, diff: int):
        new_hp = self._hp + diff
        assert 0 <= new_hp <= self.max_hp
        self._hp = new_hp

    def eff_a(self, critical: bool = False) -> int:
        """
        補正済みこうげき
        :return:
        """
        # TODO: 補正
        return self.st_a

    def eff_b(self, critical: bool = False) -> int:
        """
        補正済みぼうぎょ
        :return:
        """
        # TODO: 補正
        return self.st_b

    def eff_c(self, critical: bool = False) -> int:
        """
        補正済みとくしゅ
        :return:
        """
        # TODO: 補正
        return self.st_c

    def eff_s(self) -> int:
        """
        補正済みすばやさ
        :return:
        """
        # TODO: 補正
        return self.st_s

    def move_index(self, move: Move) -> int:
        """
        技からそのインデックスを取得
        :param move:
        :return:
        """
        for i, pms in enumerate(self.moves):
            if pms.move == move:
                return i
        raise ValueError

    def __str__(self):
        return f"{self._poke_st.dexno.name} (HP {self.hp}/{self.max_hp})"
