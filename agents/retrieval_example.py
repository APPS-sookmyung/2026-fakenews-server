"""Run from the project root with ``python -m agents.retrieval_example``."""

import argparse
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agents.retrieval_agent import RetrievalAgent

def example_param() -> dict:
    return {
        "event":{"simulation_id":"simulation-1","actor_id":"participant-7","post_id":10,"exposure_id":"exposure-100"}
    }

def main():
    parser = argparse.ArgumentParser(description="RetrievalAgent example")
    parser.add_argument(
        "param",
        nargs="?",
        help='JSON input, e.g. \'{"event":{"simulation_id":"simulation-1","actor_id":"participant-7","post_id":20,"exposure_id":"exposure-100"}}\'',
    )
    parser.add_argument("--mock", action="store_true", help="모의 실행")
    args = parser.parse_args()

    try:
        if args.mock:
            param = example_param()
        else:
            if args.param is None:
                parser.error("param JSON을 입력하거나 --mock을 사용하세요.")
            # In cmd.exe, single quotes are not shell quoting and may arrive
            # as literal characters around the JSON argument.
            param_text = args.param.strip()

            print("DEBUG args.param =", repr(args.param))
            print("DEBUG param_text =", repr(param_text))

            if len(param_text) >= 2 and param_text[0] == param_text[-1] == "'":
                param_text = param_text[1:-1]
            param = json.loads(param_text)

    except json.JSONDecodeError as exc:
        parser.error(f"param must be valid JSON: {exc.msg}")
    if not isinstance(param, dict):
        parser.error("param must be a JSON object")
    if not isinstance(param.get("event"), dict):
        parser.error("param must contain an 'event' JSON object")

    agent = RetrievalAgent()
    print(json.dumps(agent.run(param["event"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
