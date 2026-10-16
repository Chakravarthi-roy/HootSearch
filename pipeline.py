import os
from ingest import extract, chunk_text
from store import store, source_exists, delete_source, list_sources
import threading
import time

def ingest(path):
    name = os.path.basename(path)

    if source_exists(name):
        # print("File already present, rename if its new")
        return False

    text = extract(path)
    if not text.strip():
        print(f" File {name} has no data")
        return False
    chunks = chunk_text(text)

    store(chunks, name)
    print(f"File {name}: {len(chunks)} chunks stored")
    return True

def sync(folder="docs"):
    on_disk = set()
    added = 0
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".pdf"):
            continue
        on_disk.add(filename)
        path = os.path.join(folder, filename)
        if ingest(path):
            added += 1

    removed = 0
    for name in list_sources():
        if name not in on_disk:
            delete_source(name)
            print(f"  - {name}: file deleted, chunks removed!")
            removed += 1

    return added, removed

def watch(folder="docs", interval=3):
    print(f"Watching {folder}/ every {interval}s. Press Ctrl+C to stop.")
    try:
        while True:
            sync(folder)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch stopped.")

def start_watcher(folder="docs", interval=3):
    t = threading.Thread(target=watch, args=(folder, interval), daemon=True)
    t.start()
    return t




