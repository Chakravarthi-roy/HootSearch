from pypdf import PdfReader
import argparse

def extract_pdf():
    reader = PdfReader()
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages)

def main():
    parser = argparse.ArguementParser(description="Document Q&A")
    parser.add_argument("file", help="path to the PDF")
    args = parser.parse_args()

    text = extract_text(args.file)
    print(text)

if __name__ == "__main__":
    main()
