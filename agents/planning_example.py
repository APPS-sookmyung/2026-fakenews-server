"""저장소 루트에서 python -m agents.planning_example로 실행합니다.

기본 실행은 프로젝트 루트 .env를 읽고 실제 Gemini를 호출합니다.
--mock 옵션은 키와 네트워크 없이 고정 응답으로 실행합니다.
"""

import argparse
import json

from . import PlanningAgent


def example_model_call(system_prompt: str, input_json: str) -> dict:
    data = json.loads(input_json)
    return {
        "action": "COMMENT",
        "post_id": data["context"]["event"]["post_id"],
        "content": "주말에도 연장 운영하나요?",
        "reason": "주말 도서관 이용에 관심이 있는 참여자입니다.",
    }


def main():
    parser = argparse.ArgumentParser(description="PlanningAgent Gemini 예제")
    parser.add_argument("--mock", action="store_true", help="Gemini 대신 고정 응답 사용")
    args = parser.parse_args()
    context = {
        "event": {
            "simulation_id": "simulation-1", "actor_id": "participant-7",
            "post_id": 20, "exposure_id": "exposure-100",
        },
        "post": {"id": 20, "content": "동네 도서관 운영 시간이 늘었습니다."},
        "memories": [],
        "profile": {"interests": ["독서"], "description": "주말에 도서관 이용"},
        "relationship": {},
        "retrieval_errors": [],
    }
    if args.mock:
        model_call = example_model_call
    else:
        from .gemini_model import gemini_model_call
        model_call = gemini_model_call
    agent = PlanningAgent(model_call=model_call)
    print(json.dumps(agent.run(context), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
