# TYPEFIRE 打字遊戲 — 交接文件
> 給下一位 Claude 的完整說明

---

## 專案結構

| 角色 | 網址 |
|------|------|
| Public 主專案 | https://github.com/typefire-game/typefire-game.github.io |
| Private 專案 | https://github.com/tukdevs/typefire-data |

**Public 主專案檔案：**
- `index.html` — 遊戲主體（最新版：`index_20260410_1939.html`）
- `about.html` — 關於頁面（最新版：`about_20260410_1446.html`）
- `privacy.html` — 隱私政策（最新版：`privacy_20260410_1446.html`）
- `passages.json` — 10000 題題庫
- `manifest.json` — PWA manifest
- `icon.svg` — 向量圖示（最新版：`icon_20260410_1923.svg`）
- `icon-512.png` — 512px PNG 圖示（最新版：`icon-512_20260410_1923.png`）
- `apple-touch-icon.png` — iOS 主畫面圖示 180px（最新版：`apple-touch-icon_20260410_1923.png`）
- `favicon.ico` — 瀏覽器分頁圖示（最新版：`favicon_20260410_1923.ico`）
- `og-image.png` — 社群分享預覽圖 1200×630（最新版：`og-image_20260410_1930.png`）
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

- 最新 index.html 是 `index_20260410_1939.html`，已上傳 GitHub
- about.html、privacy.html 最新版是 `*_20260410_1446.html`
- 圖示全套已更新（icon.svg、icon-512.png、apple-touch-icon.png、favicon.ico、og-image.png）
- `passages.json`（10000 題）已在主專案根目錄
- Contact 頁面已移除（Privacy Policy 裡只有一段說明，無聯絡資訊）
- PWA 可安裝，manifest.json 已上傳
- GitHub Actions 每日自動更新題庫（需 Secrets：`GH_TOKEN`、`PUBLIC_REPO`）

---

## 設計規範

### 字體
- **單一字體**：Inter（Google Fonts），不同地方用不同字重

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
--correct:   #dae5d8;   /* 正確字元（同 --ink，接近白的亮色）*/
```

### 顏色使用原則
- 打字正確 → `--correct`（`#dae5d8`，接近白色的亮色）
- 打字錯誤 → `--wrong`（亮土黃）+ `--wrong-bg` 底色
- GO / PLAY / TRY AGAIN 等 CTA 按鈕 → `--accent-cta`（較亮綠）
- 一般強調 → `--accent`

### 游標樣式
```css
.char.cursor::before {
  content:''; position:absolute; left:-0.06em; top:-0.1em; height:1.2em;
  width:0.1em; background:var(--accent); border-radius:0.25rem;
  animation:blink 1s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
```
- 寬度用 `em`（跟字體等比）
- smooth 漸變閃爍（非 step-end）
- 高度 1.2em（超出字高一點，參考 monkeytype 風格）

---

## RWD 排版原則

這個專案嚴格遵守 RWD 規範，詳見 `rwd_guidelines_20260410_1440.md`。重點：

- **所有尺寸用 `rem`**，不用 `px`（例外：`border: 1.5px`、`ghost-input font-size: 16px` 防 iOS 縮放、canvas 繪圖）
- **高度用 `100dvh`**，不用 `100vh`
- **底部安全區**：fixed/bottom 元素加 `padding-bottom: max(Xrem, env(safe-area-inset-bottom))`
- **Breakpoint**：`@media(min-width: 37.5rem)`（= 600px）
- **Flexbox 防擠壓**：可縮元素 `flex:1; min-width:0`，不可縮元素 `flex-shrink:0; white-space:nowrap`
- **max-width**：`42.5rem`（主容器）、`20rem`（成績頁內容）、`17.5rem`（GO/Leaderboard 按鈕）
- **觸控目標**：footer 連結加 `padding:.6rem .45rem` 確保 ≥ 44px 點擊區域
- **全域圖片**：`img, video { max-width:100%; height:auto; }`

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

採用「sentinel 策略」：

```js
history.replaceState({tf:true}, '');
history.pushState({tf:true}, '');  // sentinel

window.addEventListener('popstate', () => {
  // 檢查當前最上層是什麼，關閉它
  history.pushState({tf:true}, '');
});
```

---

## 防止密碼/信用卡自動填入

- Ghost input 用 `type="search"`
- Nickname input 也用 `type="search"` + `autocomplete="off"`（不可用 `type="text"` 或 `autocomplete="username"`，會觸發自動填入橫幅）
- Search 清除按鈕用 CSS 隱藏：`.nickname-input::-webkit-search-cancel-button { display:none; }`

```html
<input type="search" autocomplete="off" autocorrect="off"
  autocapitalize="none" spellcheck="false" inputmode="text">
```

---

## Cookie Consent Banner

- 底部固定欄，文字分兩行（第一行說明、第二行 Privacy Policy 連結）
- 用 `localStorage.setItem('cookie_ok', '1')` 記住已確認
- 點 OK 後消失

---

## PWA

- `manifest.json` 已是獨立檔案
- 圖示：`icon.svg`（向量）+ `icon-512.png`（512px PNG）+ `apple-touch-icon.png`（180px，iOS 用）+ `favicon.ico`（16/32/48px，瀏覽器分頁用）
- 無 Service Worker（刻意不註冊，避免快取問題）

---

## 社群分享

### OG / Twitter Card
```html
<meta property="og:title" content="TYPEFIRE — Typing Speed Test">
<meta property="og:image" content="https://typefire-game.github.io/og-image.png">
<meta property="og:url" content="https://typefire-game.github.io">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://typefire-game.github.io/og-image.png">
```

### Share Card（成績分享）
- 用 Canvas 繪製 800×420 圖片
- 用 Web Share API 分享（含 title、text、file）
- Title: `TYPEFIRE — {wpm} WPM`
- Text: `I typed {wpm} WPM with {acc} accuracy on TYPEFIRE! Can you beat me?\ntypefire-game.github.io`
- Fallback：直接下載圖片

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
- **非首頁的所有 footer 都有 Home 連結**（用 `js-go-home` class）

### about.html / privacy.html
- 獨立頁面，有各自 URL（AdSense 審核需要）
- Header 有 logo + Home 按鈕（無箭頭）
- Footer 有 Home + 互相連結
- 文字段落下方有置中的 Home 按鈕（無箭頭）
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

請上傳 `index_20260410_1939.html`、`about_20260410_1446.html`、`privacy_20260410_1446.html`，然後說明你要做什麼。
