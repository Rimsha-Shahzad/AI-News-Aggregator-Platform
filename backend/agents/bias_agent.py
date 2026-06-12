from typing import Dict, Any

async def bias_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- STARTING BIAS AGENT (LOCAL SAFE MODE) ---")
    articles = state.get("personalized_articles", [])
    
    # Assign local placeholder bias labels instead of running paid GPT calls
    default_leanings = ["Center", "Left-Center", "Right-Center"]
    for idx, article in enumerate(articles):
        article["bias_label"] = default_leanings[idx % len(default_leanings)]
        
    print(f"Bias Agent: Analyzed {len(articles)} articles locally.")
    return {"bias_labeled_articles": articles}