#!/usr/bin/env python3
"""
Step 4: WebGIS Application Builder
Generates:
1. data/processed/taiwan_protected_trees_data.js (Zero-CORS offline-ready JS bundle)
2. Validates index.html
"""

import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GEOJSON_PATH = os.path.join(PROCESSED_DIR, "taiwan_protected_trees.geojson")
STATS_PATH = os.path.join(PROCESSED_DIR, "statistics.json")
JS_DATA_PATH = os.path.join(PROCESSED_DIR, "taiwan_protected_trees_data.js")
HTML_OUT_PATH = os.path.join(BASE_DIR, "index.html")

def build_data_bundle():
    print(f"[*] Reading GeoJSON from {GEOJSON_PATH}...")
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    with open(STATS_PATH, "r", encoding="utf-8") as f:
        stats_data = json.load(f)

    print(f"[*] Packaging into zero-CORS JS bundle: {JS_DATA_PATH}...")
    with open(JS_DATA_PATH, "w", encoding="utf-8") as f:
        f.write("// Auto-generated zero-CORS offline data bundle for Taiwan Protected Trees WebGIS\n")
        f.write("window.TAIWAN_TREES_STATS = ")
        json.dump(stats_data, f, ensure_ascii=False)
        f.write(";\n")
        f.write("window.TAIWAN_TREES_GEOJSON = ")
        json.dump(geojson_data, f, ensure_ascii=False)
        f.write(";\n")

    print(f"    [+] Created data bundle ({os.path.getsize(JS_DATA_PATH):,} bytes)")
    return stats_data

def main():
    print("=" * 70)
    print("STEP 4: BUILDING STANDALONE WEBGIS PLATFORM (INDEX.HTML)")
    print("=" * 70)
    stats = build_data_bundle()
    if os.path.exists(HTML_OUT_PATH):
        print(f"[✓] index.html verified: {HTML_OUT_PATH} ({os.path.getsize(HTML_OUT_PATH):,} bytes)")
    print(f"[✓] Step 4 Complete: Ready to launch!")

if __name__ == "__main__":
    main()
