# 기억 관리 툴 : 아래 두 함수를 이 파일에 함께 구현합니다.
# save_memory: 실험·참여자별 실제 행동 결과 저장.
# update_memory_result: 성공 여부가 불명확했던 실행 결과 보정.
# 연결: 완성한 함수를 __init__.py에서 import하고 해당 tool_groups에 등록하세요.

"""SQLite 경험 저장소. 같은 노출은 하나의 기록이며 UNKNOWN만 확정 결과로 보정한다."""

import hashlib
import json
import os
import sqlite3
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .critic_tools import ACTIONS, same_id, valid_id


def memory_key(event):
    if not isinstance(event, Mapping):
        raise ValueError("event가 필요합니다.")
    for key in ("simulation_id", "actor_id", "exposure_id", "post_id"):
        if not valid_id(event.get(key)):
            raise ValueError(f"event.{key}가 필요합니다.")
    identity = [event[k] for k in ("simulation_id", "actor_id", "exposure_id")]
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()


def normalize_result(decision, result):
    """누락 결과는 성공을 추론하지 않는다. 계획과 다른 실행 결과는 저장을 거부한다."""
    if decision is not None and not isinstance(decision, Mapping):
        raise ValueError("decision은 객체 또는 None이어야 합니다.")
    if result is None:
        return {"decision_id": decision.get("decision_id") if decision else None,
                "action": decision.get("action") if decision else None,
                "status": "UNKNOWN", "resource_id": None,
                "error": "실행 결과가 전달되지 않았습니다.", "idempotency_key": None}
    if not isinstance(result, Mapping):
        raise ValueError("result는 객체여야 합니다.")
    action, status = result.get("action"), result.get("status")
    missing_execution = decision is None and action is None and status == "UNKNOWN"
    if not missing_execution and (not isinstance(action, str) or action not in ACTIONS):
        raise ValueError("실행 결과의 action이 올바르지 않습니다.")
    if not isinstance(status, str) or status not in {"SUCCESS", "FAILED", "UNKNOWN", "SKIPPED"}:
        raise ValueError("실행 결과의 status가 올바르지 않습니다.")
    if action == "SKIP" and status != "SKIPPED":
        raise ValueError("SKIP의 실행 결과는 SKIPPED여야 합니다.")
    if decision is not None:
        if status != "SKIPPED" and (not isinstance(decision.get("decision_id"), str) or not decision["decision_id"].strip()):
            raise ValueError("실행 결과를 연결할 decision_id가 필요합니다.")
        if not same_id(result.get("decision_id"), decision.get("decision_id")):
            raise ValueError("실행 결과의 decision_id가 제안과 다릅니다.")
        if status != "SKIPPED" and action != decision.get("action"):
            raise ValueError("실행 행동이 제안과 다릅니다.")
        if status == "SUCCESS" and action == "COMMENT" and (
            not isinstance(decision.get("content"), str) or not decision["content"].strip()
        ):
            raise ValueError("성공한 댓글의 본문이 필요합니다.")
    elif status != "SKIPPED" and not missing_execution:
        raise ValueError("실행 결과를 검증할 decision이 필요합니다.")
    return {key: result.get(key) for key in (
        "decision_id", "action", "status", "resource_id", "error", "idempotency_key")}


def apply_result(memory, result):
    memory["result"] = result
    succeeded = result["status"] == "SUCCESS"
    memory["executed_action"] = result["action"] if succeeded else None
    memory["executed_content"] = (memory.get("decision") or {}).get("content") if succeeded and result["action"] == "COMMENT" else None
    labels = {"SUCCESS": "실행 성공", "FAILED": "실행 실패", "UNKNOWN": "실행 여부 불명확", "SKIPPED": "실행 생략"}
    memory["summary"] = f"게시글 {memory['event']['post_id']}: {result['action']} / {labels[result['status']]}"
    if result.get("error"):
        memory["summary"] += f" ({result['error']})"
    return memory


