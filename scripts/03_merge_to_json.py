#!/usr/bin/env python3
"""
Step 3: Data Merge & Harmonization Pipeline
Merges National Old Tree database + Taipei + Taoyuan + Chiayi + Hualien PDF extracts.
Preserves complete Ground Truth lineage, converts coordinates, normalizes county/species,
and generates:
1. data/processed/taiwan_protected_trees_master.json (Full JSON with all attributes)
2. data/processed/taiwan_protected_trees.geojson (Standard GIS GeoJSON FeatureCollection)
3. data/processed/statistics.json (Analytics summary for dashboard & reports)
"""

import os
import sys
import csv
import math
import json
import re
from datetime import datetime
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
EXTRACTED_DIR = os.path.join(BASE_DIR, "data", "extracted_md")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

MASTER_JSON_PATH = os.path.join(PROCESSED_DIR, "taiwan_protected_trees_master.json")
GEOJSON_PATH = os.path.join(PROCESSED_DIR, "taiwan_protected_trees.geojson")
STATS_PATH = os.path.join(PROCESSED_DIR, "statistics.json")

# Standardize County Names (統一「台」與「臺」，以及行政區別名)
COUNTY_MAP = {
    "台北市": "臺北市", "臺北市": "臺北市",
    "新北市": "新北市",
    "基隆市": "基隆市",
    "桃園市": "桃園市", "桃園縣": "桃園市",
    "新竹市": "新竹市",
    "新竹縣": "新竹縣",
    "苗栗縣": "苗栗縣",
    "台中市": "臺中市", "臺中市": "臺中市",
    "彰化縣": "彰化縣",
    "南投縣": "南投縣",
    "雲林縣": "雲林縣",
    "嘉義市": "嘉義市",
    "嘉義縣": "嘉義縣",
    "台南市": "臺南市", "臺南市": "臺南市",
    "高雄市": "高雄市",
    "屏東縣": "屏東縣",
    "宜蘭縣": "宜蘭縣",
    "花蓮縣": "花蓮縣",
    "台東縣": "臺東縣", "臺東縣": "臺東縣",
    "澎湖縣": "澎湖縣",
    "金門縣": "金門縣",
    "連江縣": "連江縣",
}

def normalize_county(name):
    if not name:
        return "未知縣市"
    name = str(name).strip()
    for k, v in COUNTY_MAP.items():
        if k in name:
            return v
    return name

def normalize_species(name):
    if not name:
        return "未詳或多種"
    name = str(name).strip()
    name = re.sub(r'[\?？]+', '', name)
    # Common synonyms
    synonyms = {
        "正榕": "榕樹", "雀榕": "雀榕", "白榕": "白榕",
        "楓香樹": "楓香",
        "樟樹": "樟樹", "香樟": "樟樹",
        "茄苳樹": "茄苳", "重陽木": "茄苳",
        "芒果樹": "芒果",
        "龍眼樹": "龍眼",
        "麵包樹": "麵包樹",
        "黑板樹": "黑板樹",
        "苦楝樹": "苦楝",
        "刺桐樹": "刺桐",
        "木棉樹": "木棉",
        "樟": "樟樹",
        "榕": "榕樹",
        "茄苳": "茄苳",
    }
    return synonyms.get(name, name)

