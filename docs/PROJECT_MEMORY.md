# Project Memory: 臺灣受保護樹木與珍貴老樹 GIS (TREE_GIS_LOCATION)

## 一、 核心事實 (Durable Facts)
1. **法源依據**：臺灣樹木保護核心法規為《森林法》第38條之2至第38條之6「樹木保護專章」以及中央農委會（現農業部）《森林以外之樹木普查方法及受保護樹木認定標準》；地方政府自治法規包含《臺北市樹木保護自治條例》、《高雄市特定紀念樹木保護自治條例》、《新北市珍貴樹木保護措施》等。
2. **全國整合性資料集**：農業部林業試驗所建立的「老樹報報」（全國城鄉老樹資源調查資料庫，`https://map.oldtree.life/api/Tree/trees`）收錄全臺 22 縣市達 10,461 筆老樹，為目前涵蓋面最廣的真實基準資料庫。
3. **地方縣市開放資料差異**：
   - 臺北市文化局（`data.taipei`）提供全臺最完備的受保護樹木開放資料，共 3,874 筆（含經緯度與樹胸徑）。
   - 桃園市農業局提供 595 筆（含 GPS 坐標與胸徑）。
   - 嘉義縣政府提供 92 筆，但坐標為 TWD97（二度分帶 TM2 投影），檔案編碼為 Big5。
   - 花蓮縣政府等以 20 頁官方公報 PDF 形式發布，含 TWD97 坐標（x:312659, y:2653235 等）。
4. **坐標轉換**：TWD97 TM2 zone 121 (EPSG:3826) 透過高斯克呂格反算可精確無損轉換為 WGS84 (EPSG:4326)。
5. **資料庫去重與增強**：空間距離在 25 公尺以內且縣市相同的樹木進行多源交叉比對與合併，保留雙重來源憑證。

## 二、 決策紀錄 (Decisions)
1. **PDF 提取策略**：使用 PyMuPDF (`fitz.open().find_tables()`) 進行向量表格抽取，結構化轉為 Markdown (`data/extracted_md/hualien_protected_trees.md`) 及 JSON。
2. **Zero-CORS 離線架構**：為避免使用者直接雙擊 `index.html`（`file:///` 協議）時被瀏覽器阻擋本地 JSON fetch，特別在 Step 4 生成 `data/processed/taiwan_protected_trees_data.js`，將圖資掛載至 `window.TAIWAN_TREES_GEOJSON`，實現免伺服器離線秒開。
3. **圖資圖層**：預設載入 Esri World Dark Gray Canvas（免 API Key、零浮水印）搭配內政部國土測繪中心 (NLSC) 臺灣通用電子地圖與正射影像圖、以及 OpenStreetMap。
4. **雲端部署與訪客計數**：
   - GitHub 儲存庫：`https://github.com/SinLiongToo/TREE_GIS_LOCATION`
   - GitHub Pages 正式發布網址：`https://sinliongtoo.github.io/TREE_GIS_LOCATION/`
   - 訪客計數徽章：整合 `komarev.com/ghpvc` 於頂部狀態欄、側邊欄底端與 README，並加入 `.nojekyll` 確保純靜態資源完整提供。
   - Cloudflare Pages 鏡像：支援由 Cloudflare Pages 連接 GitHub `SinLiongToo/TREE_GIS_LOCATION`，自動派發全球 Edge CDN 鏡像網址。
5. **創作源起與人文實踐**：本 WebGIS 系統以作者杜信龍原創台語科幻生態繪本《CHHIAU-CHHŌE樹王公》（搜揣樹王公，史秀里冊房，ISBN 9786269928811）為靈感核心，將主角夢境「搜揣樹王公」轉化為現實全臺 11,428 筆老樹空間探查，並於系統首頁 Title、導覽列、專屬 Modal、`README.md` 及專冊 `README_CHHIAU_CHHOE.md` 完整串聯。
6. **全國樹木修剪作業手冊與技術規範整合**：整合中央上位機關（農業部林保署、林試所、國土管理署第02902章植栽養護）與地方指標縣市（臺北、新北、高雄、臺南）之官方樹木修剪手冊、技術規範與 PDF 下載途徑，於頂部 Header、側邊欄及三欄 Tab 分頁 Modal 內提供使用者直接一鍵查閱。
7. **多源真實底圖快速切換器與 Google 360° 街景聯動**：
   - 地圖左上方常駐顯眼快捷切換膠囊按鈕：`[深色底圖] [🛰️ Google 衛星空照] [臺灣電子地圖]`，徹底解決使用者找不到 Leaflet 預設右上角微小收合圖層控制項的問題。
   - 整合免 API Key 之 Google Hybrid 實時衛星混合空拍（`lyrs=y`，含繁體中文路名地標、公園建築輪廓）與 Esri World Imagery 高解析空拍。
   - 老樹檔案抽屜（Dossier）新增「360° 街景」快捷鈕，動態串接 Google Maps Street View 參數（`api=1&map_action=pano&viewpoint={lat},{lon}`），一鍵直擊現場老樹實景。

## 三、 常見地雷與注意事項 (Gotchas)
1. **Windows 控制台編碼**：PowerShell 預設為 CP950，Python 腳本內必須加入 `sys.stdout.reconfigure(encoding='utf-8')`，以防 Unicode 符號（如 Checkmark）引發 `UnicodeEncodeError`。
2. **政府網站 SSL 限制**：部分地方政府網站（如嘉義縣）使用的 SSL 密鑰長度較短，直接使用 Python 內建 urllib 會報 `[SSL: DH_KEY_TOO_SMALL]`，因此在腳本中建立了自動調用 `curl.exe -k -sL` 的容錯回退機制。
3. **CartoDB 圖資 API Key 限制與浮水印**：CartoDB 自 2024 年底起針對未帶 API Key 的 `basemaps.cartocdn.com` 請求加上全螢幕斜向「API KEY REQUIRED carto.com/basemaps/apikey」浮水印。WebGIS 解決方案為改採 Esri World Dark Gray Canvas（Base + Reference）作為深色底圖，穩定、免 API Key 且支援高縮放比。
4. **Tailwind 按鈕高亮覆蓋問題**：在切換樹齡與 DBH 按鈕時，若只 add 作用中色彩類別而未主動 remove `border-slate-700 bg-slate-800 text-slate-300`，Tailwind 生成的 slate 暗色類別在層疊順序上會壓制 `bg-emerald-500/20`，導致視覺無反饋。已於 CSS 加入 `.filter-age-btn.active, .filter-dbh-btn.active` 專屬樣式規則搭配 JS 徹底清洗類別解決。
