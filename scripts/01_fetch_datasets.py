#!/usr/bin/env python3
"""
Step 1: Data Collection Script
Fetches official protected and precious old tree datasets across Taiwan.
"""

import os
import sys
import json
import ssl
import time
import subprocess
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_RAW, exist_ok=True)

ctx = ssl._create_unverified_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

DATA_SOURCES = [
    {
        "id": "national_oldtree_life",
        "title": "全國城鄉老樹資源調查資料庫 (老樹報報)",
        "agency": "農業部林業試驗所 / 國立中興大學",
        "format": "JSON",
        "url": "https://map.oldtree.life/api/Tree/trees",
        "dest_file": "oldtree_national.json",
        "license": "政府資料開放授權條款 / 農業部林試所科技計畫公開資料",
        "description": "涵蓋全台灣 22 縣市之列管受保護樹木、珍貴老樹與民間踏查老樹，包含 GPS 座標、樹齡、樹高、胸圍、樹籍沿革與原始管理機關。",
    },
    {
        "id": "taipei_cultural_bureau",
        "title": "臺北市受保護樹木",
        "agency": "臺北市政府文化局",
        "format": "CSV",
        "url": "https://data.taipei/api/dataset/d9d1140b-c2c3-405f-8dd1-7b87b00f6f53/resource/a7c2db0d-8b6e-42b2-bdcc-ae69a6797e1d/download",
        "dest_file": "taipei_protected_trees.csv",
        "license": "政府資料開放授權條款第1版",
        "description": "依據《臺北市樹木保護自治條例》列管之受保護樹木清單，包含編號、樹種、學名、胸徑、胸圍、地址與 GPS 經緯度座標。",
    },
    {
        "id": "taoyuan_agri_bureau",
        "title": "桃園市受保護樹木資料",
        "agency": "桃園市政府農業局",
        "format": "CSV",
        "url": "https://opendata.tycg.gov.tw/api/dataset/25bbcd34-16a8-4c4e-a341-4666cd0db5b4/resource/64ead2ac-24d0-48b5-8c4d-8ea4deec0baf/download",
        "dest_file": "taoyuan_protected_trees.csv",
        "license": "政府資料開放授權條款第1版",
        "description": "依據《森林法》樹木保護專章列管受保護樹木，包含樹木編號、樹種、區域、地址、GPS 座標、樹高與胸高直徑。",
    },
    {
        "id": "chiayi_county_gov",
        "title": "嘉義縣受保護樹木",
        "agency": "嘉義縣政府農業處",
        "format": "CSV",
        "url": "https://ws-tm.cyhg.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvMTM0OS9yZWxmaWxlLzEyNTY1LzIwNTQ0OC83NjExMjViNy02MzQzLTQ4YmUtYTQzZS0wZTk2N2ZkYzNjMDkuY3N2&n=6ICB5qi56LOH5paZLTEuY3N2",
        "dest_file": "chiayi_protected_trees.csv",
        "license": "政府資料開放授權條款第1版",
        "description": "嘉義縣轄內公告受保護樹木清單，含轄內編號、樹種中名、TWD97 座標、樹高、胸圍、鄉鎮與地址。",
    },
    {
        "id": "hualien_county_pdf",
        "title": "花蓮縣轄區受保護樹木列冊清冊",
        "agency": "花蓮縣政府農業處",
        "format": "PDF",
        "url": "https://ws.hl.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDIyL3JlbGZpbGUvOTg1NS83MDQxMy9lMTVlZGM2ZS1kNDExLTRhZTktYmViNC1lNjg3OTUyNzJlZmUucGRm&n=6Iqx6JOu57ij6L2E5Y2A5Y%2BX5L%2Bd6K235qi55pyo5YiX5YaK5riF5ZauLnBkZg%3D%3D",
        "dest_file": "hualien_protected_trees.pdf",
        "license": "花蓮縣政府公報公開文件",
        "description": "花蓮縣政府依森林法第38條之2公告之轄區受保護樹木造冊清冊，共20頁表格，含編號、樹種、樹齡、胸圍、胸徑、地號與土地所有權人。",
    }
]

def download_source(src):
    dest_path = os.path.join(DATA_RAW, src["dest_file"])
    print(f"[*] Fetching: {src['title']} ({src['format']})...")
    print(f"    URL: {src['url']}")

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        file_size = os.path.getsize(dest_path)
        print(f"    [+] Existing valid file found ({file_size:,} bytes), ready.")
        return {**src, "status": "ok_existing", "bytes": file_size, "path": dest_path, "updated_at": datetime.now().isoformat()}

    # Try urllib first
    try:
        req = urllib.request.Request(src["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, context=ctx, timeout=40) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            file_size = len(data)
            print(f"    [+] Downloaded successfully: {file_size:,} bytes -> {src['dest_file']}")
            return {**src, "status": "ok_downloaded", "bytes": file_size, "path": dest_path, "updated_at": datetime.now().isoformat()}
    except Exception as e:
        print(f"    [!] urllib failed ({e}), falling back to curl.exe...")
        try:
            cmd = ["curl.exe", "-k", "-sL", "-m", "40", "-A", UA, src["url"], "-o", dest_path]
            subprocess.run(cmd, check=True)
            file_size = os.path.getsize(dest_path)
            print(f"    [+] curl.exe downloaded successfully: {file_size:,} bytes -> {src['dest_file']}")
            return {**src, "status": "ok_curl", "bytes": file_size, "path": dest_path, "updated_at": datetime.now().isoformat()}
        except Exception as e2:
            print(f"    [-] Failed downloading {src['title']}: {e2}", file=sys.stderr)
            return {**src, "status": "failed", "error": str(e2), "path": dest_path}

def main():
    print("=" * 70)
    print("STEP 1: BATCH DOWNLOADING OFFICIAL PROTECTED TREE DATASETS")
    print("=" * 70)
    manifest = []
    for src in DATA_SOURCES:
        res = download_source(src)
        manifest.append(res)
        print("-" * 50)

    manifest_path = os.path.join(DATA_RAW, "sources_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "sources": manifest
        }, f, ensure_ascii=False, indent=2)

    print(f"[OK] Step 1 Complete. Manifest saved to {manifest_path}")

if __name__ == "__main__":
    main()
