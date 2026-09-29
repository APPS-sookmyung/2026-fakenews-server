"""게시글에 반응하기 전에 필요한 정보를 조회하는 에이전트."""

from collections.abc import Mapping, Sequence
from typing import Any

from .tools.retrieval_tools import build_retrieval_tools


def _memory_lookup(simulation_id: int | str, actor_id: int | str) -> list:
    """Default memory provider; connect this to the project's memory store."""
    return []


def _profile_lookup(actor_id: int | str) -> Mapping:
    """Default profile provider; connect this to the participant store."""
    return {}


def _relationship_lookup(actor_id: int | str, author_id: int | str) -> Mapping:
    """Default relationship provider; connect this to the relationship store."""
    return {}


class RetrievalAgent:
    """조회 도구를 호출해 PlanningAgent에 전달할 context를 구성합니다."""

    REQUIRED_TOOLS = frozenset({
        "get_post",
        "search_memories",
        "get_profile_and_relationship",
    })

    def __init__(self):
        # Named attributes let run() call the three retrieval functions directly.
        (
            self.get_post,
            self.search_memories,
            self.get_profile_and_relationship,
        ) = build_retrieval_tools(
            _memory_lookup,
            _profile_lookup,
            _relationship_lookup,
        )

    def run(self, event: Mapping[str, Any]) -> dict:
        """event를 조회해 Planner가 요구하는 context를 반환합니다."""
        if not isinstance(event, Mapping):
            raise ValueError("event는 객체여야 합니다.")

        for key in ("simulation_id", "actor_id", "post_id", "exposure_id"):
            if key not in event or event[key] is None:
                raise ValueError(f"event.{key}가 필요합니다.")

        context = {
            "event": dict(event),
            "post": None,
            "memories": [],
            "profile": None,
            "relationship": {},
            "retrieval_errors": [],
        }

        try:
            post = self.get_post(event["post_id"])
            if not isinstance(post, Mapping) or not post:
                raise ValueError("게시글 조회 결과가 비어 있거나 객체가 아닙니다.")
            context["post"] = dict(post)
        except Exception as exc:
            context["retrieval_errors"].append({
                "source": "get_post",
                "message": str(exc),
            })

        # 게시글 조회 실패 시 작성자 ID를 알 수 없으므로 나머지 조회는 건너뜁니다.
        if context["post"] is not None:
            try:
                memories = self.search_memories(
                    event["simulation_id"], event["actor_id"]
                )
                if memories is None:
                    memories = []
                if isinstance(memories, (str, bytes, Mapping)) or not isinstance(
                    memories, Sequence
                ):
                    raise ValueError("기억 조회 결과는 목록이어야 합니다.")
                context["memories"] = list(memories)
            except Exception as exc:
                context["retrieval_errors"].append({
                    "source": "search_memories",
                    "message": str(exc),
                })

            try:
                result = self.get_profile_and_relationship(
                    event["simulation_id"],
                    event["actor_id"],
                    context["post"].get("userId"),
                )
                if not isinstance(result, Mapping):
                    raise ValueError("성향·관계 조회 결과는 객체여야 합니다.")
                profile = result.get("profile")
                if not isinstance(profile, Mapping) or not profile:
                    raise ValueError("참여자 profile 조회 결과가 비어 있습니다.")
                relationship = result.get("relationship") or {}
                if not isinstance(relationship, Mapping):
                    raise ValueError("relationship 조회 결과는 객체여야 합니다.")
                context["profile"] = dict(profile)
                context["relationship"] = dict(relationship)
            except Exception as exc:
                context["retrieval_errors"].append({
                    "source": "get_profile_and_relationship",
                    "message": str(exc),
                })

        return context
