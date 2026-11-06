# agent-completion-proof

エージェントの「完了しました」という自己申告を、実行ログの証拠と突き合わせて検証する CLI デモ。

記事: https://zenn.dev/liatris/articles/20261015-agent-completion-proof

## 前提

- Python 3.11 以上(3.11 と 3.14.6 で確認)
- 追加の依存ライブラリは無し(標準ライブラリのみ)

## 動かし方

```bash
git clone https://github.com/liatris000/liatris-20261015-agent-completion-proof.git
cd liatris-20261015-agent-completion-proof
python3 demo.py
python3 -m unittest discover -s tests
```

`demo.py` は `work/` の下に実際にファイルを書き込み、実行ログを `work/execution_log.jsonl` に残す。`work/` は `.gitignore` に入れてある。

## 期待される出力

`python3 demo.py` の最後に、次の集計が出る(各タスクの行には、手元の `work/` までの絶対パスが入る)。

```text
== 集計 ==
  VERIFIED   3/6 (50%)
  UNVERIFIED 2/6 (33%)
  MISMATCH   1/6 (17%)
```

`python3 -m unittest discover -s tests`:

```text
Ran 4 tests in 0.000s

OK
```

## 判定の 3 分類

- `VERIFIED` — タスク仕様と実行ログの証拠が一致
- `UNVERIFIED` — 完了報告はあるが証拠が無い(「やったふり」)
- `MISMATCH` — 証拠はあるが対象がタスク仕様とずれている(誤った対象への実行)

## 確かめていない範囲

- エージェントは、わざと失敗する偽のエージェント(`agent_verify/agent.py`)。実際の AI エージェント(Claude Code など)の実行ログでは試していない

## 構成

- `agent_verify/tasks.py` — 発注するタスクの仕様(何を・どこに)
- `agent_verify/agent.py` — タスクを実行する(または、わざと実行せず完了報告だけ出す)エージェント役
- `agent_verify/logger.py` — 実際に呼ばれたツールと対象を JSONL に記録する証拠レイヤー
- `agent_verify/verifier.py` — タスク仕様・完了報告・実行ログの 3 者を突き合わせて判定する
- `demo.py` — 上記を通しで動かすエントリポイント
- `tests/test_verifier.py` — 判定ロジックの単体テスト

## ライセンス

MIT
