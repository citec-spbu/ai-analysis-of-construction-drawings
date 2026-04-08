from langgraph.graph import StateGraph, END

from app.agent.nodes import (
    node_agent,
    node_tools,
    node_instructor,
    node_retrieve
)
from app.agent.state import AgentState


def build_graph(agent, tools, instructor_client, retriever):

    workflow = StateGraph(AgentState)

    # -----------------------
    # nodes
    # -----------------------

    workflow.add_node("retrieve", lambda s: node_retrieve(s, retriever))
    workflow.add_node("agent", lambda s: node_agent(s, agent))
    workflow.add_node("tools", lambda s: node_tools(s, tools))
    workflow.add_node("instructor", lambda s: node_instructor(s, instructor_client))

    # -----------------------
    # entry
    # -----------------------

    workflow.set_entry_point("retrieve")

    # -----------------------
    # edges
    # -----------------------

    workflow.add_edge("retrieve", "agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("instructor", END)

    return workflow.compile()

def should_continue(state: AgentState):
    """
    Решает: идти в tools или завершать
    """

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "instructor"