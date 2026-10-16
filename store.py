import chromadb

def get_collection():
    client = chromadb.PersistentClient(path="Chroma_db")
    return client.get_or_create_collection("docs")

def source_exists(name):
    res = get_collection().get(where={"source": name}, limit=1)
    return len(res["ids"]) > 0

def list_sources():
    res = get_collection().get(include=["metadatas"])
    return sorted({m["source"] for m in res["metadatas"] if m and "source" in m})

def delete_source(name):
    get_collection().delete(where={"source": name})

def store(chunks, source):
    col = get_collection()   
    col.upsert(
        ids=[f"{source}-{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"source": source, "chunk": i} for i in range(len(chunks))],
    )
    return col.count()

def search(question, k=3):
    col = get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[question], n_results=min(k, col.count()))
    hits = []
    for text, meta, dist in zip(res["documents"][0], 
                                res["metadatas"][0], 
                                res["distances"][0]):
        hits.append({"text": text, "source": meta["source"], "chunk": meta["chunk"], "distance": dist})
    return hits
