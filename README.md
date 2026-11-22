# Day22 — Projections

Equal Earth 與麥卡托的全球相對面積對照，保留亞洲500公里圈三投影案例。

- [互動地圖](https://dongpo.github.io/geomni-30daymap-2026-day22-projections/)
- [32秒實際操作影片](https://dongpo.github.io/geomni-30daymap-2026-day22-projections/video/)
- [資料與方法](DATA-NOTES.txt)
- [使用者修訂貼文](facebook-user-revision-zh.txt)

## 重現

前端無外部底圖、CDN或金鑰依賴，使用已計算的 world.js 與 asia/data.js。

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python scripts/build.py
.venv/bin/python asia/scripts/build.py
python -m http.server 8000
```

以瀏覽器開啟 http://localhost:8000 。來源資料已附，版本以 SHA256 識別。兩個 build.py 內含數值斷言，輸出 evidence/qa.json。

## 解讀限制

- 全球圖共同裁切南60至北85度，未納南極洲；洲別依來源分類，未拆跨洲國家。
- 相對面積取自Natural Earth概括輪廓，不是官方洲別統計。
- 麥卡托為WGS84橢球投影；不是Web Mercator。
- 動畫中間狀態為座標內插，非正式投影。下方數字固定列出兩個端點結果。
- 亞洲500公里圈為測地示範圈，不是實際旅行可達範圍。
- 影片32秒、1154×1080；原始瀏覽器畫面右側只補1px，沒有拉伸。30fps為編碼率，實際擷取間隔見video/qa.json。無音軌。

## 資料授權與署名

Natural Earth 1:110m資料為[Public Domain](https://www.naturalearthdata.com/about/terms-of-use/)。來源檔案、SHA256與處理限制見DATA-NOTES.txt。Geomni製圖與操作影片。程式與製作成果未另外宣告開源授權；公開可查閱不代表授予所有用途。
