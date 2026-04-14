# TYPEFIRE 打字遊戲 — 交接文件
> 給下一位 Claude 的完整說明

---

## 專案結構

| 角色 | 網址 |
|------|------|
| Public 主專案 | https://github.com/typefire-game/typefire-game.github.io |
| Private 專案 | https://github.com/tukdevs/typefire-data |

**Public 主專案檔案：**
- `index.html` — 遊戲主體
- `about.html` — 關於頁面
- `privacy.html` — 隱私政策
- `passages.json` — 10000 題題庫
- `manifest.json` — PWA manifest
- `icon.svg` — 向量圖示
- `icon-512.png` — 512px PNG 圖示（maskable，無圓角，讓 OS 決定形狀）
- `apple-touch-icon.png` — iOS 主畫面圖示 180px
- `favicon.ico` — 瀏覽器分頁圖示
- `og-image.png` — 社群分享預覽圖 1200×630
- `robots.txt`, `sitemap.xml`, `README.md`, `.gitignore`

**Private 專案檔案：**
- `update_passages.py` — 每日自動抓 200 題、FIFO 替換、推送到 public repo
- `.github/workflows/fetch.yml` — 每日 UTC 01:00 自動執行

---

## 目前狀態（截至 2026-04-14）

- 最新版本均已上傳 GitHub
- GitHub Actions 每日自動更新題庫（需 Secrets：`GH_TOKEN`、`PUBLIC_REPO`）
- PWA 可安裝，manifest.json 已設定 `purpose: maskable`
- AdSense 廣告欄位已預留，尚未上線

---

## 設計規範

### 字體
- **單一字體**：Inter（Google Fonts），不同地方用不同字重

### 配色（莫蘭迪森林深色系）
```css
--bg:        #272a26;
--bg-ad:     #20231f;
--surface:   #343832;
--border:    #3e433c;
--ink:       #dae5d8;
--muted:     #7a8a78;
--accent:    #5e8f58;
--accent-dk: #4a7244;
--accent-cta:#72b06b;
--wrong:     #b09050;
--wrong-bg:  #38342e;
--correct:   #dae5d8;
```

### 游標
- 獨立 `<div id="caret">` DOM 元素，`position:fixed`
- 每次打字後用 `getBoundingClientRect()` 精確定位，不用 `::before` 偽元素
- 尺寸：`width: calc(var(--word-size)*0.1)`、`height: calc(var(--word-size)*1.2)`

---

## RWD 排版原則

- **所有尺寸用 `rem`**，不用 `px`（例外：`border: 1.5px`、`ghost-input font-size: 16px`、canvas 繪圖）
- **高度用 `100dvh`**，不用 `100vh`
- **Breakpoint**：`@media(min-width: 37.5rem)`（= 600px）
- **PWA standalone**：`@media(display-mode: standalone)` 用於 PWA 專屬排版調整
- **max-width**：`42.5rem`（主容器）、`20rem`（成績頁內容）、`17.5rem`（GO/Leaderboard 按鈕）

---

## 題庫架構

### passages.json 格式
```json
["passage text 1...", "passage text 2...", ...]
```
每題已是 1000+ keystrokes 的完整段落，來源只有英文 Wikipedia，數學/科學/哲學主題頁面。

### 前端載入邏輯（重要）
1. **Passage engine 完全在 non-module script（window scope）**，不依賴 Firebase CDN
2. 頁面載入時立即 `fetch('passages.json')`
3. fetch 完成後立即 `window._passagesReady=true`，不等 Firebase
4. GO 按下後**立刻進入遊戲畫面**，不顯示 `...`
5. 若 passages 未就緒，題目區靜默空白；超過 2 秒才顯示 `LOADING…`

---

## 重要設計原則

- **不能有任何花費**（不用收費 API）
- **題目只來自英文 Wikipedia**（數學/科學/哲學主題頁面，非人物頁面）
- **每題 1000+ keystrokes**
- **排行榜**：Firebase Realtime Database（免費方案），只寫入前 100 名
- **廣告欄位**已預留（AdSense，尚未上線）
- **不能有 Service Worker**（會造成快取問題）
- **檔名加時間戳** `_yyyymmdd_hhmm`（台灣時區，用 `TZ='Asia/Taipei' date '+%Y%m%d_%H%M'` 取得）
- **省 token**：不要開 GitHub 網頁，需要什麼資訊直接問使用者

