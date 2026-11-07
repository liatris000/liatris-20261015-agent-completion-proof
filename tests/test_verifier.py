import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_verify.agent import CompletionReport
from agent_verify.logger import LogEntry
from agent_verify.tasks import Task
from agent_verify.verifier import Verdict, verify


class VerifierTest(unittest.TestCase):
    def test_verified_when_evidence_matches(self) -> None:
        task = Task("t1", "write_file", "/tmp/x/report.md", content="ok")
        report = CompletionReport("t1", "write_file を完了しました", "completed")
        entry = LogEntry(ts=0.0, task_id="t1", tool="write_file", target="/tmp/x/report.md", detail="")

        results = verify([task], [report], [entry])

        self.assertEqual(results[0].verdict, Verdict.VERIFIED)

    def test_unverified_when_no_evidence(self) -> None:
        task = Task("t1", "write_file", "/tmp/x/report.md", fake=True)
        report = CompletionReport("t1", "write_file を完了しました", "completed")

        results = verify([task], [report], [])

        self.assertEqual(results[0].verdict, Verdict.UNVERIFIED)

    def test_mismatch_when_target_differs(self) -> None:
        task = Task("t1", "write_file", "/tmp/x/notes.md")
        report = CompletionReport("t1", "write_file を完了しました", "completed")
        entry = LogEntry(ts=0.0, task_id="t1", tool="write_file", target="/tmp/x/xnotes.md", detail="")

        results = verify([task], [report], [entry])

        self.assertEqual(results[0].verdict, Verdict.MISMATCH)

    def test_mismatch_when_task_unknown(self) -> None:
        report = CompletionReport("ghost", "存在しないタスクの完了報告", "completed")

        results = verify([], [report], [])

        self.assertEqual(results[0].verdict, Verdict.MISMATCH)


if __name__ == "__main__":
    unittest.main()
