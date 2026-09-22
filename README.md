# agent-completion-proof

エージェントの「完了しました」という自己申告を、実行ログの証拠と突き合わせて検証する CLI デモ。

## 構成

- `agent_verify/tasks.py` — 発注するタスクの仕様(何を・どこに)
- `agent_verify/agent.py` — タスクを実行する(または、わざと実行せず完了報告だけ出す)エージェント役
- `agent_verify/logger.py` — 実際に呼ばれたツールと対象を JSONL に記録する証拠レイヤー
- `agent_verify/verifier.py` — タスク仕様・完了報告・実行ログの3者を突き合わせて判定する
- `demo.py` — 上記を通しで動かすエントリポイント
- `tests/test_verifier.py` — 判定ロジックの単体テスト

## 実行

```bash
python3 demo.py
python3 -m unittest discover -s tests
```

追加の依存ライブラリは無し(標準ライブラリのみ)。Python 3.11 で動作確認済み。

## 判定の3分類

- `VERIFIED` — タスク仕様と実行ログの証拠が一致
- `UNVERIFIED` — 完了報告はあるが証拠が無い(「やったふり」)
- `MISMATCH` — 証拠はあるが対象がタスク仕様とずれている(誤った対象への実行)
