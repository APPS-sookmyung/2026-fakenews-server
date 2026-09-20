"""
MemoryAgent — 경험 기록 에이전트
담당: 통합 담당 + A

어떤 에이전트인가요?
이번 게시글에 실제로 어떻게 반응했는지 저장합니다.
저장한 경험은 다음 노출에서 RetrievalAgent가 조회합니다.
초기에는 일반 저장 코드로 구현하고, 필요하면 나중에 모델 요약을 추가합니다.

구현해야 하는 기능
1. 경험 구성: 어떤 글을 보고 무엇을 제안하고 실제로 무엇을 했는지 정리합니다.
2. 결과 구분: 성공, 실패, SKIP, 성공 여부 불명확을 각각 기록합니다.
3. 기억 저장: 실험 ID와 참여자 ID를 함께 저장해 기억이 섞이지 않게 합니다.
4. 중복 방지: 같은 노출의 같은 결과를 여러 번 기억으로 생성하지 않습니다.
5. 저장 재시도: 기록 실패 시 기록 저장만 재시도합니다.
6. 결과 보정: UNKNOWN이 나중에 확정되면 기존 기록을 갱신합니다.

연결할 툴
- save_memory: 경험 저장 및 중복 저장 방지
- update_memory_result: 불명확했던 실행 결과 보정
조회 툴 search_memories와 같은 저장소 및 데이터 형식을 사용하세요.

받는 값
event, context, decision, critique, result
초기 조회/계획 단계에서 종료했다면 없는 값은 None이며 종료 사유를 기록합니다.

돌려줄 값
memory_result: status, memory_id, error

다음 연결
ActionAgent 또는 main.py의 중단 경로 → MemoryAgent → 종료
저장된 경험 → 다음 노출의 RetrievalAgent

주의할 점
계획한 행동을 실제 성공 행동처럼 저장하지 않습니다.
기억 저장 실패 때문에 좋아요/댓글/재게시를 다시 실행하지 않습니다.
"""

# TODO: class MemoryAgent
# TODO: 기억 저장/수정 툴을 전달받는 초기화 부분
# TODO: run(event, context, decision, critique, result) → memory_result
# 아래에 구현하세요.

# 툴 연결: tools/__init__.py의 tool_groups["memory"]를 main.py에서 전달받아 이 에이전트의 run에서 호출하세요.

# 툴 구현 파일: tools/memory_tools.py에 관련 함수를 함께 작성하세요.