---

## 各頁面結構

### index.html 畫面流程
1. **Start screen**（首頁）：廣告 → LEADERBOARD → 15s/30s/60s → GO → footer
2. **Game UI**（打字區）：header（TYPEFIRE + LEADERBOARD + 倒數）→ stats → progress bar → 題目區 → 廣告 → footer
3. **Result screen**（成績頁）：Home → YOUR SPEED → WPM → 4 格統計 → 廣告 → nickname → LEADERBOARD + SHARE → PLAY AGAIN → footer（Home · Install）
4. **Leaderboard overlay**
5. **Mode picker modal**（select mode 視窗）

### Select mode 視窗位置
- `align-items: flex-end`、`padding-bottom: 8dvh`
- 從任何入口開啟位置都一樣，純 CSS，無 JS 動態計算

### about.html / privacy.html
- footer 有 Install PWA 連結（含獨立 JS 處理 beforeinstallprompt）

---

## 手勢與觸控控制

```js
html { touch-action: pan-y; }
document.addEventListener('gesturestart', e => e.preventDefault());
document.addEventListener('gesturechange', e => e.preventDefault());
document.addEventListener('touchmove', e => {
  if (e.touches.length > 1) e.preventDefault();
}, { passive: false });
```

---

## 上一頁（Back）導航邏輯

採用「sentinel 策略」：初始化時 `history.pushState` 一個 sentinel，`popstate` 時檢查當前畫面狀態並關閉最上層。

---

## 防止密碼/信用卡自動填入

- Ghost input 用 `type="search"`
- Nickname input 也用 `type="search"` + `autocomplete="off"`

---

## Cookie Consent Banner

- 底部固定欄，用 `localStorage.setItem('cookie_ok', '1')` 記住已確認

---

## PWA

- `manifest.json` 已是獨立檔案
- 圖示：`icon.svg`（向量，favicon 用）+ `icon-512.png`（512px，`purpose: maskable`）+ `apple-touch-icon.png`（180px，iOS）+ `favicon.ico`
- icon 設計：深色背景（#272a26）滿版正方形（無圓角）+ T 字母居中 + 底部綠條（#5e8f58，y=450）
- 無 Service Worker（刻意不註冊）

---

## 社群分享（Share Card）

- Canvas 繪製，用 `devicePixelRatio`（最低 3.125，約 300dpi）
- 分享用 Web Share API，fallback 下載
- Gmail 主旨問題：Web Share API 無法控制 Gmail 主旨，已知限制，無解

---

## GitHub Actions（Private Repo）

### Secrets 需求
| 名稱 | 值 |
|------|-----|
| `GH_TOKEN` | GitHub PAT（有 public repo write 權限）|
| `PUBLIC_REPO` | `typefire-game/typefire-game.github.io` |

### 正常執行的 log 特徵
```
Fetched 200 new passages.
Updated pool: 10000 passages (removed 200 old, added 200 new)
  [github] pushed passages.json — 200
Done.
```

### 常見失敗原因
1. `GH_TOKEN` 或 `PUBLIC_REPO` Secret 未設定或值錯誤
2. `passages.json` 超過 1MB → 腳本已改用 Git blob API 讀取大檔案
3. Wikipedia API 回應異常

---

## 已知待修問題（給下一位 Claude）

### 1. 成績頁 PLAY AGAIN 按鈕高度太高
**症狀**：nickname 輸入欄 focus（出現鍵盤）時，PLAY AGAIN 按鈕被 flex 撐大，佔據大量空間。

**根本原因**：`#result-screen` 是 `display:flex; flex-direction:column; overflow-y:auto`，PLAY AGAIN 沒有設 `flex-shrink:0`，被 flex 撐大。

**修法**：
```css
#result-screen .again-btn {
  flex-shrink: 0;
  padding: .75rem 0;
  font-size: 1.2rem;
}
#result-screen .share-btn {
  flex-shrink: 0;
}
```
同時確認 result screen 的所有子元素都加 `flex-shrink:0`。

---

## 給新 Claude 的第一個指令

請上傳最新版的 `index.html`、`about.html`、`privacy.html`，然後說明你要做什麼。

