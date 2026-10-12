from pypdf import PdfReader
import argparse
from ingest import extract, chunk_text
from store import store, search
from llm import answer

def main():
    parser = argparse.ArgumentParser(description="Document Q&A")
    parser.add_argument("file", nargs="?", help="path to the PDF")
    parser.add_argument("--chunks", action="store_true", help="show chunks of the text")
    parser.add_argument("--store", action="store_true", help="embed chunks and save them")
    parser.add_argument("--ask", help="ask a question and get an answer")
    parser.add_argument("--search", help="show top matching chunks")
    args = parser.parse_args()

    if args.search:
    hits = search(args.search, k=3)
    if not hits:
        print("Nothing stored yet. Run --store on a PDF first.")
    for rank, h in enumerate(hits, 1):
        print(f"#{rank}  distance={h['distance']:.3f}  "
              f"{h['source']} (chunk {h['chunk']})")
        print(h["text"])
        print()
    return

    if args.ask:
        hits = search(args.ask)
        print(answer(args.ask, hits))
        """
        if not hits:
            print("Storage Empty, Run --store")
        for rank, h in enumerate(hits, 1):
            print(f"#{rank}  distance={h['distance']:.3f}  "
                  f"{h['source']} (chunk {h['chunk']})")
            print(h["text"][:300].replace("\n", " "), end="\n\n")
        """
        print("\nRetrieved From(citations):")
        for i, h in enumerate(hits, 1):
            print(f"  [{i}] {h['source']} chunk {h['chunk']} (distance {h['distance']:.2f})")
        return

    if not args.file:
        parser.error("include a file in the command")

    text = extract_pdf(args.file)
    # print(text)
    
    if args.store:
        chunks = chunk_text(text)
        total = store_chunks(chunks, os.path.basename(args.file))
        print(f"stored {len(chunks)} chunks, collection holds {total}")
    elif args.chunks:
        chunks = chunk_text(text)
        print(f"{len(text)} doc length -> {len(chunks)} size chunks")
        for i, c in enumerate(chunks[:3]):
            print(f"{i} \n{c}", end="\n\n")
    else:
        print(text)
	

if __name__ == "__main__":
    main()
