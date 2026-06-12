import asyncio
# Add backend. to specify the folder location
from backend.database import articles_col, digests_col

async def test_connection():
    print("Connecting to database...")
    try:
        # Count documents in your collections
        article_count = await articles_col.count_documents({})
        digest_count = await digests_col.count_documents({})
        
        print("\n=== DATABASE CONNECTION SUCCESSFUL ===")
        print(f"Total articles found: {article_count}")
        print(f"Total digests found: {digest_count}")
        
        # Check if we can pull one article
        sample_article = await articles_col.find_one({})
        if sample_article:
            print("\nSample Article Title:", sample_article.get("title"))
        else:
            print("\n⚠️ Warning: The 'articles' collection is completely empty!")
            
        print("======================================\n")
    except Exception as e:
        print(f"\n❌ Connection Error: {e}\n")

asyncio.run(test_connection())