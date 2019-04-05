# PokéAI ～人工知能の考えた最強のポケモン対戦戦略～
PokéAI(ポケエーアイ)は、ポケモンバトルの戦略を人工知能に考えさせ、
究極的には人が思いつかなかったような戦略を編み出すことを目標とするプロジェクトです。

初代バージョンの全ポケモン・技実装用ブランチ。

成果は同人誌の形で発表。頒布情報は[blog](http://select766.hatenablog.com/archive/category/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3)参照。

# setup
Python 3.6が必要。

```
python setup.py develop
```

`pokeai`パッケージとしてimport可能になる。

# test
```
python -m unittest
```

# 基本構成
- `pokeai/sim`
  - ポケモンバトルのルールを実装するシミュレータ。
- `pokeai/agent`
  - 戦略を生み出すAI部分。

# 実験方法
masterブランチは随時更新されるため、過去の実験コマンドが動かなくなっている場合があります。過去のバージョンは[tags](https://github.com/select766/pokeai/tags)から参照ください。

- 第1巻（初代1vs1編）：2018年10月（技術書典5）で刊行の本での実験の再現コマンド→[experiment_201810.md](experiment_201810.md)
- 第2巻（初代3vs3編）：2019年4月（技術書典6）で刊行の本での実験の再現コマンド→[experiment_201904.md](experiment_201904.md)

# ライセンス
コードはMITライセンスとしております。本については、ファイル内のライセンス表記をご参照ください。
