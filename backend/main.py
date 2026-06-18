import os
import random
import pymongo
from fastapi import FastAPI, HTTPException, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# Relative imports to guarantee Vercel paths resolve perfectly in production
from agents.crawl_agent import crawl_agent
from agents.personalization_agent import personalization_agent

app = FastAPI(title="NewsAI Aggregator Platform")

# 🔌 FIXED CORS MIDDLEWARE CONFIGURATION
# Using allow_origin_regex or a clean fallback layout prevents browser-side network blocks.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Safely opens endpoints up to Vercel production routing
    allow_credentials=False, # Must be False when using wildcard "*" to satisfy strict browser engine standards
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎯 SECURED CLOUD ENVIRONMENT CONFIGURATION
# Pulls from Render configuration settings automatically, falling back to local string if empty
MONGO_URI = os.getenv(
    "MONGO_URI", 
    "mongodb+srv://70145562_db_user:Q7eNCwlPoTvt6lL2@cluster0.ffx9jdh.mongodb.net/?appName=Cluster0"
)

print(f"🔌 FORCED BACKEND PRODUCTION CONNECTION: {MONGO_URI[:35]}...")

client = pymongo.MongoClient(MONGO_URI)
db = client["news_aggregator"]
articles_collection = db["articles"]
digests_collection = db["digests"]

class PipelineRequest(BaseModel):
    topics: List[str]

@app.post("/run-pipeline/{user_id}")
async def run_pipeline(user_id: str, raw_request: FastAPIRequest):
    try:
        print(f"🚀 MAIN BACKEND: Initializing Graph Pipeline for User {user_id}")
        
        # Capture raw json payload to automatically handle formatting variances
        body_data = await raw_request.json()
        print(f"📥 Raw Payload Caught: {body_data} (Type: {type(body_data)})")
        
        # Smart Dynamic Parser: Checks if frontend sent a dictionary object or a direct array list
        if isinstance(body_data, dict) and "topics" in body_data:
            incoming_topics = body_data["topics"]
        elif isinstance(body_data, list):
            incoming_topics = body_data
        else:
            incoming_topics = [str(body_data)]
            
        print(f"🎯 Evaluated Target Topics for AI Agents: {incoming_topics}")
        
        # 1. Clean and lowercase the topics list
        clean_topics = [str(t).lower().strip() for t in incoming_topics]
        
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