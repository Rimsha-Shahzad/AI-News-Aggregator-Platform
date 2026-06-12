import random
from typing import Dict, Any

def personalization_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Personalization Agent: Evaluates and ranks ingested news metadata.
    Scores articles dynamically based on matching current active interest tags.
    """
    print("\n==================================================")
    print("🎯 PERSONALIZATION AGENT EVALUATING USER INTERESTS")
    print(" -> Processing weights for selected user profile...")
    print("==================================================\n")
    
    raw_articles = state.get("raw_articles", [])
    if not raw_articles:
        raw_articles = state.get("filtered_articles", [])
        
    active_topics = state.get("topics", [])
    active_topics_clean = [str(t).lower().strip() for t in active_topics]
        
    ranked_articles = []
    
    for article in raw_articles:
        article_topic = str(article.get("topic", "")).lower().strip()
        title_lower = article.get("title", "").lower()
        
        # Cross check if this article matches what the user is selecting
        is_true_match = article_topic in active_topics_clean
        
        if is_true_match:
            simulated_score = round(random.uniform(0.88, 0.98), 2)
            if any(topic in title_lower for topic in active_topics_clean):
                simulated_score = round(random.uniform(0.94, 0.99), 2)
        else:
            simulated_score = round(random.uniform(0.40, 0.55), 2)
            
        updated_article = article.copy()
        updated_article["relevance_score"] = simulated_score
        ranked_articles.append(updated_article)
        
    ranked_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    print(f"✅ Personalization Agent: Successfully ranked {len(ranked_articles)} entries contextually.")
    
    return {"personalized_articles": ranked_articles}