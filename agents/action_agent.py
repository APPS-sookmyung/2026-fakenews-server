"""
ActionAgent — 행동 실행 에이전트

어떤 에이전트인가요?
검토를 통과한 행동을 실제 서버 API로 실행합니다.
이름은 Agent지만 추가 LLM 판단 없이 정해진 함수를 호출하는 실행 모듈입니다.

구현해야 하는 기능
1. 승인 확인: APPROVE인지, 승인된 decision_id가 현재 제안과 같은지 확인합니다.
2. 행동 분기: LIKE는 좋아요, COMMENT는 댓글, REPOST는 재게시 툴을 호출합니다.
3. SKIP 처리: 서버 쓰기 호출 없이 SKIPPED 결과를 만듭니다.
4. 중복 방지: 같은 노출 재처리에는 동일 요청 키를 사용합니다.
5. 결과 정리: 성공, 확정 실패, 성공 여부 불명확을 구분합니다.
6. 인증 처리: 신뢰된 참여자/실험 정보와 서버 인증 규칙에 맞게 실행합니다.

연결할 툴
- like_post: 좋아요 API
- create_comment: 댓글 API
- repost_post: 재게시 API
완성한 툴은 아래 run의 action별 분기에 연결하세요.
현재 서버에는 관련 엔티티만 있고 세 API는 아직 없습니다.
일반 게시글 작성 API로 대체하지 말고 API 명세를 합의한 뒤 연결합니다.

받는 값
event, decision, critique

돌려줄 값
result: decision_id, action, status, resource_id, error, idempotency_key
status: SUCCESS / FAILED / UNKNOWN / SKIPPED

다음 연결
CriticAgent → ActionAgent → MemoryAgent

주의할 점
댓글 본문을 실행 직전에 새로 생성하거나 수정하지 않습니다.
요청 키는 simulation_id + actor_id + exposure_id를 기준으로 안정적으로 생성합니다.
서버도 같은 키의 중복 실행 방지와 결과 조회를 지원해야 합니다.
타임아웃은 UNKNOWN으로 남기고 성공 여부를 확인하기 전 무조건 재전송하지 않습니다.
"""

# TODO: class ActionAgent
# TODO: 좋아요/댓글/재게시 툴을 전달받는 초기화 부분
# TODO: run(event, decision, critique) → result
# 아래에 구현하세요.

# 툴 연결: tools/__init__.py의 tool_groups["action"]를 main.py에서 전달받아 이 에이전트의 run에서 호출하세요.

# 툴 구현 파일: tools/action_tools.py에 관련 함수를 함께 작성하세요.
