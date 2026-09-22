#!/usr/bin/env python3
"""完了報告 vs 実行ログの突き合わせを実際に動かすデモ。

    python3 demo.py

`work/` 以下にファイルを実際に書き込みながら、6件のタスクを実行する。
そのうち2件はわざと「やったふり」(fake=True)、1件はわざと対象をずらして
実行する(fake="wrong_target")。完了報告だけを見るとどれも「完了しました」
だが、検証にかけると3種類の判定に分かれる。
"""
from __future__ import annotations

from pathlib import Path

from agent_verify.agent import run_task
from agent_verify.logger import ExecutionLogger
from agent_verify.tasks import build_demo_tasks
from agent_verify.verifier import summarize, verify

WORKDIR = Path(__file__).parent / "work"
LOG_PATH = Path(__file__).parent / "work" / "execution_log.jsonl"


def main() -> None:
    tasks = build_demo_tasks(str(WORKDIR))
    logger = ExecutionLogger(LOG_PATH)

    reports = []
    print("== 完了報告(エージェントの自己申告) ==")
    for task in tasks:
        report = run_task(task, logger)
        reports.append(report)
        print(f"  [{report.task_id}] {report.status}: {report.claim_text}")

    log_entries = logger.read_all()
    results = verify(tasks, reports, log_entries)

    print("\n== 検証結果(仕様 x 実行ログの突き合わせ) ==")
    for r in results:
        print(f"  [{r.task_id}] {r.verdict.value:<10} {r.reason}")

    summary = summarize(results)
    total = len(results)
    print("\n== 集計 ==")
    for verdict, count in summary.items():
        rate = (count / total * 100) if total else 0
        print(f"  {verdict:<10} {count}/{total} ({rate:.0f}%)")


if __name__ == "__main__":
    main()
