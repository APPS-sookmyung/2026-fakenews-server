"""
에이전트 연결 자리 — 통합 담당

파일별 에이전트
- retrieval_agent.py / RetrievalAgent: 게시글·기억·관계·성향 수집
- planning_agent.py / PlanningAgent: 행동과 댓글 제안
- critic_agent.py / CriticAgent: 제안 검토 및 수정 요청
- action_agent.py / ActionAgent: 승인된 행동 실행
- memory_agent.py / MemoryAgent: 실제 결과 저장

전체 순서
게시글 노출 → RetrievalAgent → PlanningAgent → CriticAgent
→ ActionAgent → MemoryAgent → 종료

여기에 구현할 기능
1. 각 에이전트가 사용할 툴/모델 호출 함수를 준비하고 전달합니다.
2. event를 받아 RetrievalAgent를 호출합니다.
3. context를 PlanningAgent에, decision을 CriticAgent에 전달합니다.
4. APPROVE이면 ActionAgent를 호출합니다.
5. REVISE이면 피드백을 PlanningAgent에 전달하고 다시 검토합니다.
   재계획은 최대 1회이며 이전 승인은 무효화합니다.
6. REJECT 또는 수정 한도 초과이면 쓰기 API 없이 SKIPPED 결과를 만듭니다.
7. 모든 종료 경로에서 실제 결과/오류를 MemoryAgent에 전달합니다.
8. 모델 출력 오류나 필수 정보 조회 실패 시 실행을 중단합니다.

툴은 어떻게 연결하나요?
각 에이전트 파일의 '연결할 툴'에 적힌 함수를 구현한 뒤,
tools/__init__.py에 import와 tool_groups 등록을 직접 추가한 뒤,
이 파일에서 해당 그룹을 에이전트에 전달하고 에이전트의 run 안에서 호출합니다.
별도 등록 프레임워크는 아직 정하지 않습니다.

현재 상태
PlanningAgent는 구현되었으며 planning_example.py에서 단독 예제를 실행할 수 있습니다.
나머지 에이전트/서버 호출 및 전체 실행 진입점은 미구현입니다.
"""

# TODO: 각 에이전트 import
# TODO: 툴/모델 준비 및 에이전트 생성
# TODO: run(event) — 위 순서와 분기 연결
# 아래에 구현하세요.


# 툴 연결: from .tools import tool_groups를 작성하고 각 그룹을 해당 에이전트에 전달하세요(연결 완료 후 저장소 루트에서 python -m agents.main 방식 사용).
