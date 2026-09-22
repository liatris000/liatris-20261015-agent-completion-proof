"""検証デモ用のタスク定義。

`fake=True` のタスクは、エージェントに「実際の書き込みをせず完了報告だけ出す」
挙動をわざと取らせるためのフラグ。検証の効果を見せるために混ぜてある。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str  # "write_file" | "append_line" | "mkdir"
    target: str
    content: str = ""
    # False: 正常に実行する / True: 実行せず「完了」とだけ報告する
    # "wrong_target": 書き込み先を1文字ずらして実行する(証拠はあるが対象違い)
    fake: bool | str = False


def build_demo_tasks(workdir: str) -> list[Task]:
    return [
        Task("t1", "write_file", f"{workdir}/report.md", content="# report\n"),
        Task("t2", "mkdir", f"{workdir}/output"),
        # t3: エージェントが「やったふり」で終わらせるケース
        Task("t4", "append_line", f"{workdir}/report.md", content="- 追記した行\n"),
        Task("t3", "write_file", f"{workdir}/config.json", content='{"ok": true}\n', fake=True),
        # t5: 書き込み先を1文字だけ間違えるケース(証拠はあるが対象が違う = MISMATCH)
        Task("t5", "write_file", f"{workdir}/notes.md", content="# notes\n", fake="wrong_target"),
        Task("t6", "mkdir", f"{workdir}/logs", fake=True),
    ]
