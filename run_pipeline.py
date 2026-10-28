#!/usr/bin/env python3
"""
Taiwan Protected Trees & Precious Old Trees GIS Pipeline Master Runner
Executes the end-to-end workflow:
1. Data Collection (Fetch official datasets)
2. Extraction (Official PDF to Markdown & structured JSON)
3. Merge & Harmonize (TWD97->WGS84, deduplicate, Master JSON & GeoJSON)
4. WebGIS Builder (Zero-CORS bundle & index.html WebGIS platform)
"""

import os
import sys
import time
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

STEPS = [
    ("Step 1: Data Collection", os.path.join(SCRIPTS_DIR, "01_fetch_datasets.py")),
    ("Step 2: PDF to Markdown Extraction", os.path.join(SCRIPTS_DIR, "02_extract_pdf_to_md.py")),
    ("Step 3: Harmonize & Merge to Master JSON/GeoJSON", os.path.join(SCRIPTS_DIR, "03_merge_to_json.py")),
    ("Step 4: Build WebGIS & Zero-CORS Data Bundle", os.path.join(SCRIPTS_DIR, "04_build_gis_map.py")),
]

def main():
    t_start = time.time()
    print("=" * 80)
    print(" 🌲 臺灣受保護樹木與珍貴老樹 WebGIS 全自動資料管線 (END-TO-END PIPELINE)")
    print("=" * 80)

    for i, (title, script_path) in enumerate(STEPS, 1):
        print(f"\n[{i}/{len(STEPS)}] Running {title}...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path])
        if res.returncode != 0:
            print(f"[!] Pipeline failed at {title} (exit code {res.returncode})", file=sys.stderr)
            sys.exit(res.returncode)
        elapsed = time.time() - t0
        print(f"[{i}/{len(STEPS)}] Completed {title} in {elapsed:.2f}s")

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"🎉 全部管線執行完畢！總耗時: {total_time:.2f} 秒")
    print(f"📍 成果 GIS 地圖平臺：index.html (直接以瀏覽器開啟即可操作)")
    print(f"📂 成果 GeoJSON：data/processed/taiwan_protected_trees.geojson (可直接載入 QGIS)")
    print(f"📑 成果 PDF 提取：data/extracted_md/hualien_protected_trees.md (完整樹籍 Markdown 表格)")
    print("=" * 80)

if __name__ == "__main__":
    main()
