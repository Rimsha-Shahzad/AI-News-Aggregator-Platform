import feedparser
import ssl
import urllib.parse
from typing import List, Dict, Any

if not hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def crawl_agent(topics: List[str]) -> Dict[str, Any]:
    """
    Crawl Agent: Ingests real-time data from Google News RSS streams.
    Optimized with clean fallback search terms to ensure data is always returned.
    """
    print("\n==================================================")
    print("🤖 CRAWL AGENT STARTING INGESTION")
    print(f" -> Active search topics requested: {topics}")
    print("==================================================\n")
    
    raw_articles = []
    chosen_topics = topics if topics else ["technology", "world", "science"]
    
    # High-yield keyword mappings to prevent zero-result drops from RSS
    topic_mapping = {
        "weather": "weather forecast",
        "forecast": "weather forecast",
        "space": "space nasa",
        "finance": "finance business",
        "sports": "sports",
        "gaming": "video games"
    }
    
    for topic in chosen_topics:
        clean_topic = topic.lower().strip()
        search_query = topic_mapping.get(clean_topic, clean_topic)
        encoded_topic = urllib.parse.quote(search_query)
        
        rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            print(f"📡 Querying RSS for '{search_query}'... Found {len(feed.entries)} entries.")
            
            for entry in feed.entries[:15]:  
                article = {
                    "title": entry.get("title", "Untitled News Story"),
                    "url": entry.get("link", "https://example.com"),
                    "source": entry.get("source", {}).get("text", "Global Media Feed"),
                    "published": entry.get("published", ""),
                    "topic": clean_topic  # Strictly lowercased to map beautifully to frontend
                }
                raw_articles.append(article)
        except Exception as e:
            print(f"❌ Error crawling RSS for topic '{topic}': {e}")
            
    print(f"\n✅ Crawl Agent successfully collected {len(raw_articles)} total articles.")
    return {"raw_articles": raw_articles}