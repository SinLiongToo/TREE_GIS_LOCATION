import fitz
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open('data/raw/hualien_protected_trees.pdf')
print("Total pages:", len(doc))

# Let's inspect page 0 text blocks
p0 = doc[0]
blocks = p0.get_text("blocks")
print(f"Page 1 blocks count: {len(blocks)}")
for b in blocks[:15]:
    # (x0, y0, x1, y1, text, block_no, block_type)
    print(f"Block: bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {repr(b[4].strip())}")

# Test PyMuPDF built-in table finder
try:
    tabs = p0.find_tables()
    print("PyMuPDF find_tables count:", len(tabs.tables))
    if len(tabs.tables) > 0:
        df = tabs.tables[0].extract()
        for row in df[:6]:
            print("Row:", row)
except Exception as e:
    print("Table find error:", e)
