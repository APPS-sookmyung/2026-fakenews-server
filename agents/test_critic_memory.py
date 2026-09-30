"""서비스 및 모델 호출 없이 검증/기억 계약을 테스트한다."""

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from . import CriticAgent, MemoryAgent
from .tools import tool_groups
from .tools.memory_tools import save_memory, update_memory_result
from .tools.retrieval_tools import search_memories


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "memory.sqlite3"
        self.event = dict(simulation_id="s", actor_id="a", exposure_id="e", post_id=1)
        self.context = dict(event=self.event, post={"id": 1, "content": "도서관 소식"},
                            profile={"interests": ["독서"]}, memories=[], retrieval_errors=[])
        self.decision = dict(decision_id="d", action="COMMENT", post_id=1,
                             content="주말에도 운영하나요?", reason="독서에 관심")
        self.result = dict(decision_id="d", action="COMMENT", status="SUCCESS",
                           resource_id=2, error=None, idempotency_key="request")
        self.agent = MemoryAgent(tools=tool_groups["memory"], db_path=self.db)

    def remember(self, **changes):
        return self.agent.run(self.event, self.context, self.decision, None,
                              dict(self.result, **changes))

    def read(self):
        return search_memories("s", "a", db_path=self.db)

    def test_critic_valid_actions_and_immutability(self):
        before = copy.deepcopy(self.decision)
        critic = CriticAgent(tools=tool_groups["critic"])
        for action in ("LIKE", "COMMENT", "REPOST", "SKIP"):
            decision = dict(self.decision, action=action,
                            content=self.decision["content"] if action == "COMMENT" else None)
            self.assertEqual(critic.run(self.context, decision)["verdict"], "APPROVE")
        self.assertEqual(before, self.decision)

    def test_critic_revise_fields(self):
        for changes in ({"action": []}, {"content": " "}, {"decision_id": None}, {"reason": ""}):
            with self.subTest(changes=changes):
                critique = CriticAgent().run(self.context, dict(self.decision, **changes))
                self.assertEqual(critique["verdict"], "REVISE")
                self.assertTrue(critique["feedback"])
        self.assertEqual(CriticAgent(max_comment_length=2).run(self.context, self.decision)["verdict"], "REVISE")

    def test_critic_reject_target_and_retrieval_failures(self):
        for post_id in (2, "1", True):
            self.assertEqual(CriticAgent().run(self.context, dict(self.decision, post_id=post_id))["verdict"], "REJECT")
        for change in ({"retrieval_errors": ["timeout"]}, {"profile": {}}, {"post": {"id": 2}}, {"post": {"deleted": True}}):
            self.assertEqual(CriticAgent().run(dict(self.context, **change), self.decision)["verdict"], "REJECT")

    def test_optional_model_and_failure(self):
        model = Mock(return_value={"verdict": "REVISE", "reasons": ["문맥 불일치"], "feedback": "질문을 수정하세요", "decision_id": "wrong"})
        critic = CriticAgent(model_call=model)
        self.assertEqual(critic.run(self.context, self.decision)["decision_id"], "d")
        self.assertEqual(model.call_count, 1)
        critic.run(self.context, dict(self.decision, content=""))
        self.assertEqual(model.call_count, 1)
        for response in ("not JSON", {"verdict": "APPROVE"}, {"verdict": "REVISE", "reasons": []}):
            model.return_value = response
            self.assertEqual(critic.run(self.context, self.decision)["verdict"], "REJECT")
        model.side_effect = TimeoutError()
        self.assertEqual(critic.run(self.context, self.decision)["verdict"], "REJECT")

    def test_statuses_never_invent_success(self):
        for status in ("SUCCESS", "FAILED", "UNKNOWN", "SKIPPED"):
            self.event["exposure_id"] = status
            self.assertEqual(self.remember(status=status)["status"], "SAVED")
        for memory in self.read():
            success = memory["result"]["status"] == "SUCCESS"
            self.assertEqual(memory["executed_action"], "COMMENT" if success else None)
            self.assertEqual(memory["executed_content"], self.decision["content"] if success else None)

    def test_duplicate_and_tenant_isolation(self):
        first = self.remember()
        second = self.remember()
        self.assertEqual(second["status"], "DUPLICATE")
        self.assertEqual(first["memory_id"], second["memory_id"])
        self.assertEqual(len(self.read()), 1)
        self.assertEqual(search_memories("other", "a", db_path=self.db), [])
        self.assertEqual(search_memories("s", "other", db_path=self.db), [])
        self.assertEqual(search_memories("s", "a", post_id="1", db_path=self.db), [])

    def test_unknown_reconciliation_and_final_conflict(self):
        self.remember(status="UNKNOWN", error="timeout", resource_id=None)
        updated = self.agent.update_result(self.event, self.result)
        self.assertEqual(updated["status"], "UPDATED")
        self.assertEqual(self.read()[0]["executed_content"], self.decision["content"])
        self.assertEqual(self.remember(status="FAILED")["status"], "FAILED")
        self.assertEqual(self.read()[0]["result"]["status"], "SUCCESS")
        self.assertEqual(self.agent.update_result(dict(self.event, actor_id="other"), self.result)["status"], "FAILED")

    def test_run_can_reconcile_unknown(self):
        self.remember(status="UNKNOWN", resource_id=None)
        self.assertEqual(self.remember()["status"], "UPDATED")
        self.assertEqual(len(self.read()), 1)

    def test_invalid_result_does_not_create_memory(self):
        for changes in ({"decision_id": "other"}, {"status": "OK"}, {"action": "LIKE"}, {"action": "SKIP"}):
            self.assertEqual(self.remember(**changes)["status"], "FAILED")
        self.assertEqual(self.read(), [])

    def test_early_stop_and_missing_results(self):
        self.assertEqual(self.agent.run(self.event, self.context)["status"], "SAVED")
        self.assertEqual(self.read()[0]["result"]["status"], "UNKNOWN")
        self.event["exposure_id"] = "stopped"
        result = dict(decision_id=None, action="SKIP", status="SKIPPED", error="조회 실패")
        self.assertEqual(self.agent.run(self.event, result=result)["status"], "SAVED")
        self.assertIn("조회 실패", self.read()[0]["summary"])

    def test_only_storage_retried(self):
        calls = []

        def flaky(memory, **kwargs):
            calls.append(memory)
            if len(calls) == 1:
                raise OSError("temporary")
            return save_memory(memory, **kwargs)

        flaky.__name__ = "save_memory"
        agent = MemoryAgent(tools=[flaky, update_memory_result], db_path=self.db)
        self.assertEqual(agent.run(self.event, self.context, self.decision, None, self.result)["status"], "SAVED")
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(self.read()), 1)


if __name__ == "__main__":
    unittest.main()
