# TYPEFIRE 打字遊戲 — 交接文件
> 給下一位 Claude 的完整說明

---

## 專案結構

| 角色 | 網址 |
|------|------|
| Public 主專案 | https://github.com/typefire-game/typefire-game.github.io |
| Private 專案 | https://github.com/tukdevs/typefire-data |

**Public 主專案檔案：**
- `index.html` — 遊戲主體（最新版：`index_20260410_0808.html`）
- `about.html` — 關於頁面（獨立頁面）
- `privacy.html` — 隱私政策（獨立頁面）
- `passages.json` — 10000 題題庫
- `manifest.json` — PWA manifest
- `icon.svg` — 向量圖示
- `icon-512.png` — 512px PNG 圖示
- `robots.txt` — 搜尋引擎設定
- `sitemap.xml` — 網站地圖
- `README.md` — 專案說明
- `.gitignore` — Git 忽略設定

**Private 專案檔案：**
- `fetch_passages_colab_20260405_1405.py` — 手動抓 10000 題（已完成，不需再跑）
- `update_passages_20260407_1037.py` — 每日自動抓 200 題、FIFO 替換、推送到 public repo
- `.github/workflows/fetch_20260407_1037.yml` — 每日 UTC 01:00 自動執行

---

## 目前狀態

- 最新 index.html 是 `index_20260410_0808.html`，已上傳 GitHub
- `passages.json`（10000 題）已在主專案根目錄
- about.html、privacy.html 是獨立頁面（有各自 URL），footer 直接連結
- Contact 頁面已移除（Privacy Policy 裡只有一段說明，無聯絡資訊）
- PWA 可安裝，manifest.json 已上傳
- GitHub Actions 每日自動更新題庫（需 Secrets：`GH_TOKEN`、`PUBLIC_REPO`）

---

## 設計規範

### 字體
- **單一字體**：Inter（Google Fonts），不同地方用不同字重
- 不使用 Bebas Neue 或 DM Mono（已全面替換）

### 配色（莫蘭迪森林深色系）
```css
--bg:        #272a26;   /* 背景 */
--bg-ad:     #20231f;   /* 廣告區背景 */
--surface:   #343832;   /* 卡片/框框 */
--border:    #3e433c;   /* 邊框 */
--ink:       #dae5d8;   /* 主文字 */
--muted:     #7a8a78;   /* 次要文字 */
--accent:    #5e8f58;   /* 主題色（綠） */
--accent-dk: #4a7244;   /* 深綠 */
--accent-cta:#72b06b;   /* CTA 按鈕用較亮綠色 */
--wrong:     #b09050;   /* 錯誤字元（亮土黃） */
--wrong-bg:  #38342e;   /* 錯誤字元背景 */
--correct:   #5e8f58;   /* 正確字元（同 accent） */
```

### 顏色使用原則
- 打字正確 → `--correct`（綠）
- 打字錯誤 → `--wrong`（亮土黃）+ `--wrong-bg` 底色
- GO / PLAY / TRY AGAIN 等 CTA 按鈕 → `--accent-cta`（較亮綠）
- 一般強調 → `--accent`

---

## 題庫架構

### passages.json 格式
```json
["passage text 1...", "passage text 2...", ...]
```
每題已是 1000+ keystrokes 的完整段落，來源只有英文 Wikipedia，數學/科學/哲學主題頁面。

### 前端載入邏輯
1. 頁面載入時，在第一個 `<script>`（非 module）立即 `fetch('passages.json')`，存成 `window._passagesPromise`
2. Module script 載入後 `await window._passagesPromise`，shuffle 後填入 `localPool`（20 題）
3. 每用一題補一題（從 `allPassages` 循環取）
4. 新遊戲開始時從 `localPool` 取題，不接續上一局

### 重要注意事項
- **ERROR 不一定是程式碼問題**：GitHub Pages deploy 需要 1–5 分鐘，deploy 期間 fetch 可能失敗
- passages.json 是 10000 題的大檔，正常網路幾乎即時載入

