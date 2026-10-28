# 🌲 臺灣受保護樹木與珍貴老樹 GIS 地理資訊系統
### (Taiwan Protected & Precious Old Trees WebGIS Platform)

> 依據《森林法》樹木保護專章與各縣市政府樹木保護自治法規，全自動抓取、提取（PDF 轉 Markdown）、正規化整併，並呈現於現代化 WebGIS 互動地圖。

![全台受保護樹木涵蓋 22 縣市](https://img.shields.io/badge/列管點位-11%2C428筆-emerald?style=for-the-badge&logo=treehouse)
![百年老樹](https://img.shields.io/badge/百年名木-1%2C362棵-amber?style=for-the-badge)
![零CORS離線可用](https://img.shields.io/badge/執行方式-免伺服器離線秒開-blue?style=for-the-badge)
![造訪人次](https://komarev.com/ghpvc/?username=SinLiongToo-TREE-GIS-LOCATION&label=VISITORS&color=10b981&style=for-the-badge)

🌐 **線上公開訪問入口 (Live Demos)**：
- 🟢 **GitHub Pages**: [https://sinliongtoo.github.io/TREE_GIS_LOCATION/](https://sinliongtoo.github.io/TREE_GIS_LOCATION/)
- 🟠 **Cloudflare Pages 分流鏡像**: [https://tree-gis-location.pages.dev/](https://tree-gis-location.pages.dev/)

---

## 🌟 成果展示與核心特色

1. **🗺️ 11,428 筆全國列管老樹空間分佈圖**：
   - 整合農業部林業試驗所（老樹報報）、臺北市文化局、桃園市農業局、嘉義縣政府、花蓮縣政府公報等官方權責資料。
   - 涵蓋全臺 22 縣市與離島（臺北、新北、桃園、臺中、臺南、高雄、花蓮、彰化、南投、苗栗、宜蘭、臺東、屏東、澎湖、金門、連江等）。
2. **📄 PDF 轉 Markdown (PDF to MD) 自動化提取**：
   - 針對花蓮縣政府等尚未開放 API、以 20 頁官方公報 PDF 發布的列冊清單，使用 PyMuPDF 自動解析表格。
   - 產出標準 Markdown 表格檔案 [`data/extracted_md/hualien_protected_trees.md`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/TREE_GIS_LOCATION/data/extracted_md/hualien_protected_trees.md)。
   - 將臺灣專用 **TWD97 二度分帶坐標** 即時高精度解算為 **WGS84 經緯度** 上圖。
3. **🧭 現代化 WebGIS 互動圖台**：
   - **多底圖切換**：Esri 深色底圖（免金鑰/無浮水印）、內政部國土測繪中心 (NLSC) 臺灣通用電子地圖、NLSC 衛星正射影像、OpenStreetMap。
   - **空間群聚 (MarkerCluster)**：流暢承載萬級點位，支援滑鼠滾輪縮放與點擊散開。
   - **多維交叉篩選器**：縣市、前 20 大樹種、樹齡門檻（百年老樹/五十年老樹）、胸高直徑 (DBH ≥ 1.5m / ≥ 1.0m)、主管來源機構、關鍵字模糊搜尋。
   - **獨立樹籍卡抽屜**：展示樹種、學名、編號、推估樹齡、胸徑/胸圍、樹高、健康狀態、土地所有權人/管理單位、田野沿革與照片，並附 Google 導航與原始政府連結。
   - **附近老樹 GPS 定位**：一鍵搜尋距離使用者目前位置最近的列管樹木與直線距離。
   - **格式匯出**：地圖支援將當前篩選結果一鍵匯出為 **GeoJSON (GIS 圖層)** 或 **CSV (Excel 試算表)**。

---

## 🚀 快速開始 (Quick Start)

### 1. 檢視 WebGIS 地圖
直接以瀏覽器開啟專案根目錄的 [`index.html`](file:///c:/Users/tu-hs/OneDrive/文件/2022_0308_MASA/2022-0708/Projects_antigravity/TREE_GIS_LOCATION/index.html)：
- **雙擊直接開啟**：已內建 Zero-CORS 資料包，免開本機伺服器即可直接離線在地圖上看點。
- **或啟動本機 HTTP 伺服器**：
  ```powershell
  python -m http.server 8000
  ```
  打開瀏覽器訪問 `http://localhost:8000`。

### 2. 重新執行完整資料管線
```powershell
python run_pipeline.py
```
*(4 秒內全自動完成抓取、提取、整併與圖台建置！)*

---

## 📁 目錄結構

```
TREE_GIS_LOCATION/
├── index.html                           # 🌟 核心成果：WebGIS 全國受保護樹木地圖平臺
├── run_pipeline.py                      # 一鍵執行全部 4 個階段之主控腳本
├── README.md                            # 專案介紹與操作指引
├── docs/
│   ├── WORKFLOW.md                      # 資料管線詳細流程與法源標準
│   └── PROJECT_MEMORY.md                # 專案持久記憶、架構決策與地雷紀錄
├── scripts/
│   ├── 01_fetch_datasets.py             # Step 1: 批次下載官方開放資料 (JSON/CSV/PDF)
│   ├── 02_extract_pdf_to_md.py          # Step 2: PDF 表格提取轉 Markdown 及結構化 JSON
│   ├── 03_merge_to_json.py              # Step 3: 坐標轉換、去重增強、Master JSON / GeoJSON
│   └── 04_build_gis_map.py              # Step 4: 產出 Zero-CORS bundle 與 WebGIS 平臺
└── data/
    ├── raw/                             # 官方原始資料檔
    │   ├── sources_manifest.json        # 各來源機關之 Metadata 憑證
    │   ├── oldtree_national.json        # 農業部林試所老樹報報 (10,461 筆)
    │   ├── taipei_protected_trees.csv   # 臺北市文化局 (3,874 筆)
    │   ├── taoyuan_protected_trees.csv  # 桃園市農業局 (595 筆)
    │   ├── chiayi_protected_trees.csv   # 嘉義縣政府 (93 筆)
    │   └── hualien_protected_trees.pdf  # 花蓮縣政府公報清冊 (20 頁 PDF)
    ├── extracted_md/                    # 提取輸出目錄
    │   ├── hualien_protected_trees.md   # PDF 提取之 Markdown 樹籍表格
    │   └── hualien_protected_trees.json # PDF 提取之結構化 JSON
    └── processed/                       # 最終處理成品
        ├── taiwan_protected_trees_master.json # 整合全屬性 Master 資料集
        ├── taiwan_protected_trees.geojson     # QGIS / GIS 專用空間圖層 (11,428 筆)
        ├── taiwan_protected_trees_data.js    # 離線 Zero-CORS 資料包
        └── statistics.json                    # 全國樹種與縣市分佈統計
```

---

## ☁️ 部署與 Cloudflare Pages 鏡像設定 (Cloudflare Mirror Guide)

本系統為 100% 純靜態前端架構，無伺服器相依性，支援同時部署於 **GitHub Pages** 與 **Cloudflare Pages** 達成全球 CDN 雙重鏡像分流：

### 1. GitHub Pages (已由 CI/CD 啟用)
- 網址：`https://<username>.github.io/<repo-name>/`
- 設定路徑：GitHub Repo -> `Settings` -> `Pages` -> Source 設為 `Deploy from a branch` (`main` / root)。

### 2. Cloudflare Pages 鏡像 (1 分鐘快速設定)
1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 點擊側邊欄 **Workers & Pages** -> **Create application** -> 選 **Pages**。
3. 點選 **Connect to Git** 並授權存取 GitHub 上的 `TREE_GIS_LOCATION` 儲存庫。
4. 設定建置組態 (Build settings)：
   - **Framework preset**: `None`
   - **Build command**: (保持空白)
   - **Build output directory**: `/` (或留空表示根目錄)
5. 點擊 **Save and Deploy**。
6. 完成後即可獲得官方免費且極速的全球 CDN 鏡像網址：`https://tree-gis-location.pages.dev/`。
7. 未來每當 GitHub `main` 分支推動更新，Cloudflare Pages 即會全自動同步重新部署！

---

## 🏛️ 資料權責依據 (Ground Truth Provenance)

| 資料集 | 主管機關 | 法律基礎 | 原始公開網址 |
| :--- | :--- | :--- | :--- |
| 全國城鄉老樹資源 | 農業部林業試驗所 / 中興大學 | 《森林法》第38條之2 | [https://oldtree.life/](https://oldtree.life/) |
| 臺北市受保護樹木 | 臺北市政府文化局 | 《臺北市樹木保護自治條例》 | [臺北市資料大平臺](https://data.taipei/dataset/detail?id=d9d1140b-c2c3-405f-8dd1-7b87b00f6f53) |
| 桃園市受保護樹木 | 桃園市政府農業局 | 《森林法》樹木保護專章 | [桃園市資料開放平台](https://opendata.tycg.gov.tw/dataset/detail?id=25bbcd34-16a8-4c4e-a341-4666cd0db5b4) |
| 嘉義縣受保護樹木 | 嘉義縣政府農業處 | 《森林法》第38條之2 | [政府資料開放平臺 (133889)](https://data.gov.tw/dataset/133889) |
| 花蓮縣受保護樹木 | 花蓮縣政府農業處 | 《森林法》第38條之2 | [花蓮縣政府全球資訊網公報](https://ws.hl.gov.tw/) |

---

## ⚖️ 免責與實務建議
本平臺整合之圖資供日常探訪、生態教學、學術研究與老樹踏查使用。若涉及工程開挖、土地開發、道路拓寬或建築執照審查評估，為確保符合《森林法》受保護樹木保護罰則規範，**應以基地所在縣市政府主管機關（各縣市農業局/處，臺北市為文化局）最新公告之實體地號列管名冊或正式公函為準**。
