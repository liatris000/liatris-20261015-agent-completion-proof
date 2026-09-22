"""完了報告とログを突き合わせる検証スクリプト。

方針:
- 完了報告の文面(`claim_text`)そのものは信用しない。自然文をパースして
  正誤判定する設計は、結局「エージェントが書いた文章を信じる」構造から
  抜け出せないため
- 代わりに、発注したタスクの仕様(`Task`)と実行ログ(`LogEntry`)を突き合わせる。
  両者が一致して初めて VERIFIED とする
- 証拠が一切無ければ UNVERIFIED、証拠はあるが対象が仕様とずれていれば
  MISMATCH として区別する(どちらも「未検証」だが原因が違うので運用上は分けたい)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .agent import CompletionReport
from .logger import LogEntry
from .tasks import Task


class Verdict(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"  # ログに証拠が無い(やったふり)
    MISMATCH = "MISMATCH"  # 証拠はあるが仕様と食い違う(対象違い等)


@dataclass(frozen=True)
class VerificationResult:
    task_id: str
    verdict: Verdict
    reason: str


def verify(
    tasks: list[Task],
    reports: list[CompletionReport],
    log_entries: list[LogEntry],
) -> list[VerificationResult]:
    tasks_by_id = {t.task_id: t for t in tasks}
    # 同じ task_id に複数ログが出ることは想定していないため最後の1件を採用
    evidence_by_id: dict[str, LogEntry] = {e.task_id: e for e in log_entries}

    results = []
    for report in reports:
        task = tasks_by_id.get(report.task_id)
        if task is None:
            results.append(
                VerificationResult(report.task_id, Verdict.MISMATCH, "対応するタスク仕様が見つからない")
            )
            continue

        evidence = evidence_by_id.get(report.task_id)
        if evidence is None:
            results.append(
                VerificationResult(
                    report.task_id, Verdict.UNVERIFIED, "完了報告はあるが実行ログに証拠が無い"
                )
            )
            continue

        if evidence.tool != task.kind or evidence.target != task.target:
            results.append(
                VerificationResult(
                    report.task_id,
                    Verdict.MISMATCH,
                    f"証拠はあるが仕様と不一致 (仕様: {task.kind} {task.target} / "
                    f"証拠: {evidence.tool} {evidence.target})",
                )
            )
            continue

        results.append(VerificationResult(report.task_id, Verdict.VERIFIED, "仕様と証拠が一致"))

    return results


def summarize(results: list[VerificationResult]) -> dict[str, int]:
    summary = {v.value: 0 for v in Verdict}
    for r in results:
        summary[r.verdict.value] += 1
    return summary
