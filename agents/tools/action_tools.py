"""합의된 서버 API 실행기를 연결하는 행동 툴. URL은 추측하지 않는다."""

class ActionFailed(RuntimeError):
    """서버가 부작용 없음을 확인한 확정 실패."""


def _execute(action, *, simulation_id, actor_id, post_id, content,
             idempotency_key, executor=None, token=None):
    if executor is None or not isinstance(token, str) or not token.strip():
        raise ActionFailed("행동 API executor와 Bearer 토큰이 필요합니다.")
    return executor(action=action, simulation_id=simulation_id, actor_id=actor_id,
                    post_id=post_id, content=content, idempotency_key=idempotency_key,
                    token=token)


def like_post(**kwargs):
    return _execute("LIKE", **kwargs)


def create_comment(**kwargs):
    return _execute("COMMENT", **kwargs)


def repost_post(**kwargs):
    return _execute("REPOST", **kwargs)