def twd97_to_wgs84(x, y):
    try:
        x, y = float(x), float(y)
    except (ValueError, TypeError):
        return None, None
    if x <= 0 or y <= 0:
        return None, None
    a = 6378137.0
    b = 6356752.314245
    long0 = 121.0 * math.pi / 180.0
    k0 = 0.9999
    dx = 250000.0
    e = math.sqrt(1 - (b / a)**2)
    e2 = e**2 / (1 - e**2)

    x -= dx
    M = y / k0
    mu = M / (a * (1.0 - (e**2)/4.0 - 3.0*(e**4)/64.0 - 5.0*(e**6)/256.0))
    e1 = (1.0 - math.sqrt(1.0 - e**2)) / (1.0 + math.sqrt(1.0 - e**2))

    J1 = (3.0*e1/2.0 - 27.0*(e1**3)/32.0)
    J2 = (21.0*(e1**2)/16.0 - 55.0*(e1**4)/32.0)
    J3 = (151.0*(e1**3)/96.0)
    J4 = (1097.0*(e1**4)/512.0)

    fp = mu + J1*math.sin(2.0*mu) + J2*math.sin(4.0*mu) + J3*math.sin(6.0*mu) + J4*math.sin(8.0*mu)

    C1 = e2 * (math.cos(fp)**2)
    T1 = math.tan(fp)**2
    R1 = a * (1.0 - e**2) / ((1.0 - (e**2)*(math.sin(fp)**2))**1.5)
    N1 = a / math.sqrt(1.0 - (e**2)*(math.sin(fp)**2))
    D = x / (N1 * k0)

    Q1 = N1 * math.tan(fp) / R1
    Q2 = (D**2)/2.0
    Q3 = (5.0 + 3.0*T1 + 10.0*C1 - 4.0*(C1**2) - 9.0*e2) * (D**4)/24.0
    Q4 = (61.0 + 90.0*T1 + 298.0*C1 + 45.0*(T1**2) - 3.0*(C1**2) - 252.0*e2) * (D**6)/720.0
    lat = fp - Q1 * (Q2 - Q3 + Q4)

    Q5 = D
    Q6 = (1.0 + 2.0*T1 + C1) * (D**3)/6.0
    Q7 = (5.0 - 2.0*C1 + 28.0*T1 - 3.0*(C1**2) + 8.0*e2 + 24.0*(T1**2)) * (D**5)/120.0
    lon = long0 + (Q5 - Q6 + Q7) / math.cos(fp)

    return round(lon * 180.0 / math.pi, 6), round(lat * 180.0 / math.pi, 6)

def is_valid_tw_coord(lon, lat):
    if lon is None or lat is None:
        return False
    # Taiwan & Outlying Islands (Penghu, Kinmen, Matsu) bounding box
    return (118.0 <= lon <= 122.5) and (21.5 <= lat <= 26.5)

def distance_meters(lon1, lat1, lon2, lat2):
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def load_national_oldtree():
    path = os.path.join(RAW_DIR, "oldtree_national.json")
    print(f"[*] Processing National Old Tree DB: {path}")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trees = []
    for item in data:
        coords = item.get("coordinate", {}).get("coordinates", [None, None])
        lon = float(coords[0]) if coords and len(coords) > 0 and coords[0] is not None else None
        lat = float(coords[1]) if coords and len(coords) > 1 and coords[1] is not None else None

        # Age parsing
        age_val = None
        raw_age = str(item.get("tree_age", "")).strip()
        if raw_age and raw_age.isdigit():
            age_val = int(raw_age)

        # Height & Bust parsing
        try:
            h = float(item.get("tree_heigh")) if item.get("tree_heigh") and float(item.get("tree_heigh")) > 0 else None
        except (ValueError, TypeError):
            h = None

        try:
            b = float(item.get("tree_bust")) if item.get("tree_bust") and float(item.get("tree_bust")) > 0 else None
        except (ValueError, TypeError):
            b = None

        county = normalize_county(item.get("county"))
        town = item.get("town", "").strip()
        village = item.get("village", "").strip()
        sp = normalize_species(item.get("treeName"))
        tree_id = item.get("treeId", "")

        t = {
            "id": f"NAT-{tree_id or item.get('id')}",
            "tree_id": str(tree_id),
            "source_dataset": "national_oldtree_life",
            "source_agency": item.get("source") or item.get("owner") or "農業部林業試驗所",
            "source_ground_truth": {
                "title": "全國城鄉老樹資源調查資料庫 (老樹報報)",
                "url": item.get("oldtreeUrl") or f"https://oldtree.life/oldtree/{tree_id}",
                "agency": "農業部林業試驗所 / 國立中興大學",
                "license": "政府資料開放授權條款"
            },
            "county": county,
            "township": town,
            "village": village,
            "address": item.get("location") or f"{county}{town}{village}",
            "species_zh": sp,
            "scientific_name": item.get("tree_taxon_name") or None,
            "species_en": None,
            "estimated_age": age_val,
            "tree_height_m": h,
            "dbh_m": round(b / math.pi, 2) if b else None,
            "bust_circumference_m": b,
            "crown_area_m2": float(item.get("tree_crown")) if item.get("tree_crown") and float(item.get("tree_crown")) > 0 else None,
            "health_status": item.get("health_sta") or None,
            "owner_or_manager": item.get("owner") or None,
            "protection_basis": "《森林法》樹木保護專章 / 珍貴老樹普查",
            "story": item.get("tree_story") or None,
            "remarks": item.get("remarks") or None,
            "photo_url": item.get("oldtree_photo_url") or None,
            "longitude": lon,
            "latitude": lat,
            "has_valid_coords": is_valid_tw_coord(lon, lat)
        }
        trees.append(t)
    print(f"    [+] Loaded {len(trees)} national trees (Valid coords: {sum(1 for t in trees if t['has_valid_coords'])})")
    return trees

