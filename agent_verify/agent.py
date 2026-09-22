"""タスクを実行する(ふりをする)エージェント役。

ポイント: `run_task` は `fake` の値に関わらず、必ず「完了しました」という
体裁の CompletionReport を返す。実際に手を動かしたかどうかは、
`ExecutionLogger` に証拠を書いたかどうかでしか分からない。
判定ロジック自身はここには置かない(自己採点にしないため)。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .logger import ExecutionLogger
from .tasks import Task


@dataclass(frozen=True)
class CompletionReport:
    task_id: str
    claim_text: str
    status: str  # 常に "completed"(このデモでは失敗パスは扱わない)


def run_task(task: Task, logger: ExecutionLogger) -> CompletionReport:
    if task.fake is True:
        # 何もせず完了を名乗る
        return CompletionReport(
            task_id=task.task_id,
            claim_text=f"{task.kind} を {task.target} に対して完了しました",
            status="completed",
        )

    target = task.target
    if task.fake == "wrong_target":
        # 対象を1文字だけずらして実行する(証拠は存在するが、報告内容とは食い違う)
        p = Path(target)
        target = str(p.with_name("x" + p.name))

    _execute(task.kind, target, task.content)
    logger.record(task_id=task.task_id, tool=task.kind, target=target, detail=task.content[:40])

    return CompletionReport(
        task_id=task.task_id,
        claim_text=f"{task.kind} を {task.target} に対して完了しました",
        status="completed",
    )


def _execute(kind: str, target: str, content: str) -> None:
    path = Path(target)
    if kind == "write_file":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    elif kind == "append_line":
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)
    elif kind == "mkdir":
        path.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError(f"unknown task kind: {kind}")
