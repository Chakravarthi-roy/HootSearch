import argparse

from ingest import extract
from llm import answer
from pipeline import sync, watch, start_watcher, delete_document
from store import search, list_sources, get_chunks, reset_collection

def app():
    added, removed = sync()
    print(f"Synced docs: {added} added, {removed} removed")
    start_watcher()
    chat()

def chat():
    print("Ask! Type 'exit' to quit:)")
    while True:
        try:
            q = input("\nQuestion:").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue

        hits = search(q)
        a = answer(q, hits)  # was answer(question, hits): `question` didn't exist
        print("\n" + a)
        print("\nRetrieved from chunks:")
        for i, h in enumerate(hits, 1):
            print(f"  [{i}] {h['source']} chunk {h['chunk']} (distance {h['distance']:.2f})")

def main():
    parser = argparse.ArgumentParser(description="Document Q&A")
    parser.add_argument("--ask", help="ask a question and get an answer")
    parser.add_argument("--list", action="store_true", help="list stored documents")
    parser.add_argument("--search", help="show top matching chunks")
    parser.add_argument("--show", help="show the stored chunks of one document")
    parser.add_argument("--sync", action="store_true", help="ingest new PDFs / remove deleted ones")
    parser.add_argument("--text", metavar="FILE", help="print the raw text extracted from a PDF")
    parser.add_argument("--watch", action="store_true", help="keep watching docs/ to sync automatically")
    parser.add_argument("--reset", action="store_true", help="wipe the database (PDFs are kept)")
    parser.add_argument("--delete", metavar="NAME", help="delete a document and its chunks")
    args = parser.parse_args()

    # These options don't need a file, so they come before the file checks.
    if args.sync:
        added, removed = sync()
        print(f"sync done, {added} added & {removed} removed")
        return

    if args.watch:
        watch()
        return

    if args.search:
        hits = search(args.search, k=3)
        if not hits:
            print("Nothing stored yet. Run --sync")
        for rank, h in enumerate(hits, 1):
            print(f"#{rank}  distance={h['distance']:.3f}  "
                  f"{h['source']} (chunk {h['chunk']})")
            print(h["text"], end="\n\n")
        return

    if args.list:
        sources = list_sources()
        if not sources:
            print("Nothing stored yet. Run --sync")
        for s in sources:
            print(f"  {s}  ({len(get_chunks(s))} chunks)")
        return

    if args.show:
        chunks = get_chunks(args.show)
        if not chunks:
            print(f"No stored document named {args.show}. Try --list")
            return
        print(f"{args.show}: {len(chunks)} chunks")
        for c in chunks:
            print(f"--- chunk {c['chunk']} ({len(c['text'])} chars) ---")
            print(c["text"], end="\n\n")
        return

    if args.ask:
        hits = search(args.ask)
        print(answer(args.ask, hits))
        print("\nRetrieved From(citations):")
        for i, h in enumerate(hits, 1):
            print(f"  [{i}] {h['source']} chunk {h['chunk']} (distance {h['distance']:.2f})")
        return

    if args.text:
        print(extract(args.text))
        return

    if args.reset:
        if input("Wipe the whole database? PDFs in docs/ are kept. [y/N] ").strip().lower() == "y":
            reset_collection()
            print("Database cleared. Run --sync to rebuild.")
        return

    if args.delete:
        msg = f"Delete {args.delete} from docs/ and the database? This cannot be undone. [y/N] "
        if input(msg).strip().lower() != "y":
            return
        if delete_document(args.delete):
            print(f"Deleted {args.delete}")
        else:
            print(f"No document named {args.delete}. Try --list")
        return

    app()

if __name__ == "__main__":
    main()