def load_taipei_trees():
    path = os.path.join(RAW_DIR, "taipei_protected_trees.csv")
    print(f"[*] Processing Taipei Protected Trees: {path}")
    if not os.path.exists(path):
        return []
    trees = []
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tree_id = row.get("編號", "").strip()
            sp = normalize_species(row.get("樹種名稱", ""))
            sc_name = row.get("樹種學名", "").strip()
            en_name = row.get("英文名", "").strip()
            addr = row.get("地址", "").strip()
            district = row.get("地理位置名稱", "").strip()
            mgr = row.get("管理單位", "").strip()

            try:
                lat = float(row.get("緯度", ""))
                lon = float(row.get("經度", ""))
            except (ValueError, TypeError):
                lat, lon = None, None

            try:
                dbh = float(row.get("胸徑寬度公尺", ""))
            except (ValueError, TypeError):
                dbh = None

            try:
                bust = float(row.get("胸圍長度公尺", ""))
            except (ValueError, TypeError):
                bust = None

            t = {
                "id": f"TPE-{tree_id}",
                "tree_id": str(tree_id),
                "source_dataset": "taipei_cultural_bureau",
                "source_agency": mgr or "臺北市政府文化局",
                "source_ground_truth": {
                    "title": "臺北市受保護樹木",
                    "url": "https://data.taipei/dataset/detail?id=d9d1140b-c2c3-405f-8dd1-7b87b00f6f53",
                    "agency": "臺北市政府文化局",
                    "license": "政府資料開放授權條款第1版"
                },
                "county": "臺北市",
                "township": district if district.endswith("區") else f"{district}區" if district else "臺北市",
                "village": "",
                "address": addr,
                "species_zh": sp,
                "scientific_name": sc_name or None,
                "species_en": en_name or None,
                "estimated_age": None,
                "tree_height_m": None,
                "dbh_m": dbh,
                "bust_circumference_m": bust,
                "crown_area_m2": None,
                "health_status": "受保護列管中",
                "owner_or_manager": mgr or "臺北市政府",
                "protection_basis": "《臺北市樹木保護自治條例》",
                "story": None,
                "remarks": None,
                "photo_url": None,
                "longitude": lon,
                "latitude": lat,
                "has_valid_coords": is_valid_tw_coord(lon, lat)
            }
            trees.append(t)
    print(f"    [+] Loaded {len(trees)} Taipei trees (Valid coords: {sum(1 for t in trees if t['has_valid_coords'])})")
    return trees

