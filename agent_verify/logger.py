"""実行ログを記録するレイヤー。

エージェントの「完了しました」という報告文とは別に、実際に呼ばれたツールと
その対象を JSONL で記録する。ここに書かれたものだけを「証拠」として扱う。
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LogEntry:
    ts: float
    task_id: str
    tool: str
    target: str
    detail: str


class ExecutionLogger:
    """ツール呼び出しの証拠を1件ずつ JSONL に追記する。"""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        # 前回実行分が残っていると誤検知の原因になるので、開始時に空にする
        self.log_path.write_text("", encoding="utf-8")

    def record(self, task_id: str, tool: str, target: str, detail: str = "") -> None:
        entry = LogEntry(ts=time.time(), task_id=task_id, tool=tool, target=target, detail=detail)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

    def read_all(self) -> list[LogEntry]:
        if not self.log_path.exists():
            return []
        entries = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            entries.append(LogEntry(**data))
        return entries
