"""조회→계획 연결과 검토·기억 에이전트 생성.

ActionAgent 및 승인/재계획/실행/기억 기록을 포함한 전체 실행 루프는 아직 없다.
retrieve_and_plan은 조회 오류가 있으면 모델을 호출하지 않고 decision=None을 반환한다.
"""
from .critic_agent import CriticAgent
from .memory_agent import MemoryAgent
from .tools import tool_groups
from .retrieval_agent import RetrievalAgent
from .planning_agent import PlanningAgent


def create_retrieval_agent(**kwargs):
    return RetrievalAgent(tools=tool_groups["retrieval"], **kwargs)


def retrieve_and_plan(event, *, model_call, **retrieval_options):
    """조회에 성공한 경우에만 계획한다. 서버 쓰기 및 행동 실행은 하지 않는다."""
    context = create_retrieval_agent(**retrieval_options).run(event)
    if context["retrieval_errors"]:
        return {"context": context, "decision": None}
    return {"context": context, "decision": PlanningAgent(model_call).run(context)}


def create_review_memory_agents(*, model_call=None, db_path=None, max_comment_length=None):
    """통합 흐름에서 사용할 두 에이전트에 등록된 툴을 연결한다."""
    return (
        CriticAgent(tools=tool_groups["critic"], model_call=model_call,
                    max_comment_length=max_comment_length),
        MemoryAgent(tools=tool_groups["memory"], db_path=db_path),
    )
