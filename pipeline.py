import hashlib
import os
import threading
import time

from ingest import extract, chunk_text
from store import (store, source_exists, get_source_hash,
                   delete_source, list_sources)

_sync_lock = threading.Lock()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ingest(path):
    name = os.path.basename(path)
    new_hash = file_hash(path)
    old_hash = get_source_hash(name)

    if old_hash == new_hash:
        return False

    if source_exists(name):
        delete_source(name)
        print(f"  ~ {name}: changed, re-ingesting")

    text = extract(path)
    if not text.strip():
        print(f"  File {name} has no extractable text")
        return False

    chunks = chunk_text(text)
    store(chunks, name, new_hash)
    print(f"File {name}: {len(chunks)} chunks stored")
    return True


def sync(folder="docs"):
    with _sync_lock:
        os.makedirs(folder, exist_ok=True)

        on_disk = set()
        added = 0
        for filename in sorted(os.listdir(folder)):
            if not filename.lower().endswith(".pdf"):
                continue
            on_disk.add(filename)
            path = os.path.join(folder, filename)

            if time.time() - os.path.getmtime(path) < 2:
                continue

            try:
                if ingest(path):
                    added += 1
            except Exception as e:
                print(f"  ! {filename}: failed to ingest ({e})")

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
            try:
                sync(folder)
            except Exception as e:
                print(f"watch error: {e}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch stopped.")


def start_watcher(folder="docs", interval=3):
    t = threading.Thread(target=watch, args=(folder, interval), daemon=True)
    t.start()
    return t