### 每日自動更新
- `update_passages.py` 從 Wikipedia 抓 200 題，FIFO 替換最舊的 200 題
- 推送到 public repo 的 `passages.json`
- 篩選邏輯與 fetch_passages 完全一致（English-only、1000+ keystrokes、同一篇最多 5 題等）

---

## 重要設計原則

- **不能有任何花費**（不用收費 API）
- **題目只來自英文 Wikipedia**（數學/科學/哲學主題頁面，非人物頁面）
- **每題 1000+ keystrokes**
- **排行榜**：Firebase Realtime Database（免費方案），只寫入前 100 名
- **廣告欄位**已預留（AdSense，尚未上線）
- **不能有 Service Worker**（會造成快取問題，每次載入都需要取得最新版）
- **檔名加時間戳** `_yyyymmdd_hhmm`（台灣時區，用 `TZ='Asia/Taipei' date '+%Y%m%d_%H%M'` 取得）
- **省 token**：不要開 GitHub 網頁，需要什麼資訊直接問使用者

---

## 手勢與觸控控制

```js
// 封鎖 pinch-zoom，保留垂直捲動（讓瀏覽器原生 PTR 可用）
html { touch-action: pan-y; }
document.addEventListener('gesturestart', e => e.preventDefault());
document.addEventListener('gesturechange', e => e.preventDefault());
document.addEventListener('touchmove', e => {
  if (e.touches.length > 1) e.preventDefault();
}, { passive: false });
```

- 橫向滑動封鎖：`overscroll-behavior-x: none`
- 原生 Pull-to-Refresh：保留（不做自製 PTR，回歸瀏覽器原生）

---

## 上一頁（Back）導航邏輯

採用「sentinel 策略」，不在每個 overlay 開關時 pushState：

```js
// 頁面載入時放兩個 entry（一個底層 + 一個 sentinel）
history.replaceState({tf:true}, '');
history.pushState({tf:true}, '');  // sentinel

window.addEventListener('popstate', () => {
  // 檢查當前最上層是什麼，關閉它
  // 首頁時：什麼都不做，re-push sentinel
  // 永遠 re-push sentinel，確保下一次 back 也被攔截
  history.pushState({tf:true}, '');
});
```

效果：
- 首頁按上一頁 → 留在首頁不動
- Leaderboard 按上一頁 → 關閉 leaderboard，回首頁
- 不會意外跳出網站或跑到其他頁面

---

## 密碼/信用卡自動填入防止

Ghost input 用 `type="search"` 而非 `type="text"`，可避免 Android Chrome 顯示密碼/信用卡自動填入橫幅：

```html
<input id="ghost-input" type="search"
  autocomplete="off" autocorrect="off" autocapitalize="none"
  spellcheck="false" inputmode="text" aria-hidden="true">
```

---

## Cookie Consent Banner

- 底部固定欄，簡短說明 essential cookies only
- 用 `localStorage.setItem('cookie_ok', '1')` 記住已確認
- 點 OK 後消失

---

## PWA

- `manifest.json` 已是獨立檔案（不再用 blob URL inline）
- 圖示：`icon.svg`（向量）+ `icon-512.png`（512px PNG）
- 兩個圖示都用幾何形狀繪製（不依賴字型），視覺一致
- 無 Service Worker（刻意不註冊，避免快取問題）

---

## 各頁面結構

### index.html
- Start screen（首頁）
- Result screen（成績）
- Leaderboard overlay
- Game UI（打字區）
- Mode picker modal
- Cookie consent banner
- Footer 在每個畫面都有（連結到 about.html、privacy.html）

### about.html / privacy.html
- 獨立頁面，有各自 URL（AdSense 審核需要）
- Header 有 logo + Home 按鈕
- Footer 有互相連結
- 文字段落下方有置中的 Home 按鈕
- 配色、字體與 index.html 完全一致

---

## 待辦事項

| 項目 | 狀態 |
|------|------|
| AdSense 廣告上線 | 待辦（廣告欄位已預留） |
| PWA 安裝體驗（banner 式） | 待辦 |
| 程式碼最小化（移到 private 專案） | 待辦 |

---

## 給新 Claude 的第一個指令

請上傳 `index_20260410_0808.html`，然後說明你要做什麼。
