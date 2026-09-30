# 행동 검증 툴 —: 아래 함수를 이 파일에 구현합니다.
# validate_action: 행동 종류·대상 게시글·댓글 필수값과 길이 검증.
# 연결: 완성한 함수를 __init__.py에서 import하고 해당 tool_groups에 등록하세요.

from collections.abc import Mapping

ACTIONS = frozenset({"LIKE", "COMMENT", "REPOST", "SKIP"})


def valid_id(value):
    return type(value) is int or isinstance(value, str) and bool(value.strip())


def same_id(left, right):
    return type(left) is type(right) and left == right


def validate_action(context, decision, *, max_comment_length=None):
    """제안을 변경하지 않는다. 길이 제한은 서버와 합의한 값을 주입한다."""
    if max_comment_length is not None and (type(max_comment_length) is not int or max_comment_length < 1):
        raise ValueError("max_comment_length는 양의 정수여야 합니다.")
    decision_id = decision.get("decision_id") if isinstance(decision, Mapping) else None

    def report(verdict, reasons):
        return {"decision_id": decision_id, "verdict": verdict, "reasons": reasons,
                "feedback": " ".join(reasons) if verdict != "APPROVE" else None}

    if not isinstance(context, Mapping) or not isinstance(context.get("event"), Mapping):
        return report("REJECT", ["신뢰할 수 있는 context.event가 필요합니다."])
    post_id = context["event"].get("post_id")
    if not valid_id(post_id) or context.get("retrieval_errors"):
        return report("REJECT", ["대상 정보가 없거나 조회 오류가 있습니다."])
    post = context.get("post")
    if not isinstance(post, Mapping) or not post or not isinstance(context.get("profile"), Mapping) or not context["profile"]:
        return report("REJECT", ["조회된 게시글과 참여자 성향이 필요합니다."])
    if post.get("deleted") or post.get("is_deleted"):
        return report("REJECT", ["삭제된 게시글입니다."])
    for key in ("id", "post_id"):
        if key in post and not same_id(post[key], post_id):
            return report("REJECT", ["조회 게시글과 노출 대상이 다릅니다."])
    if not isinstance(decision, Mapping):
        return report("REVISE", ["제안을 객체 형식으로 다시 생성하세요."])
    if "post_id" in decision and not same_id(decision["post_id"], post_id):
        return report("REJECT", ["제안의 대상 게시글이 노출된 게시글과 다릅니다."])
    reasons = []
    if not isinstance(decision_id, str) or not decision_id.strip():
        reasons.append("새 decision_id를 생성하세요.")
    if "post_id" not in decision:
        reasons.append("노출된 post_id를 포함하세요.")
    action = decision.get("action")
    if not isinstance(action, str) or action not in ACTIONS:
        reasons.append("action은 LIKE, COMMENT, REPOST, SKIP 중 하나여야 합니다.")
    if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
        reasons.append("행동 선택 이유 reason을 작성하세요.")
    content = decision.get("content")
    if action == "COMMENT":
        if not isinstance(content, str) or not content.strip():
            reasons.append("COMMENT에는 비어 있지 않은 댓글 본문이 필요합니다.")
        elif max_comment_length is not None and len(content) > max_comment_length:
            reasons.append(f"댓글을 {max_comment_length}자 이내로 줄이세요.")
    elif content is not None:
        reasons.append("COMMENT 이외의 content는 null이어야 합니다.")
    return report("REVISE", reasons) if reasons else report("APPROVE", [])
