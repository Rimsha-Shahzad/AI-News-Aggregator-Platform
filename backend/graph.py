from langgraph.graph import StateGraph, END
from agents.crawl_agent import crawl_agent
from agents.filter_agent import filter_agent
from agents.personalization_agent import personalization_agent
from agents.bias_agent import bias_agent
from agents.digest_agent import digest_agent
from typing import TypedDict, List, Optional, Any

class AgentState(TypedDict):
    user_id: str
    topics: List[str]
    user_preferences: dict
    raw_articles: List[Any]
    filtered_articles: List[Any]
    personalized_articles: List[Any]
    bias_labeled_articles: List[Any]
    digest: Optional[dict]
    summary: Optional[str]

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("crawl", crawl_agent)
    graph.add_node("filter", filter_agent)
    graph.add_node("personalize", personalization_agent)
    graph.add_node("bias", bias_agent)
    # Fixed naming conflict by changing node string to 'digest_node'
    graph.add_node("digest_node", digest_agent)
    
    graph.set_entry_point("crawl")
    graph.add_edge("crawl", "filter")
    graph.add_edge("filter", "personalize")
    graph.add_edge("personalize", "bias")
    graph.add_edge("bias", "digest_node")
    graph.add_edge("digest_node", END)
    return graph.compile()

pipeline = build_graph()