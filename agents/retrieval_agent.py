"""
RetrievalAgent — 상황 수집 에이전트
담당: A

어떤 에이전트인가요?
게시글에 반응하기 전에 필요한 정보를 모읍니다.
노출된 글, 이 참여자의 과거 기억, 작성자와의 관계, 참여자의 성향을
한데 묶어 PlanningAgent에 전달합니다.

구현해야 하는 기능
1. 게시글 조회: 본문, 작성자, 작성 시각, 삭제 여부를 가져옵니다.
2. 기억 조회: 같은 실험·참여자의 과거 반응과 관련 기억을 검색합니다.
3. 관계·성향 조회: 참여자의 페르소나, 관심사, 작성자와의 관계를 가져옵니다.
4. 정보 정리: 조회 결과를 context로 묶고 출처와 누락 정보를 표시합니다.
5. 예외 처리: 기억이 없는 정상 상황과 조회 실패를 구분합니다.
   게시글이 없거나 필수 성향을 읽지 못하면 실행 중단 사유를 반환합니다.

연결할 툴
- get_post: 게시글 조회. 현재 서버의 GET /api/posts/{postId} 연결.
- search_memories: 실험 ID와 참여자 ID로 기억 조회. 저장소는 구현 필요.
- get_profile_and_relationship: 관계·성향 조회. 서버 명세는 구현 전 합의 필요.
이 툴을 완성하면 아래 run의 정보 수집 부분에서 호출하세요.
조회는 정해진 코드로 시작해도 됩니다. LLM 호출은 필수가 아닙니다.

받는 값
event: simulation_id, actor_id, post_id, exposure_id
actor_id는 시뮬레이션 참여자이며 로그인 사용자 ID와 같다고 가정하지 않습니다.

돌려줄 값
context: event, post, memories, profile, relationship, retrieval_errors
실패를 빈 데이터로 숨기지 않습니다.

다음 연결
main.py → RetrievalAgent → PlanningAgent
context에 필수 조회 오류가 있으면 main.py에서 종료 결과를 기록합니다.
"""

# TODO: class RetrievalAgent
# TODO: 필요한 조회 툴을 전달받는 초기화 부분
# TODO: run(event) → context
# 아래에 구현하세요.

# 툴 연결: tools/__init__.py의 tool_groups["retrieval"]를 main.py에서 전달받아 이 에이전트의 run에서 호출하세요.

# 툴 구현 파일: tools/retrieval_tools.py에 관련 함수를 함께 작성하세요.
