import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# --- FIX DOTENV PATH RESOLUTION ---
# Find the exact folder where THIS database.py file lives, and look for .env right next to it
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path=env_path)
# ----------------------------------

# Debug prints to ensure variables are loading successfully
print(f"--- DATABASE DEBUG ---")
print(f"MONGODB_URL loaded: {'Yes' if os.getenv('MONGODB_URL') else 'No (None)'}")
print(f"DB_NAME loaded: {os.getenv('DB_NAME')}")
print(f"----------------------")

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("DB_NAME") or "news_aggregator_db"]  # Added a fallback name string to prevent type crashes!

articles_col = db["articles"]
users_col = db["users"]
digests_col = db["digests"]