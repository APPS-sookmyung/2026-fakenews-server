"""PlanningAgent에 전달할 Gemini 호출 함수. 프로젝트 루트 .env를 읽습니다."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


def gemini_model_call(system_prompt: str, input_json: str) -> str:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", encoding="utf-8-sig")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "발급받은_API_키":
        raise ValueError("프로젝트 루트 .env에 실제 GEMINI_API_KEY를 설정하세요.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    post_id = json.loads(input_json)["context"]["event"]["post_id"]
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["LIKE", "COMMENT", "REPOST", "SKIP"]},
            "post_id": {"type": "integer" if type(post_id) is int else "string"},
            "content": {"type": ["string", "null"]},
            "reason": {"type": "string"},
        },
        "required": ["action", "post_id", "content", "reason"],
        "additionalProperties": False,
    }
    try:
        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000),
        ) as client:
            response = client.models.generate_content(
                model=model,
                contents=input_json,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_json_schema=schema,
                ),
            )
    except errors.APIError as exc:
        # SDK 원문에는 요청 정보가 포함될 수 있어 상태 코드만 노출합니다.
        hints = {
            400: "API 키와 요청 설정을 확인하세요.",
            403: "API 키 권한을 확인하세요.",
            404: "GEMINI_MODEL의 모델 이름과 사용 가능 여부를 확인하세요.",
            429: "Gemini 사용량 한도 또는 결제 설정을 확인하세요.",
        }
        hint = hints.get(exc.code, "잠시 후 다시 시도하세요.")
        raise RuntimeError(f"Gemini 요청 실패 (HTTP {exc.code}). {hint}") from None
    if not response.text:
        raise ValueError("Gemini가 텍스트를 반환하지 않았습니다. 차단 또는 생성 중단 여부를 확인하세요.")
    return response.text
