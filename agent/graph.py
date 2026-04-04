from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    generate_code_node,
    execute_code_node,
    analyze_error_node,
    should_continue
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("generate_code", generate_code_node)
    graph.add_node("execute_code", execute_code_node)
    graph.add_node("analyze_error", analyze_error_node)

    graph.set_entry_point("generate_code")

    graph.add_edge("generate_code", "execute_code")

    graph.add_conditional_edges(
        "execute_code",
        should_continue,
        {
            "done": END,
            "failed": END,
            "fix": "analyze_error"
        }
    )

    graph.add_edge("analyze_error", "execute_code")

    return graph.compile()


agent = build_graph()