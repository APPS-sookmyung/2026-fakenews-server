"""승인된 제안을 그대로 실행한다. LLM 호출과 자동 재전송은 하지 않는다."""
import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from threading import Lock

from .tools.action_tools import ActionFailed, like_post, create_comment, repost_post
from .tools.critic_tools import ACTIONS, same_id


class ActionAgent:
    """event는 호출자의 신뢰된 정보다. 재시작/다중 프로세스 중복은 서버가 막아야 한다."""

    def __init__(self, tools=None, *, executor=None, token=None):
        registered = {tool.__name__: tool for tool in (
            tools if tools is not None else [like_post, create_comment, repost_post])}
        self.tools = {action: registered[name] for action, name in (
            ("LIKE", "like_post"), ("COMMENT", "create_comment"), ("REPOST", "repost_post"))}
        self.executor, self.token = executor, token
        self._results = {}
        self._lock = Lock()

    def run(self, event, decision, critique):
        if not isinstance(event, Mapping):
            raise ValueError("신뢰된 event가 필요합니다.")
        for field in ("simulation_id", "actor_id", "post_id"):
            if type(event.get(field)) is not int or not 0 < event[field] <= 9223372036854775807:
                raise ValueError(f"{field}는 양의 Long 정수여야 합니다.")
        exposure = event.get("exposure_id")
        if not (type(exposure) is int and exposure > 0 or isinstance(exposure, str) and exposure.strip()):
            raise ValueError("exposure_id가 필요합니다.")
        key = "action-" + hashlib.sha256(json.dumps(
            [event["simulation_id"], event["actor_id"], exposure],
            ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        decision = deepcopy(dict(decision)) if isinstance(decision, Mapping) else {}
        result = dict(decision_id=decision.get("decision_id"), action=decision.get("action"),
                      status="FAILED", resource_id=None, error=None, idempotency_key=key)

        def stop(error, status="FAILED"):
            return dict(result, status=status, error=error)

        if (not isinstance(decision.get("decision_id"), str) or not decision["decision_id"].strip()
                or not isinstance(critique, Mapping) or critique.get("verdict") != "APPROVE"
                or not same_id(critique.get("decision_id"), decision["decision_id"])):
            return stop("현재 제안에 대한 승인이 없습니다.", "SKIPPED")
        action = decision.get("action")
        if not isinstance(action, str) or action not in ACTIONS:
            return stop("허용되지 않은 행동입니다.")
        if not same_id(decision.get("post_id"), event["post_id"]):
            return stop("제안과 노출 대상이 다릅니다.")
        content = decision.get("content")
        if action == "COMMENT":
            if not isinstance(content, str) or not content.strip():
                return stop("댓글 본문이 필요합니다.")
        elif content is not None:
            return stop("COMMENT 이외의 content는 null이어야 합니다.")
        fingerprint = json.dumps([event["post_id"], decision], sort_keys=True, ensure_ascii=False)
        with self._lock:
            if key in self._results:
                previous, saved = self._results[key]
                if previous != fingerprint:
                    return stop("같은 노출에 다른 제안이 이미 처리되었습니다.")
                return deepcopy(saved)
            if action == "SKIP":
                result["status"] = "SKIPPED"
            else:
                try:
                    response = self.tools[action](
                        simulation_id=event["simulation_id"], actor_id=event["actor_id"],
                        post_id=event["post_id"], content=content, idempotency_key=key,
                        executor=self.executor, token=self.token)
                    if not isinstance(response, Mapping) or response.get("status") not in ("SUCCESS", "FAILED", "UNKNOWN"):
                        raise ValueError("잘못된 행동 응답")
                    resource = response.get("resource_id")
                    if response["status"] == "SUCCESS" and not (
                        type(resource) is int and resource > 0 or isinstance(resource, str) and resource.strip()
                    ):
                        raise ValueError("성공 응답에 resource_id가 없습니다.")
                    error = response.get("error")
                    if error is not None and not isinstance(error, str):
                        raise ValueError("잘못된 error 형식")
                    result.update(status=response["status"],
                                  resource_id=resource if response["status"] == "SUCCESS" else None,
                                  error=error if response["status"] != "SUCCESS" else None)
                except ActionFailed:
                    result.update(status="FAILED", error="행동 API 미설정, 인증 누락 또는 확인된 실행 거절")
                except Exception:
                    result.update(status="UNKNOWN", error="실행 결과를 확인할 수 없습니다. 서버 결과 조회가 필요합니다.")
            self._results[key] = (fingerprint, deepcopy(result))
            return deepcopy(result)
