from fastapi import APIRouter
from database import articles_col, users_col

router = APIRouter()

@router.get("/feed/{user_id}")
async def get_feed(user_id: str, limit: int = 20):
    # Removed {"user_id": user_id} so your local fallback data can safely render 
    # on your screen without needing strict profile mapping matches.
    cursor = articles_col.find(
        {},
        {"_id": 0, "embedding": 0}
    ).sort("relevance_score", -1).limit(limit)
    
    articles = await cursor.to_list(length=limit)
    return {"user_id": user_id, "articles": articles}

@router.post("/preferences/{user_id}")
async def set_preferences(user_id: str, preferences: dict):
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": preferences},
        upsert=True
    )
    return {"status": "saved"}