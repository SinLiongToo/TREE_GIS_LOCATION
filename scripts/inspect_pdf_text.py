import fitz # PyMuPDF
import sys

def inspect_pdf(filepath):
    print(f"=== Inspecting {filepath} ===")
    doc = fitz.open(filepath)
    print("Page count:", len(doc))
    for i in range(min(3, len(doc))):
        page = doc[i]
        text = page.get_text()
        print(f"--- Page {i+1} (Chars: {len(text)}) ---")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for l in lines[:15]:
            print("  ", l)

if __name__ == '__main__':
    inspect_pdf('data/raw/hualien_protected_trees.pdf')
    inspect_pdf('data/raw/yilan_protected_trees.pdf')