@contextmanager
def connection(db_path=None):
    path = Path(db_path or os.environ.get("AGENT_MEMORY_DB") or Path(__file__).resolve().parents[1] / "data" / "memories.sqlite3")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS memories (
            memory_id TEXT PRIMARY KEY, simulation_id TEXT NOT NULL,
            actor_id TEXT NOT NULL, payload TEXT NOT NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS memories_actor ON memories(simulation_id, actor_id)")
        conn.commit()
        with conn:
            yield conn
    finally:
        conn.close()


def _write(conn, memory):
    conn.execute("INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?)", (
        memory["memory_id"], json.dumps(memory["event"]["simulation_id"]),
        json.dumps(memory["event"]["actor_id"]), json.dumps(memory, ensure_ascii=False)))


def _merge(existing, incoming):
    if existing["event"] != incoming["event"] or existing.get("decision") != incoming.get("decision"):
        raise ValueError("동일 노출에 서로 다른 대상 또는 제안이 있습니다.")
    old, new = existing["result"], incoming["result"]
    if old == new:
        return "DUPLICATE", existing
    if old["status"] != "UNKNOWN" or new["status"] not in {"SUCCESS", "FAILED", "SKIPPED"}:
        raise ValueError("확정된 결과를 덮어쓰거나 불명확한 결과로 변경할 수 없습니다.")
    if old.get("idempotency_key") is not None and old["idempotency_key"] != new.get("idempotency_key"):
        raise ValueError("보정 결과의 요청 키가 다릅니다.")
    apply_result(existing, new)
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    return "UPDATED", existing


def save_memory(memory, *, db_path=None):
    # JSON 왕복으로 호출자가 저장 후 원본을 변경해도 기록이 영향을 받지 않게 한다.
    memory = json.loads(json.dumps(memory, ensure_ascii=False))
    memory_id = memory_key(memory["event"])
    memory["memory_id"] = memory_id
    decision = memory.get("decision")
    if decision and not same_id(decision.get("post_id"), memory["event"]["post_id"]):
        # 잘못된 제안도 거절 경험으로 남길 수 있지만 실행 성공으로 저장할 수 없다.
        if memory["result"]["status"] != "SKIPPED":
            raise ValueError("제안의 대상과 노출 대상이 다릅니다.")
    apply_result(memory, normalize_result(decision, memory["result"]))
    now = datetime.now(timezone.utc).isoformat()
    memory["created_at"] = memory["updated_at"] = now
    with connection(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT payload FROM memories WHERE memory_id = ?", (memory_id,)).fetchone()
        status = "SAVED"
        if row:
            status, memory = _merge(json.loads(row[0]), memory)
        if status != "DUPLICATE":
            _write(conn, memory)
    return {"status": status, "memory_id": memory_id, "error": None}


def update_memory_result(event, result, *, db_path=None):
    """노출 및 참여자 범위를 확인한 뒤 UNKNOWN 기록만 보정한다."""
    memory_id = memory_key(event)
    with connection(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT payload FROM memories WHERE memory_id = ?", (memory_id,)).fetchone()
        if not row:
            raise ValueError("보정할 기억이 없습니다.")
        existing = json.loads(row[0])
        if existing["event"] != dict(event):
            raise ValueError("기억의 노출 대상이 다릅니다.")
        incoming = dict(existing)
        incoming["result"] = normalize_result(existing.get("decision"), result)
        status, memory = _merge(existing, incoming)
        if status != "DUPLICATE":
            _write(conn, memory)
    return {"status": status, "memory_id": memory_id, "error": None}


def search_memories(simulation_id, actor_id, *, post_id=None, limit=20, db_path=None):
    """동일 실험·참여자의 최신 경험 조회. post_id가 있으면 해당 글로 제한한다."""
    if not valid_id(simulation_id) or not valid_id(actor_id):
        raise ValueError("실험 및 참여자 ID가 필요합니다.")
    if type(limit) is not int or limit < 1:
        raise ValueError("limit는 양의 정수여야 합니다.")
    with connection(db_path) as conn:
        rows = conn.execute("SELECT payload FROM memories WHERE simulation_id = ? AND actor_id = ?",
                            (json.dumps(simulation_id), json.dumps(actor_id))).fetchall()
    memories = [json.loads(row[0]) for row in rows]
    if post_id is not None:
        memories = [m for m in memories if same_id(m["event"]["post_id"], post_id)]
    return sorted(memories, key=lambda m: (m["updated_at"], m["memory_id"]), reverse=True)[:limit]
