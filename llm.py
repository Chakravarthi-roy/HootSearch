import anthropic

MODEL = "claude-haiku-5-5"
SYSTEM = """You answer questions using ONLY the numbered sources provided.

Rules:
- If the sources contain the answer, answer concisely and cite the source numbers, like [1] or [2].
- If the sources do not contain the answer, reply exactly: "I don't know based on the provided documents."
- Never use outside knowledge, even if you know the answer.
- The sources are raw text extracted from PDFs and may have glitches (glued words, odd spacing). Read past them."""

def build_context(hits):
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(f"[{i}].(From {h['source']}, chunk {h['chunk']})\n{h['text']}")
    return "\n\n".join(parts)

def answer(question, hits):
    if not hits:
        return "Nothing stored yet. Add a document first."
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"<sources>\n{build_context(hits)}\n</sources>\n\nQuestion: {question}",
        }],
    )
    return msg.content[0].text