def load_taoyuan_trees():
    path = os.path.join(RAW_DIR, "taoyuan_protected_trees.csv")
    print(f"[*] Processing Taoyuan Protected Trees: {path}")
    if not os.path.exists(path):
        return []
    trees = []
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tree_id = row.get("樹木編號", "").strip()
            sp = normalize_species(row.get("樹種", ""))
            district = row.get("區域", "").strip()
            addr = row.get("地址", "").strip()

            try:
                lat = float(row.get("GPS緯度", ""))
                lon = float(row.get("GPS經度", ""))
            except (ValueError, TypeError):
                lat, lon = None, None

            try:
                h = float(row.get("樹高_公尺", ""))
            except (ValueError, TypeError):
                h = None

            try:
                dbh = float(row.get("胸高直徑_公尺", ""))
            except (ValueError, TypeError):
                dbh = None

            try:
                bust = float(row.get("胸高圍_公尺", ""))
            except (ValueError, TypeError):
                bust = None

            t = {
                "id": f"TYC-{tree_id}",
                "tree_id": str(tree_id),
                "source_dataset": "taoyuan_agri_bureau",
                "source_agency": "桃園市政府農業局",
                "source_ground_truth": {
                    "title": "桃園市受保護樹木資料",
                    "url": "https://opendata.tycg.gov.tw/dataset/detail?id=25bbcd34-16a8-4c4e-a341-4666cd0db5b4",
                    "agency": "桃園市政府農業局",
                    "license": "政府資料開放授權條款第1版"
                },
                "county": "桃園市",
                "township": district if district.endswith("區") else f"{district}區" if district else "桃園市",
                "village": "",
                "address": addr,
                "species_zh": sp,
                "scientific_name": None,
                "species_en": None,
                "estimated_age": None,
                "tree_height_m": h,
                "dbh_m": dbh,
                "bust_circumference_m": bust or (round(dbh * math.pi, 2) if dbh else None),
                "crown_area_m2": None,
                "health_status": "受保護列管中",
                "owner_or_manager": "桃園市政府農業局",
                "protection_basis": "《森林法》樹木保護專章",
                "story": None,
                "remarks": None,
                "photo_url": None,
                "longitude": lon,
                "latitude": lat,
                "has_valid_coords": is_valid_tw_coord(lon, lat)
            }
            trees.append(t)
    print(f"    [+] Loaded {len(trees)} Taoyuan trees (Valid coords: {sum(1 for t in trees if t['has_valid_coords'])})")
    return trees

