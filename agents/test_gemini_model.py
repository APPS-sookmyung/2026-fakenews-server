"""네트워크 없이 SDK 연결과 PlanningAgent 검증을 확인합니다."""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from . import PlanningAgent
from .gemini_model import gemini_model_call


class GeminiModelTests(unittest.TestCase):
    def setUp(self):
        self.context = {
            "event": {"post_id": 20}, "post": {"content": "도서관"},
            "profile": {"interests": ["독서"]}, "retrieval_errors": [],
        }

    @patch("agents.gemini_model.load_dotenv")
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"})
    @patch("agents.gemini_model.genai.Client")
    def test_request_and_validation(self, client_factory, load_env):
        client = client_factory.return_value.__enter__.return_value
        generate = client.models.generate_content
        generate.return_value = SimpleNamespace(text=json.dumps({
            "action": "SKIP", "post_id": 20, "content": None, "reason": "관심 없음",
        }))
        result = PlanningAgent(gemini_model_call).run(self.context)
        self.assertEqual(result["action"], "SKIP")
        kwargs = generate.call_args.kwargs
        self.assertEqual(kwargs["model"], "test-model")
        self.assertEqual(kwargs["config"].response_mime_type, "application/json")
        self.assertEqual(json.loads(kwargs["contents"])["context"], self.context)
        self.assertEqual(load_env.call_args.args[0].name, ".env")
        generate.return_value = SimpleNamespace(text="")
        with self.assertRaises(ValueError):
            PlanningAgent(gemini_model_call).run(self.context)
        generate.return_value = SimpleNamespace(text=json.dumps({
            "action": "LIKE", "post_id": 99, "content": None, "reason": "test",
        }))
        with self.assertRaises(ValueError):
            PlanningAgent(gemini_model_call).run(self.context)

    @patch("agents.gemini_model.load_dotenv")
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_missing_key(self, load_env):
        with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
            PlanningAgent(gemini_model_call).run(self.context)


if __name__ == "__main__":
    unittest.main()
