#!/usr/bin/env python3
"""
Step 2: PDF Extraction Pipeline (PDF to MD & JSON)
Extracts official Protected Trees Gazette PDF from Hualien County Government
using PyMuPDF (fitz), converts TWD97 coordinates to WGS84, and outputs:
- data/extracted_md/hualien_protected_trees.md (Human-readable Markdown table)
- data/extracted_md/hualien_protected_trees.json (Machine-readable JSON)
"""

import os
import sys
import re
import math
import json
from datetime import datetime
import fitz  # PyMuPDF

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "data", "raw", "hualien_protected_trees.pdf")
MD_OUT_DIR = os.path.join(BASE_DIR, "data", "extracted_md")
os.makedirs(MD_OUT_DIR, exist_ok=True)

MD_PATH = os.path.join(MD_OUT_DIR, "hualien_protected_trees.md")
JSON_PATH = os.path.join(MD_OUT_DIR, "hualien_protected_trees.json")

def twd97_to_wgs84(x, y):
    """Converts Taiwan TWD97 (EPSG:3826 TM2 zone 121) to WGS84 (EPSG:4326)"""
    try:
        x = float(x)
        y = float(y)
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

def clean_cell(val):
    if val is None:
        return ""
    val = str(val).strip()
    val = re.sub(r'\s+', ' ', val)
    return val

def extract_pdf():
    print(f"[*] Opening PDF: {PDF_PATH}")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}")

    doc = fitz.open(PDF_PATH)
    print(f"    Total pages in PDF: {len(doc)}")

    all_records = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        tabs = page.find_tables()
        if not tabs.tables:
            continue
        
        tab = tabs.tables[0]
        extracted = tab.extract()
        
        # Determine table rows
        for row in extracted:
            if not row or len(row) < 5:
                continue
            first_col = clean_cell(row[0])
            # Skip title / header rows
            if "花蓮縣" in first_col or "編號" in first_col or not first_col:
                continue

            # Row layout in Hualien PDF:
            # ['花蓮03', '松園別館', '琉球松', '89年', '2.9', '0.92', '105', '國軍退除役官兵輔導會...', 'x:312659', 'y:2653235', '1', '原樹保條例列管']
            tree_id = first_col
            location = clean_cell(row[1]) if len(row) > 1 else ""
            species = clean_cell(row[2]) if len(row) > 2 else ""
            age_str = clean_cell(row[3]) if len(row) > 3 else ""
            bust_str = clean_cell(row[4]) if len(row) > 4 else ""
            dbh_str = clean_cell(row[5]) if len(row) > 5 else ""
            crown_str = clean_cell(row[6]) if len(row) > 6 else ""
            owner = clean_cell(row[7]) if len(row) > 7 else ""
            
            # Extract coordinates from remaining columns or text
            coord_x = None
            coord_y = None
            quantity = "1"
            remark = ""

            # Check col 8 and 9 for x: and y:
            combined_tail = " ".join([clean_cell(c) for c in row[8:] if c])
            mx = re.search(r'x\s*[:：]?\s*([0-9.]+)', combined_tail, re.IGNORECASE)
            my = re.search(r'y\s*[:：]?\s*([0-9.]+)', combined_tail, re.IGNORECASE)
            if mx:
                coord_x = mx.group(1)
            if my:
                coord_y = my.group(1)

            for c in row[8:]:
                c_str = clean_cell(c)
                if "原樹保" in c_str or "列管" in c_str or "公告" in c_str or "解除" in c_str:
                    remark = c_str
                elif c_str.isdigit() and int(c_str) < 100 and not mx:
                    quantity = c_str

            # Parse numeric age, dbh, bust
            age_num = None
            mage = re.search(r'(\d+)', age_str)
            if mage:
                age_num = int(mage.group(1))

            try:
                dbh_num = float(dbh_str) if dbh_str else None
            except ValueError:
                dbh_num = None

            try:
                bust_num = float(bust_str) if bust_str else None
            except ValueError:
                bust_num = None

            # Convert coords
            lon, lat = twd97_to_wgs84(coord_x, coord_y) if coord_x and coord_y else (None, None)

            record = {
                "source": "花蓮縣政府農業處官方公告清冊 (PDF)",
                "source_id": "hualien_county_pdf",
                "county": "花蓮縣",
                "tree_id": f"HL-{tree_id}",
                "original_id": tree_id,
                "tree_name": species,
                "scientific_name": None,
                "location": location,
                "estimated_age": age_num,
                "age_display": age_str,
                "bust_circumference_m": bust_num,
                "dbh_m": dbh_num,
                "crown_area_m2": crown_str,
                "owner": owner,
                "coord_twd97_x": coord_x,
                "coord_twd97_y": coord_y,
                "longitude": lon,
                "latitude": lat,
                "remarks": remark
            }
            all_records.append(record)

    print(f"    [+] Successfully extracted {len(all_records)} protected trees from PDF!")

    # Output to Markdown (.md)
    md_lines = [
        "# 花蓮縣轄區受保護樹木列冊清冊 (PDF 提取結果)",
        "",
        "> **資料來源**：花蓮縣政府農業處公告之《花蓮縣轄區受保護樹木列冊清冊》",
        "> **依據法規**：《森林法》第38條之2暨森林以外之樹木普查方法及受保護樹木認定標準",
        f"> **提取時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> **有效解析總樹數**：{len(all_records)} 棵",
        "",
        "## 一、 摘要統計 (Summary Statistics)",
        "",
    ]

    # Species distribution
    species_counter = {}
    for r in all_records:
        sp = r["tree_name"] or "未記錄樹種"
        species_counter[sp] = species_counter.get(sp, 0) + 1

    md_lines.append("| 樹種 | 數量 | 佔比 |")
    md_lines.append("| :--- | :--- | :--- |")
    for sp, cnt in sorted(species_counter.items(), key=lambda x: x[1], reverse=True):
        pct = (cnt / len(all_records)) * 100 if all_records else 0
        md_lines.append(f"| {sp} | {cnt} | {pct:.1f}% |")

    md_lines.append("")
    md_lines.append("## 二、 完整受保護樹木清冊明細 (Detailed Table)")
    md_lines.append("")
    md_lines.append("| 編號 | 座落地點 | 樹種 | 推估樹齡 | 胸圍 (m) | 胸徑 (m) | 經度 (WGS84) | 緯度 (WGS84) | 土地所有權人 | 備註 |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for r in all_records:
        lon_s = str(r['longitude']) if r['longitude'] is not None else "-"
        lat_s = str(r['latitude']) if r['latitude'] is not None else "-"
        age_s = f"{r['estimated_age']} 年" if r['estimated_age'] else "-"
        bust_s = f"{r['bust_circumference_m']:.2f}" if r['bust_circumference_m'] is not None else "-"
        dbh_s = f"{r['dbh_m']:.2f}" if r['dbh_m'] is not None else "-"
        loc_s = r['location'].replace("|", "/")
        owner_s = r['owner'].replace("|", "/")
        rem_s = r['remarks'].replace("|", "/")
        md_lines.append(f"| {r['original_id']} | {loc_s} | {r['tree_name']} | {age_s} | {bust_s} | {dbh_s} | {lon_s} | {lat_s} | {owner_s} | {rem_s} |")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"    [+] Markdown generated at: {MD_PATH}")

    # Output to JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"    [+] JSON generated at: {JSON_PATH}")

    return all_records

if __name__ == "__main__":
    extract_pdf()
