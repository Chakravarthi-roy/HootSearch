This is HootSearch
Upload your docs, Ask a question, The app fecthes the answer from the docs.

doc -> text -> chunks -> embeddings -> vector database(chromeDb)

question -> embeddings -> search the database -> retrieve the top chunks ->
         -> LLM -> display answer

This is the basic idea. 
PyPdf - Python library used to read/extract data from pdfs

Put your PDFs in the `docs/` folder.

## Commands (try them in this order)

Each one builds on the one before it, so if something breaks you know which stage to look at by following this flow of test

**1. Raw extracted text** (to see if the extraction is clean)
```bash
python main.py docs/doc.pdf
```

**2. Print the chunks** (are they sensible? or not?)
```bash
python main.py docs/doc.pdf --chunks
```

**3. Ingest files in docs/** (chunk, embed, store, all runs & removes anything deleted from docs)
```bash
python main.py --sync
```
Run it twice. The second run should report `0 added, 0 removed`. Because it is a duplicate.

**4. Search** (is retrieval to check if it is finding the right chunks or not)
```bash
python main.py --search "<question>"
```

**5. Full answer** (search + LLM, with sources as citations)
```bash
python main.py --ask "<question>"
```

**6. Auto-sync while you work** (use a second terminal tab)
```bash
python main.py --watch
```
Drop a PDF into `docs/` and it gets ingested within a few seconds. Delete one and its chunks are removed. Stop with Ctrl+C in Windows or Control+C in Mac.

## Debugging rule

If an answer is wrong, run the same question with `--search`. If the right chunk isn't in the results, retrieval is the problem (chunking, embedding, k). If it is there, the prompt or the model is the problem. Fine tune the values based on your docs to find the optimal k. It is just an experiment game sometimes. 


