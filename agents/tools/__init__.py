# 툴 연결 파일: 각자 툴 함수를 구현한 뒤 해당 import와 그룹 등록을 직접 작성하세요.
# 순서: tools/내파일.py 구현 → 아래 import 추가 → 해당 tool_groups에 추가 → main.py에서 에이전트에 전달 → 에이전트 run에서 호출.
# 아래는 연결 예시이며 전부 주석입니다. 구현한 함수의 import부터 활성화하고, 그룹에는 구현 완료된 함수만 넣으세요.
# import만 추가하면 호출되지 않습니다. 그룹 등록과 에이전트의 실제 호출까지 구현해야 연결이 끝납니다.

# [1] 담당 영역별 파일에서 여러 함수를 함께 import합니다.
# from .retrieval_tools import get_post, search_memories, get_profile_and_relationship
# from .critic_tools import validate_action
# from .action_tools import like_post, create_comment, repost_post
# from .memory_tools import save_memory, update_memory_result

# [2] 에이전트별 등록 — 아래는 모두 구현한 뒤의 모양이며, 미완성 함수는 빼고 등록하세요.
# tool_groups = {
#     "retrieval": [get_post, search_memories, get_profile_and_relationship],
#     "critic": [validate_action],
#     "action": [like_post, create_comment, repost_post],
#     "memory": [save_memory, update_memory_result],
# }
# PlanningAgent는 별도 툴 없이 모델 호출 함수를 사용합니다.
# 새 툴은 담당 영역 파일에 구현하고 위 import 목록과 해당 그룹에 함수 이름을 추가하세요.

# [3] main.py에서 받을 형태 — 아래 코드는 이 파일이 아니라 main.py의 구현 자리입니다.
# from .tools import tool_groups
# retrieval_agent = RetrievalAgent(tools=tool_groups["retrieval"])
# 위 생성자 형식은 제안입니다. 각 에이전트가 tools를 받아 run에서 사용하는 부분도 직접 구현하세요.
