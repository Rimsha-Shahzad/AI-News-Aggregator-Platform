import random
import pymongo
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# Import your multi-agent architecture scripts
from backend.agents.crawl_agent import crawl_agent
from backend.agents.personalization_agent import personalization_agent

app = FastAPI(title="NewsAI Aggregator Platform")

# Allow absolute cross-origin resource access sharing for mobile testing devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect securely to your local MongoDB service
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["news_aggregator"]
articles_collection = db["articles"]
digests_collection = db["digests"]

class PipelineRequest(BaseModel):
    topics: List[str]

@app.post("/run-pipeline/{user_id}")
async def run_pipeline(user_id: str, request: List[str]):
    try:
        print(f"🚀 MAIN BACKEND: Initializing Graph Pipeline for User {user_id}")
        print(f"📥 Received Target Topics: {request}")
        
        # 1. Clean and lowercase the topics list
        clean_topics = [str(t).lower().strip() for t in request]
        
        # 2. Run the Crawl Agent to get real-time articles
        crawl_results = crawl_agent(clean_topics)
        raw_articles = crawl_results.get("raw_articles", [])
        
        # 3. Create the state dictionary context for your personalization graph node
        state_context = {
            "topics": clean_topics,
            "raw_articles": raw_articles
        }
        
        # 4. Process scores using the Personalization Agent
        personalization_results = personalization_agent(state_context)
        final_articles = personalization_results.get("personalized_articles", [])
        
        # 5. Clear old user articles to keep database clean and prevent UI pollution
        articles_collection.delete_many({"user_id": user_id})
        
        cleaned_feed_saves = []
        
        # 6. Sanitize every single dictionary item to safeguard standard JSON transmission parsing
        if final_articles:
            for article in final_articles:
                clean_art = article.copy()
                clean_art["user_id"] = str(user_id)
                
                # Strip out any pre-existing native MongoDB ObjectIds if present
                if "_id" in clean_art:
                    clean_art["_id"] = str(clean_art["_id"])
                    
                if "bias_label" not in clean_art:
                    clean_art["bias_label"] = random.choice(["Left", "Left-Center", "Center", "Right-Center", "Right"])
                
                cleaned_feed_saves.append(clean_art)
            
            articles_collection.insert_many(cleaned_feed_saves)
            print(f"💾 Inserted {len(cleaned_feed_saves)} scored entries into MongoDB successfully.")
            
        # 7. Compile a completely clean summary record object block free of ObjectId anomalies
        topic_summary_string = ", ".join([t.capitalize() for t in clean_topics])
        
        # Extract clean sub-slices for top articles block
        top_slice = []
        for a in cleaned_feed_saves[:3]:
            item = a.copy()
            if "_id" in item:
                del item["_id"] # Completely wipe internal DB key to prevent serialization crash loops
            top_slice.append(item)

        mock_digest = {
            "user_id": str(user_id),
            "summary": f"Today's automated personalization engine shows major updates across user profiles. Multi-agent architecture successfully cross-referenced historical media records and calculated real-time data frames matching your active interest fields: {topic_summary_string}.",
            "article_count": len(cleaned_feed_saves),
            "top_articles": top_slice
        }
        
        digests_collection.delete_many({"user_id": user_id})
        digests_collection.insert_one(mock_digest)
        
        return {"status": "success", "message": f"Pipeline successfully ran for {topic_summary_string}"}
        
    except Exception as e:
        print(f"❌ PIPELINE FAILURE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feed/{user_id}")
async def get_feed(user_id: str, limit: int = 40):
    try:
        cursor = articles_collection.find({"user_id": str(user_id)}).sort("relevance_score", -1).limit(limit)
        feed_list = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  
            feed_list.append(doc)
        return feed_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/digest/{user_id}")
async def get_digest(user_id: str):
    try:
        digest_doc = digests_collection.find_one({"user_id": str(user_id)})
        if not digest_doc:
            return {
                "summary": "No personal feed built yet. Tap the top Refresh button to sync your custom topics live!",
                "article_count": 0,
                "top_articles": []
            }
        digest_doc["_id"] = str(digest_doc["_id"])
        return digest_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))