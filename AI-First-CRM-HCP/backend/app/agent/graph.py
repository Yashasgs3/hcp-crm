from langgraph.graph import StateGraph, END

from app.agent.state import AgentState

from app.agent.nodes import planner_node
from app.agent.nodes import response_node

from app.agent.router import router

# Tool Nodes
from app.tools.log_interaction import log_interaction_node
from app.tools.edit_interaction import edit_interaction_node
from app.tools.followup_tool import followup_node
from app.tools.hcp_insights import insights_node
from app.tools.material_recommendation import material_node


builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)

builder.add_node("log_interaction", log_interaction_node)

builder.add_node("edit_interaction", edit_interaction_node)

builder.add_node("followup_tool", followup_node)

builder.add_node("hcp_insights", insights_node)

builder.add_node("material_recommendation", material_node)

builder.add_node("response", response_node)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "planner",
    router,
    {
        "log_interaction": "log_interaction",
        "edit_interaction": "edit_interaction",
        "followup_tool": "followup_tool",
        "hcp_insights": "hcp_insights",
        "material_recommendation": "material_recommendation",
        "response": "response",
        "end": END
    }
)

builder.add_edge("log_interaction", "response")

builder.add_edge("edit_interaction", "response")

builder.add_edge("followup_tool", "response")

builder.add_edge("hcp_insights", "response")

builder.add_edge("material_recommendation", "response")

builder.add_edge("response", END)

graph = builder.compile()
