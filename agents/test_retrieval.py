"""로컬 HTTP 테스트 서버 + SQLite로 조회부터 계획까지 검증한다. 외부 API 호출 없음."""
import copy
import json
from io import StringIO
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock, patch

from .main import retrieve_and_plan
from .retrieval_agent import RetrievalAgent
from .memory_agent import MemoryAgent


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.server.requests.append((self.path, self.headers.get("Authorization")))
                status, body = self.server.responses.get(self.path, (404, {}))
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(body).encode())

            def log_message(self, *args):
                pass
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.event = dict(simulation_id=1, actor_id=7, post_id=20, exposure_id="e-1")
        self.post = dict(postId=20, simulationId=None, participantId=None, userId=99,
                         content="도서관 운영 시간 연장", deleted=False)
        self.profile = dict(participantId=7, simulationId=1, displayName="독서가",
                            description="주말에 도서관 이용", interests=["독서"])
        self.server.responses = {"/api/posts/20": (200, self.post),
                                 "/api/simulations/1/participants/7/profile": (200, self.profile)}
        self.server.requests = []
        self.options = dict(base_url=f"http://127.0.0.1:{self.server.server_port}", token="test-token",
                            db_path=Path(self.tmp.name) / "memory.sqlite3")
        self.model = Mock(return_value=dict(action="COMMENT", post_id=20, content="주말에도 운영하나요?", reason="독서에 관심"))

    def test_http_sqlite_and_planning_connection(self):
        previous = dict(self.event, exposure_id="previous")
        MemoryAgent(db_path=self.options["db_path"]).run(previous)
        before = copy.deepcopy(self.event)
        result = retrieve_and_plan(self.event, model_call=self.model, **self.options)
        context = result["context"]
        self.assertEqual(context["retrieval_errors"], [])
        self.assertEqual(context["post"]["id"], 20)
        self.assertEqual(context["profile"]["interests"], ["독서"])
        self.assertEqual(len(context["memories"]), 1)
        self.assertEqual(context["relationship"]["status"], "UNAVAILABLE")
        self.assertEqual(context["relationship"]["author_user_id"], 99)
        self.assertEqual(result["decision"]["action"], "COMMENT")
        self.assertEqual(self.event, before)
        self.assertEqual(len(self.server.requests), 2)
        self.assertTrue(all(token == "Bearer test-token" for _, token in self.server.requests))
        self.assertEqual(json.loads(self.model.call_args.args[1])["context"], context)

    def test_no_memories_is_normal(self):
        context = RetrievalAgent(**self.options).run(self.event)
        self.assertEqual(context["memories"], [])
        self.assertEqual(context["retrieval_errors"], [])

    def assert_stops(self):
        self.model.reset_mock()
        result = retrieve_and_plan(self.event, model_call=self.model, **self.options)
        self.assertTrue(result["context"]["retrieval_errors"])
        self.assertIsNone(result["decision"])
        self.model.assert_not_called()
        self.assertNotIn("test-token", json.dumps(result))

    def test_http_errors_stop_planning(self):
        for status in (401, 404, 500):
            with self.subTest(status=status):
                self.server.responses["/api/posts/20"] = (status, {})
                self.assert_stops()

    def test_deleted_mismatched_and_invalid_post_stop_planning(self):
        for change in ({"deleted": True}, {"deleted": None}, {"postId": 21},
                       {"postId": True}, {"simulationId": 2}, {"content": ""}):
            with self.subTest(change=change):
                self.server.responses["/api/posts/20"] = (200, dict(self.post, **change))
                self.assert_stops()

    def test_bad_profile_stops_planning(self):
        for change in ({"participantId": 8}, {"simulationId": 2}, {"description": " "}, {"interests": None}):
            with self.subTest(change=change):
                self.server.responses["/api/simulations/1/participants/7/profile"] = (200, dict(self.profile, **change))
                self.assert_stops()

    def test_memory_error_is_not_treated_as_empty_memory(self):
        with patch("agents.tools.memory_tools.connection", side_effect=OSError("private file path")):
            self.assert_stops()

    def test_missing_token_and_timeout_stop_planning(self):
        self.options["token"] = None
        self.assert_stops()
        self.assertEqual(self.server.requests, [])
        self.options["token"] = "test-token"
        with patch("agents.tools.retrieval_tools.urlopen", side_effect=TimeoutError()):
            self.assert_stops()

    def test_invalid_event_is_rejected_before_http(self):
        for change in ({"actor_id": True}, {"post_id": "20"}, {"simulation_id": 0}, {"exposure_id": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                RetrievalAgent(**self.options).run(dict(self.event, **change))
        self.assertEqual(self.server.requests, [])

    def test_malformed_and_non_object_json_stop_planning(self):
        for body in ("not-json", "[]"):
            with self.subTest(body=body), patch("agents.tools.retrieval_tools.urlopen",
                                               side_effect=lambda *a, **kw: StringIO(body)):
                self.assert_stops()


if __name__ == "__main__":
    unittest.main()
