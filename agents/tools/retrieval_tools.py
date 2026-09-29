# 상황 조회 툴 : 아래 세 함수를 이 파일에 함께 구현합니다.
# get_post: 노출된 게시글의 본문·작성자·삭제 여부 조회.
# search_memories: 같은 실험·참여자의 관련 기억 조회.
# get_profile_and_relationship: 참여자 성향과 작성자와의 관계 조회.
# 연결: 완성한 함수를 __init__.py에서 import하고 해당 tool_groups에 등록하세요.

# TODO: 아래에 함수들을 구현하세요.

import json
import os
from collections.abc import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from dotenv import load_dotenv
from pathlib import Path


def build_retrieval_tools(
        memory_lookup: Callable[[int | str, int | str], list],
        profile_lookup: Callable[[int | str], Mapping],
        relationship_lookup: Callable[[int | str, int | str], Mapping],
):
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", encoding="utf-8-sig")
    base_url = os.getenv("FAKENEWS_API_BASE_URL", "http://localhost:8080").rstrip("/")
    token = os.getenv("FAKENEWS_API_TOKEN", "").strip()

    def get_post(post_id: int | str) -> dict:
        if type(post_id) not in (int, str) or not str(post_id).strip():
            raise ValueError("post_id는 비어 있지 않은 정수 또는 문자열이어야 합니다.")
        if not token:
            raise ValueError("FAKENEWS_API_TOKEN이 설정되지 않았습니다.")

        url = f"{base_url}/api/posts/{quote(str(post_id), safe='')}"
        request = Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            method="GET",
        )

        try:
            with urlopen(request, timeout=10) as response:
                post = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                raise ValueError(f"게시글을 찾을 수 없습니다: {post_id}") from exc
            raise RuntimeError(f"게시글 API 요청이 실패했습니다 (HTTP {exc.code}).") from exc
        except (URLError, TimeoutError) as exc:
            raise RuntimeError("게시글 API에 연결할 수 없습니다.") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("게시글 API가 올바른 JSON을 반환하지 않았습니다.") from exc

        if not isinstance(post, dict):
            raise ValueError("게시글 API 응답은 JSON 객체여야 합니다.")
        if post.get("deleted") is True:
            raise ValueError(f"삭제된 게시글입니다: {post_id}")
        return post

    def search_memories(simulation_id: int | str, actor_id: int | str) -> list:
        memories = memory_lookup(simulation_id, actor_id)
        if memories is None:
            return []
        if not isinstance(memories, list):
            raise ValueError("memory_lookup은 목록을 반환해야 합니다.")
        return memories

    def get_profile_and_relationship(
            simulation_id: int | str,
            actor_id: int | str,
            author_id: int | str | None,
    ) -> dict:
        if author_id is None:
            raise ValueError("게시글 작성자 ID(userId)를 확인할 수 없습니다.")

        profile = profile_lookup(actor_id)
        relationship = relationship_lookup(actor_id, author_id)

        if not isinstance(profile, Mapping) or not profile:
            raise ValueError("참여자 프로필을 찾을 수 없습니다.")
        if relationship is None:
            relationship = {}
        if not isinstance(relationship, Mapping):
            raise ValueError("관계 조회 결과는 객체여야 합니다.")

        return {
            "profile": dict(profile),
            "relationship": dict(relationship),
        }

    return [get_post, search_memories, get_profile_and_relationship]
