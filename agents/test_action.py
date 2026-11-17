import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

from agents.main import create_action_agent
from agents.tools.action_tools import ActionFailed


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.event = dict(simulation_id=1, actor_id=7, post_id=20, exposure_id="e-1")
        self.decision = dict(decision_id="d-1", action="LIKE", post_id=20, content=None, reason="관심")
        self.critique = dict(decision_id="d-1", verdict="APPROVE")
        self.executor = Mock(return_value=dict(status="SUCCESS", resource_id=10))
        self.agent = create_action_agent(executor=self.executor, token="trusted-token")

    def run_action(self):
        return self.agent.run(self.event, self.decision, self.critique)

    def test_dispatch_and_unchanged_comment(self):
        for action in ("LIKE", "COMMENT", "REPOST"):
            with self.subTest(action=action):
                self.event["exposure_id"] = action
                self.decision.update(action=action, content="  그대로 유지  " if action == "COMMENT" else None)
                self.assertEqual(self.run_action()["status"], "SUCCESS")
                args = self.executor.call_args.kwargs
                self.assertEqual(args["action"], action)
                self.assertEqual(args["content"], self.decision["content"])
                self.assertEqual(args["actor_id"], 7)
                self.assertEqual(args["token"], "trusted-token")

    def test_approval_gate(self):
        for critique in (None, {}, dict(verdict="REJECT", decision_id="d-1"),
                         dict(verdict="APPROVE", decision_id="other")):
            self.assertEqual(self.agent.run(self.event, self.decision, critique)["status"], "SKIPPED")
        self.executor.assert_not_called()

    def test_target_and_content_validation(self):
        for change in (dict(post_id=21), dict(post_id=True), dict(action="BAD"),
                       dict(action="COMMENT", content=" "), dict(content="unexpected")):
            decision = dict(self.decision, **change)
            self.assertEqual(self.agent.run(self.event, decision, self.critique)["status"], "FAILED")
        self.executor.assert_not_called()

    def test_skip(self):
        self.decision["action"] = "SKIP"
        self.assertEqual(self.run_action()["status"], "SKIPPED")
        self.executor.assert_not_called()

    def test_timeout_and_invalid_response_are_not_retried(self):
        for response in (TimeoutError("secret"), None, dict(status="SUCCESS"), dict(status=[])):
            with self.subTest(response=response):
                executor = Mock(side_effect=response) if isinstance(response, Exception) else Mock(return_value=response)
                agent = create_action_agent(executor=executor, token="token")
                first = agent.run(self.event, self.decision, self.critique)
                self.assertEqual(first["status"], "UNKNOWN")
                self.assertNotIn("secret", first["error"])
                self.assertEqual(first, agent.run(self.event, self.decision, self.critique))
                executor.assert_called_once()

    def test_confirmed_failure_and_missing_configuration(self):
        self.executor.side_effect = ActionFailed("secret")
        self.assertEqual(self.run_action()["status"], "FAILED")
        self.assertEqual(create_action_agent().run(self.event, self.decision, self.critique)["status"], "FAILED")

    def test_concurrent_duplicate_and_conflict(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.run_action(), range(8)))
        self.assertTrue(all(result == results[0] for result in results))
        self.executor.assert_called_once()
        self.decision["action"] = "REPOST"
        self.assertEqual(self.run_action()["status"], "FAILED")
        self.executor.assert_called_once()

    def test_stable_key_and_typed_exposure(self):
        first = self.run_action()["idempotency_key"]
        self.assertEqual(first, create_action_agent().run(self.event, self.decision, self.critique)["idempotency_key"])
        self.event["exposure_id"] = 1
        numeric = self.run_action()["idempotency_key"]
        self.event["exposure_id"] = "1"
        self.assertNotEqual(numeric, self.run_action()["idempotency_key"])

    def test_invalid_event(self):
        for change in (dict(actor_id=True), dict(simulation_id=0), dict(exposure_id="")):
            with self.assertRaises(ValueError):
                self.agent.run(dict(self.event, **change), self.decision, self.critique)
        self.executor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
