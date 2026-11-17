"""구현된 툴 등록. 그룹 등록과 별개로 각 Agent.run이 실제 툴을 호출한다."""
from .critic_tools import validate_action
from .memory_tools import save_memory, update_memory_result
from .retrieval_tools import get_post, get_profile_and_relationship, search_memories

tool_groups = {
    "critic": [validate_action],
    "memory": [save_memory, update_memory_result],
    "retrieval": [get_post, get_profile_and_relationship, search_memories],
}
