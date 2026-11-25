import chromadb

_client = chromadb.PersistentClient(path="Chroma_db")


def get_collection():
    return _client.get_or_create_collection("docs")


def source_exists(name):
    res = get_collection().get(where={"source": name}, limit=1)
    return len(res["ids"]) > 0


def get_source_hash(name):
    res = get_collection().get(where={"source": name}, limit=1,
                               include=["metadatas"])
    if not res["ids"]:
        return None
    return res["metadatas"][0].get("hash")


def list_sources():
    res = get_collection().get(include=["metadatas"])
    return sorted({m["source"] for m in res["metadatas"] if m and "source" in m})


def delete_source(name):
    get_collection().delete(where={"source": name})


def get_chunks(name):
    res = get_collection().get(where={"source": name},
                               include=["documents", "metadatas"])
    items = [{"chunk": m["chunk"], "text": d}
             for d, m in zip(res["documents"], res["metadatas"])]
    return sorted(items, key=lambda x: x["chunk"])


def store(chunks, source, file_hash=""):
    col = get_collection()
    col.upsert(
        ids=[f"{source}-{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"source": source, "chunk": i, "hash": file_hash}
                   for i in range(len(chunks))],
    )
    return col.count()


def search(question, k=6):
    col = get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[question], n_results=min(k, col.count()))
    hits = []
    for text, meta, dist in zip(res["documents"][0],
                                res["metadatas"][0],
                                res["distances"][0]):
        hits.append({"text": text, "source": meta["source"],
                     "chunk": meta["chunk"], "distance": dist})
    return hits