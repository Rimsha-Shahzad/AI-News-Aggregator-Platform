from datasketch import MinHash, MinHashLSH

def get_minhash(text: str) -> MinHash:
    m = MinHash(num_perm=128)
    for word in text.lower().split():
        m.update(word.encode("utf8"))
    return m

async def filter_agent(state: dict) -> dict:
    articles = state.get("raw_articles", [])
    lsh = MinHashLSH(threshold=0.7, num_perm=128)
    unique_articles = []
    for i, article in enumerate(articles):
        title = article.get("title", "")
        if not title or len(title) < 10:
            continue
        m = get_minhash(title)
        key = f"article_{i}"
        try:
            result = lsh.query(m)
            if result:
                continue  # duplicate, skip
            lsh.insert(key, m)
            unique_articles.append(article)
        except Exception:
            lsh.insert(key, m)
            unique_articles.append(article)
    print(f"Filter Agent: {len(articles)} → {len(unique_articles)} unique articles")
    return {**state, "filtered_articles": unique_articles}