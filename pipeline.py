import os
from ingest import extract, chunk_text
from store import store, source_exists, delete_source, list_sources
import threading

def ingest(path):
    name = os.path.basename(path)

    if source_exists(name):
        print("File already, rename if its new")
        return False

    text = extract(path)
    if not text.strip():
        print(f" File {name} has no data")
        return False
    chunks = chunk_text(text)

    if source_exists(name):
        return False

    store(chunks, name)
    print(f"File {name}: {len(chunks)} chunks stored")
    return True

def sync(folder="docs"):
    added = 0
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(folder, filename)
        if ingest_file(path):
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
        print("\nStopped watching.")

def start_watcher(folder="docs", interval=3):
    t = threading.Thread(target=watch, args=(folder, interval), daemon=True)
    t.start()
    return t




