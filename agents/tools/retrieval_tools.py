"""Spring 조회 API와 로컬 기억 저장소를 연결한다."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .memory_tools import search_memories


class RetrievalError(RuntimeError):
    pass


def _get_json(path, *, base_url, token, timeout):
    if not token or not token.strip():
        raise RetrievalError("서버 조회에 Bearer 토큰이 필요합니다.")
    request = Request(base_url.rstrip("/") + path,
                      headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise RetrievalError(f"서버 조회 실패 (HTTP {exc.code}).") from None
    except (URLError, TimeoutError, OSError):
        raise RetrievalError("서버 연결 실패 또는 조회 시간 초과.") from None
    except (ValueError, UnicodeError):
        raise RetrievalError("서버 응답이 올바른 JSON이 아닙니다.") from None
    if not isinstance(data, dict):
        raise RetrievalError("서버 응답은 JSON 객체여야 합니다.")
    return data


def get_post(post_id, *, base_url, token, timeout=10):
    raw = _get_json(f"/api/posts/{post_id}", base_url=base_url, token=token, timeout=timeout)
    return {"id": raw.get("postId"), "simulation_id": raw.get("simulationId"),
            "participant_id": raw.get("participantId"), "user_id": raw.get("userId"),
            "content": raw.get("content"), "deleted": raw.get("deleted"),
            "created_at": raw.get("createdAt")}


def get_profile_and_relationship(simulation_id, actor_id, post, *, base_url, token, timeout=10):
    raw = _get_json(f"/api/simulations/{simulation_id}/participants/{actor_id}/profile",
                    base_url=base_url, token=token, timeout=timeout)
    # 관계 저장소가 없으므로 '관계 없음'으로 추정하지 않는다.
    return {"profile": {"participant_id": raw.get("participantId"),
                        "simulation_id": raw.get("simulationId"),
                        "display_name": raw.get("displayName"),
                        "description": raw.get("description"), "interests": raw.get("interests")},
            "relationship": {"status": "UNAVAILABLE", "reason": "관계 조회 기능 미구현",
                             "author_participant_id": post.get("participant_id"),
                             "author_user_id": post.get("user_id")}}
