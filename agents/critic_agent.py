"""
CriticAgent — 행동 검토 에이전트

어떤 에이전트인가요?
PlanningAgent의 행동 제안이 실행 가능한지 검토합니다.
잘못된 제안은 수정 요청하거나 거절하고, 통과한 제안만 ActionAgent로 보냅니다.

구현해야 하는 기능
1. 형식 검사: 허용 행동인지, 대상 게시글이 맞는지, 댓글이 비어 있지 않은지 확인합니다.
2. 정책 검사: 서버와 합의한 댓글 길이와 중복 행동 제한 등을 검사합니다.
3. 문맥 검사: 제안이 게시글·기억·참여자 성향과 일관되는지 검토합니다.
4. 결과 반환: APPROVE / REVISE / REJECT와 구체적인 사유를 반환합니다.
5. 수정 피드백: B가 무엇을 바꿔야 하는지 알 수 있게 설명합니다.

연결할 툴
- validate_action: 필수값, 행동 종류, 대상, 댓글 길이 등을 일반 코드로 검사.
- 모델 호출 함수: 필요할 때만 문맥·성향 일관성을 보조 검토.
툴 검사 결과와 모델 검토 결과를 아래 run에서 종합하세요.
중복 및 권한의 최종 보장은 서버에서도 해야 합니다.

받는 값
context, decision

돌려줄 값
critique: decision_id, verdict, reasons, feedback
검토한 decision_id를 반드시 함께 돌려줍니다.

다음 연결
APPROVE → ActionAgent
REVISE → PlanningAgent에 피드백 전달. 재계획은 main.py에서 최대 1회로 제한.
REJECT 또는 수정 한도 초과 → 실행 없이 SKIP 결과 기록.

주의할 점
제안을 직접 고친 뒤 승인하지 않습니다. B가 수정하면 다시 검사합니다.
시뮬레이션 페르소나의 편향과 구현 오류를 구분합니다.
사실성 검사를 추가할지는 실험 목적에 맞춰 별도로 정합니다.
"""

# TODO: class CriticAgent
# TODO: 검증 툴과 선택적인 모델 호출 함수를 전달받는 초기화 부분
# TODO: run(context, decision) → critique
# 아래에 구현하세요.

# 툴 연결: tools/__init__.py의 tool_groups["critic"]를 main.py에서 전달받아 이 에이전트의 run에서 호출하세요.

# 툴 구현 파일: tools/critic_tools.py에 관련 함수를 함께 작성하세요.
