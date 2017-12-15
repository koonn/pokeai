"""
ランダムなパーティを生成して、ランダムプレイヤーでたたかわせて強さを測定する
python -m pokeai.ai_v4.random_rating out 10
"""
import copy
from typing import List
import pickle
import argparse
import numpy as np
from tqdm import tqdm

from pokeai.sim import Party
from . import pokeai_env
from . import party_generation_helper
from .agents import RandomAgent
from . import util

logger = util.get_logger(__name__)


def generate_random_parties(party_size: int, n_parties: int):
    return [party_generation_helper.get_random_party(party_size) for i in range(n_parties)]


class ConstantPartyGenerator:
    """
    固定されたパーティを毎回返す関数オブジェクト。
    オブジェクトのコピーにより、リセットされた状態のパーティが毎回得られる。
    """
    party_pair: List[Party]

    def __init__(self, party_pair: List[Party]):
        assert len(party_pair) == 2
        self.party_pair = party_pair

    def __call__(self) -> List[Party]:
        return copy.deepcopy(self.party_pair)


def play_party_pair(party_pair: List[Party], env_rule: pokeai_env.EnvRule, n_play: int):
    """
    パーティの組に対してランダム対戦をさせ、勝敗数を得る。
    :param party_pair:
    :param env_rule:
    :param n_play:
    :return: np.ndarray [player0の勝ち数, player1の勝ち数]
    """
    generate_party_func = ConstantPartyGenerator(party_pair)
    # 現状分ける意味はないが、履歴を持つようなエージェントでも問題を生じなくするため
    random_friend_agent = RandomAgent(len(party_pair[0].pokes), pokeai_env.N_MOVES, 0.1)  # TODO parameter
    random_enemy_agent = RandomAgent(len(party_pair[0].pokes), pokeai_env.N_MOVES, 0.1)  # TODO parameter
    env = pokeai_env.PokeaiEnv(env_rule=env_rule,
                               reward_config=pokeai_env.RewardConfig(),
                               initial_seed=1,
                               party_generator=generate_party_func,

                               observers=[pokeai_env.ObserverPossibleAction(),
                                          pokeai_env.ObserverFightingPoke(from_enemy=False,
                                                                          nv_condition=True,
                                                                          v_condition=False,
                                                                          rank=False),
                                          pokeai_env.ObserverFightingPoke(from_enemy=True,
                                                                          nv_condition=True,
                                                                          v_condition=False,
                                                                          rank=False)
                                          ],
                               enemy_agent=random_enemy_agent
                               )

    scores = np.zeros((2,), dtype=np.float32)
    # envのループを自前で回す
    for play_i in range(n_play):
        done = False
        obs = env.reset()
        while not done:
            action = random_friend_agent.act(obs)
            obs, _, done, _ = env.step(action)
        if env.result_win:
            scores[0] += 1
        elif env.result_draw:
            scores += 0.5
        else:
            scores[1] += 1
    return scores


def evaluate_parties(parties: List[Party], env_rule: pokeai_env.EnvRule, n_play: int,
                     show_progress=False) -> np.ndarray:
    """
    パーティをランダム対戦により評価する。
    総当たりで対戦し、各パーティの勝率を得る。
    :param parties:
    :param env_rule:
    :param n_play:
    :return:
    """
    n_parties = len(parties)
    party_scores = np.zeros((n_parties,), dtype=np.float32)
    n_pairs = n_parties * (n_parties - 1) // 2
    pbar = None
    if show_progress:
        pbar = tqdm(total=n_pairs)
    for i in range(n_parties):
        for j in range(i + 1, n_parties):
            pair_scores = play_party_pair([parties[i], parties[j]], env_rule, n_play)
            party_scores[i] += pair_scores[0]
            party_scores[j] += pair_scores[1]
            if show_progress:
                pbar.update(1)
    if show_progress:
        pbar.close()

    # 対戦数で割って勝率に変換
    win_rate = party_scores / ((n_parties - 1) * n_play)
    return win_rate


def evaluate_parties_groups(parties_target: List[Party], parties_baseline: List[Party], env_rule: pokeai_env.EnvRule,
                            n_play: int, show_progress=False) -> np.ndarray:
    """
    2つのパーティ群それぞれから1つずつパーティを選択し、ランダム対戦により評価する。
    総当たりで対戦し、parties_target内の各パーティの勝率を得る。
    :param parties:
    :param env_rule:
    :param n_play:
    :return:
    """
    n_parties_target = len(parties_target)
    n_parties_baseline = len(parties_baseline)
    party_scores = np.zeros((n_parties_target,), dtype=np.float32)
    n_pairs = n_parties_target * n_parties_baseline
    pbar = None
    if show_progress:
        pbar = tqdm(total=n_pairs)
    for i in range(n_parties_target):
        for j in range(n_parties_baseline):
            pair_scores = play_party_pair([parties_target[i], parties_baseline[j]], env_rule, n_play)
            party_scores[i] += pair_scores[0]
            if show_progress:
                pbar.update(1)
    if show_progress:
        pbar.close()

    # 対戦数で割って勝率に変換
    win_rate = party_scores / n_parties_baseline
    return win_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("n_parties", type=int)
    parser.add_argument("--n_play", type=int, default=10, help="n playout per party pair")
    args = parser.parse_args()
    n_parties = args.n_parties  # type: int
    party_size = 3
    parties = generate_random_parties(party_size, n_parties)
    env_rule = pokeai_env.EnvRule(party_size, faint_change_random=True)
    party_win_rates = evaluate_parties(parties, env_rule, args.n_play, show_progress=True)
    result = {"parties": parties, "win_rates": party_win_rates}
    with open(args.out, "wb") as f:
        pickle.dump(result, f)


if __name__ == '__main__':
    main()
