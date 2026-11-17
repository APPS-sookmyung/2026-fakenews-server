"""게시글·참여자 프로필·기억을 모으고 조회 오류와 누락 정보를 표시한다."""
from collections.abc import Mapping
from copy import deepcopy
from .tools.retrieval_tools import RetrievalError, get_post, get_profile_and_relationship, search_memories


class RetrievalAgent:
    def __init__(self, tools=None, *, base_url="http://localhost:8080", token=None,
                 db_path=None, timeout=10, memory_limit=20):
        registered = {tool.__name__: tool for tool in (
            tools if tools is not None else [get_post, get_profile_and_relationship, search_memories])}
        self.get_post = registered["get_post"]
        self.get_profile = registered["get_profile_and_relationship"]
        self.search_memories = registered["search_memories"]
        if timeout <= 0 or type(memory_limit) is not int or memory_limit < 1:
            raise ValueError("timeout과 memory_limit은 양수여야 합니다.")
        self.http = dict(base_url=base_url, token=token, timeout=timeout)
        self.db_path = db_path
        self.memory_limit = memory_limit

    def run(self, event):
        if not isinstance(event, Mapping):
            raise ValueError("event는 객체여야 합니다.")
        # Spring의 Long 식별자와 타입을 맞춘다. bool과 문자열 ID는 허용하지 않는다.
        for key in ("simulation_id", "actor_id", "post_id"):
            if type(event.get(key)) is not int or not 0 < event[key] <= 9223372036854775807:
                raise ValueError(f"{key}는 양의 Long 정수여야 합니다.")
        exposure = event.get("exposure_id")
        if not (type(exposure) is int and exposure > 0 or isinstance(exposure, str) and exposure.strip()):
            raise ValueError("exposure_id가 필요합니다.")
        context = dict(event=deepcopy(dict(event)), post={}, profile={}, memories=[],
                       relationship={"status": "UNAVAILABLE"}, retrieval_errors=[],
                       sources={"post": "spring", "profile": "spring", "memories": "sqlite"},
                       missing_information=["relationship"])
        try:
            post = self.get_post(event["post_id"], **self.http)
            if (not isinstance(post, Mapping) or type(post.get("id")) is not int
                    or post["id"] != event["post_id"]):
                raise ValueError("조회 게시글 ID 불일치")
            if post.get("deleted") is not False:
                raise ValueError("삭제되었거나 삭제 상태를 확인할 수 없는 게시글")
            if not isinstance(post.get("content"), str) or not post["content"].strip():
                raise ValueError("게시글 본문 누락")
            simulation_id = post.get("simulation_id")
            # 일반 사용자의 게시글은 아직 simulationId가 null일 수 있다.
            if simulation_id is not None and (type(simulation_id) is not int or simulation_id != event["simulation_id"]):
                raise ValueError("게시글의 실험 ID 불일치")
            context["post"] = deepcopy(dict(post))
        except RetrievalError as exc:
            context["retrieval_errors"].append(f"post: {exc}")
        except Exception:
            context["retrieval_errors"].append("post: 게시글 조회 실패 또는 잘못된 응답")
        try:
            bundle = self.get_profile(event["simulation_id"], event["actor_id"], context["post"], **self.http)
            profile = bundle["profile"]
            if (type(profile.get("participant_id")) is not int or profile["participant_id"] != event["actor_id"]
                    or type(profile.get("simulation_id")) is not int or profile["simulation_id"] != event["simulation_id"]
                    or not isinstance(profile.get("description"), str) or not profile["description"].strip()
                    or not isinstance(profile.get("interests"), list)
                    or any(not isinstance(i, str) or not i.strip() for i in profile["interests"])):
                raise ValueError("참여자 프로필 불일치 또는 누락")
            context["profile"] = deepcopy(dict(profile))
            context["relationship"] = deepcopy(bundle["relationship"])
        except RetrievalError as exc:
            context["retrieval_errors"].append(f"profile: {exc}")
        except Exception:
            context["retrieval_errors"].append("profile: 참여자 성향 조회 실패 또는 잘못된 응답")
        try:
            memories = self.search_memories(event["simulation_id"], event["actor_id"],
                                           limit=self.memory_limit, db_path=self.db_path)
            if not isinstance(memories, list):
                raise ValueError("잘못된 기억 조회 응답")
            context["memories"] = deepcopy(memories)
        except Exception:
            context["retrieval_errors"].append("memories: 기억 조회 실패")
        return context
