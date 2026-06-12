from fastapi import APIRouter
from database import digests_col

router = APIRouter()

@router.get("/digest/{user_id}")
async def get_digest(user_id: str):
    digest = await digests_col.find_one(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("date", -1)]
    )
    if not digest:
        return {"error": "No digest found. Run /run-pipeline first."}
    return digest

@router.get("/digest/{user_id}/history")
async def get_digest_history(user_id: str):
    cursor = digests_col.find(
        {"user_id": user_id},
        {"_id": 0, "top_articles": 0}
    ).sort("date", -1).limit(7)
    history = await cursor.to_list(length=7)
    return {"history": history}