def load_chiayi_trees():
    path = os.path.join(RAW_DIR, "chiayi_protected_trees.csv")
    print(f"[*] Processing Chiayi County Trees: {path}")
    if not os.path.exists(path):
        return []
    trees = []
    with open(path, "r", encoding="big5", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tree_id = row.get("轄內編號", "").strip()
            sp = normalize_species(row.get("樹種中名", ""))
            x_str = row.get("座標X", "").strip()
            y_str = row.get("座標Y", "").strip()
            town = row.get("鄉鎮", "").strip()
            village = row.get("村里", "").strip()
            mgr = row.get("管理人", "").strip()
            addr = row.get("地址", "").strip()
            age_raw = row.get("樹齡", "").strip()

            age_num = None
            mage = re.search(r'(\d+)', age_raw)
            if mage:
                age_num = int(mage.group(1))

            try:
                h = float(row.get("樹高", ""))
            except (ValueError, TypeError):
                h = None

            try:
                bust = float(row.get("胸圍", ""))
            except (ValueError, TypeError):
                bust = None

            lon, lat = twd97_to_wgs84(x_str, y_str)

            t = {
                "id": f"CYQ-{tree_id}",
                "tree_id": str(tree_id),
                "source_dataset": "chiayi_county_gov",
                "source_agency": "嘉義縣政府農業處",
                "source_ground_truth": {
                    "title": "嘉義縣受保護樹木",
                    "url": "https://data.gov.tw/dataset/133889",
                    "agency": "嘉義縣政府農業處",
                    "license": "政府資料開放授權條款第1版"
                },
                "county": "嘉義縣",
                "township": town,
                "village": village,
                "address": addr or f"{town}{village}",
                "species_zh": sp,
                "scientific_name": None,
                "species_en": None,
                "estimated_age": age_num,
                "tree_height_m": h,
                "dbh_m": round(bust / math.pi, 2) if bust else None,
                "bust_circumference_m": bust,
                "crown_area_m2": None,
                "health_status": "受保護列管中",
                "owner_or_manager": mgr if mgr and mgr != "無" else "嘉義縣政府",
                "protection_basis": "《森林法》樹木保護專章",
                "story": None,
                "remarks": None,
                "photo_url": None,
                "longitude": lon,
                "latitude": lat,
                "has_valid_coords": is_valid_tw_coord(lon, lat)
            }
            trees.append(t)
    print(f"    [+] Loaded {len(trees)} Chiayi trees (Valid coords: {sum(1 for t in trees if t['has_valid_coords'])})")
    return trees

def load_hualien_pdf_trees():
    path = os.path.join(EXTRACTED_DIR, "hualien_protected_trees.json")
    print(f"[*] Processing Hualien PDF Extracted Trees: {path}")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trees = []
    for item in data:
        lon = item.get("longitude")
        lat = item.get("latitude")
        sp = normalize_species(item.get("tree_name"))
        t = {
            "id": item.get("tree_id"),
            "tree_id": item.get("original_id"),
            "source_dataset": "hualien_county_pdf",
            "source_agency": item.get("owner") or "花蓮縣政府農業處",
            "source_ground_truth": {
                "title": "花蓮縣轄區受保護樹木列冊清冊 (官方公報 PDF)",
                "url": "https://ws.hl.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDIyL3JlbGZpbGUvOTg1NS83MDQxMy9lMTVlZGM2ZS1kNDExLTRhZTktYmViNC1lNjg3OTUyNzJlZmUucGRm&n=6Iqx6JOu57ij6L2E5Y2A5Y%2BX5L%2Bd6K235qi55pyo5YiX5YaK5riF5ZauLnBkZg%3D%3D",
                "agency": "花蓮縣政府農業處",
                "license": "花蓮縣政府公報公開文件"
            },
            "county": "花蓮縣",
            "township": "花蓮縣",
            "village": "",
            "address": item.get("location") or "花蓮縣轄內",
            "species_zh": sp,
            "scientific_name": None,
            "species_en": None,
            "estimated_age": item.get("estimated_age"),
            "tree_height_m": None,
            "dbh_m": item.get("dbh_m"),
            "bust_circumference_m": item.get("bust_circumference_m"),
            "crown_area_m2": None,
            "health_status": "受保護列管中",
            "owner_or_manager": item.get("owner") or "花蓮縣政府",
            "protection_basis": "《森林法》第38條之2受保護樹木",
            "story": None,
            "remarks": item.get("remarks"),
            "photo_url": None,
            "longitude": lon,
            "latitude": lat,
            "has_valid_coords": is_valid_tw_coord(lon, lat)
        }
        trees.append(t)
    print(f"    [+] Loaded {len(trees)} Hualien trees (Valid coords: {sum(1 for t in trees if t['has_valid_coords'])})")
    return trees

def merge_all_sources():
    print("=" * 70)
    print("STEP 3: MERGING AND DEDUPLICATING ALL DATASETS")
    print("=" * 70)

    # 1. Load all datasets
    national_trees = load_national_oldtree()
    taipei_trees = load_taipei_trees()
    taoyuan_trees = load_taoyuan_trees()
    chiayi_trees = load_chiayi_trees()
    hualien_trees = load_hualien_pdf_trees()

    # Create spatial lookup grid for national trees: (round(lat, 3), round(lon, 3)) -> list of trees
    grid = {}
    for t in national_trees:
        if t["has_valid_coords"]:
            key = (round(t["latitude"], 3), round(t["longitude"], 3))
            grid.setdefault(key, []).append(t)

    merged = list(national_trees)
    added_counts = {"taipei": 0, "taoyuan": 0, "chiayi": 0, "hualien": 0}

    # Helper to cross-match and enrich
    def integrate_list(tree_list, name_key):
        nonlocal added_counts
        for t in tree_list:
            if not t["has_valid_coords"]:
                merged.append(t)
                added_counts[name_key] += 1
                continue

            lat, lon = t["latitude"], t["longitude"]
            matched = False
            # Check adjacent grid cells
            r_lat, r_lon = round(lat, 3), round(lon, 3)
            for d_lat in [-0.001, 0, 0.001]:
                for d_lon in [-0.001, 0, 0.001]:
                    neighbor_key = (round(r_lat + d_lat, 3), round(r_lon + d_lon, 3))
                    for candidate in grid.get(neighbor_key, []):
                        # Within 20 meters and same county
                        dist = distance_meters(lon, lat, candidate["longitude"], candidate["latitude"])
                        if dist < 25 and candidate["county"] == t["county"]:
                            # Match found! Enrich candidate with municipal details
                            matched = True
                            if not candidate.get("scientific_name") and t.get("scientific_name"):
                                candidate["scientific_name"] = t["scientific_name"]
                            if not candidate.get("species_en") and t.get("species_en"):
                                candidate["species_en"] = t["species_en"]
                            if not candidate.get("dbh_m") and t.get("dbh_m"):
                                candidate["dbh_m"] = t["dbh_m"]
                            if not candidate.get("bust_circumference_m") and t.get("bust_circumference_m"):
                                candidate["bust_circumference_m"] = t["bust_circumference_m"]
                            # Add secondary source ground truth
                            candidate.setdefault("cross_referenced_sources", []).append(t["source_ground_truth"])
                            break
                    if matched:
                        break
                if matched:
                    break

            if not matched:
                merged.append(t)
                added_counts[name_key] += 1
                grid.setdefault((r_lat, r_lon), []).append(t)

    integrate_list(taipei_trees, "taipei")
    integrate_list(taoyuan_trees, "taoyuan")
    integrate_list(chiayi_trees, "chiayi")
    integrate_list(hualien_trees, "hualien")

    print(f"[*] Integration complete:")
    print(f"    - National Old Trees: {len(national_trees)}")
    print(f"    - Added Taipei Trees: {added_counts['taipei']}")
    print(f"    - Added Taoyuan Trees: {added_counts['taoyuan']}")
    print(f"    - Added Chiayi Trees: {added_counts['chiayi']}")
    print(f"    - Added Hualien Trees: {added_counts['hualien']}")
    print(f"    - TOTAL MERGED RECORDS: {len(merged)}")

    # 2. Output Master JSON
    with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[+] Master JSON saved: {MASTER_JSON_PATH} ({os.path.getsize(MASTER_JSON_PATH):,} bytes)")

    # 3. Output GeoJSON FeatureCollection
    geojson_features = []
    for t in merged:
        if t["has_valid_coords"]:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [t["longitude"], t["latitude"]]
                },
                "properties": {
                    "id": t["id"],
                    "tree_id": t["tree_id"],
                    "county": t["county"],
                    "township": t["township"],
                    "address": t["address"],
                    "species_zh": t["species_zh"],
                    "scientific_name": t.get("scientific_name"),
                    "species_en": t.get("species_en"),
                    "estimated_age": t.get("estimated_age"),
                    "tree_height_m": t.get("tree_height_m"),
                    "dbh_m": t.get("dbh_m"),
                    "bust_circumference_m": t.get("bust_circumference_m"),
                    "health_status": t.get("health_status"),
                    "owner_or_manager": t.get("owner_or_manager"),
                    "source_dataset": t["source_dataset"],
                    "source_agency": t["source_agency"],
                    "ground_truth_url": t["source_ground_truth"]["url"],
                    "story": t.get("story"),
                    "photo_url": t.get("photo_url")
                }
            }
            geojson_features.append(feature)

    geojson_doc = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "臺灣受保護樹木與珍貴老樹 GIS 圖資 (Master Dataset)",
            "updated_at": datetime.now().isoformat(),
            "total_features": len(geojson_features),
            "crs": "urn:ogc:def:crs:OGC:1.3:CRS84",
            "license": "政府資料開放授權條款第1版"
        },
        "features": geojson_features
    }

    with open(GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson_doc, f, ensure_ascii=False)
    print(f"[+] Master GeoJSON saved: {GEOJSON_PATH} ({os.path.getsize(GEOJSON_PATH):,} bytes, {len(geojson_features):,} features)")

    # 4. Generate Analytics Summary
    county_counts = Counter(t["county"] for t in merged)
    species_counts = Counter(t["species_zh"] for t in merged)
    age_100_plus = sum(1 for t in merged if t.get("estimated_age") and t["estimated_age"] >= 100)
    has_photo = sum(1 for t in merged if t.get("photo_url"))

    stats = {
        "generated_at": datetime.now().isoformat(),
        "total_trees_merged": len(merged),
        "total_gis_features": len(geojson_features),
        "counties_covered": len(county_counts),
        "trees_over_100_years": age_100_plus,
        "trees_with_photos": has_photo,
        "top_species": dict(species_counts.most_common(20)),
        "county_distribution": dict(county_counts.most_common()),
        "source_contributions": {
            "national_oldtree_life": len(national_trees),
            "taipei_cultural_bureau_added": added_counts["taipei"],
            "taoyuan_agri_bureau_added": added_counts["taoyuan"],
            "chiayi_county_gov_added": added_counts["chiayi"],
            "hualien_county_pdf_added": added_counts["hualien"],
        }
    }

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"[+] Statistics JSON saved: {STATS_PATH}")
    print(f"[✓] Step 3 Complete!")

if __name__ == "__main__":
    merge_all_sources()
