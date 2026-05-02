# TYPEFIRE — 交接文件
**時間戳：20260416_2206**

---

## 專案概述

TYPEFIRE 是一個純前端打字速度測試 PWA，託管在 GitHub Pages（`typefire-game.github.io`）。無後端，Firebase Realtime Database 作為 leaderboard 資料存取。使用者匿名，owner 不希望個人資訊出現在任何公開頁面。

---

## 檔案結構

```
index.html          — 主頁面（首頁 + 遊戲 + 成績）
leaderboard.html    — Leaderboard 獨立頁面（新增）
about.html
privacy.html
manifest.json
passages.json       — 題目資料（未上傳，存放在 repo）
icon-512.png
icon.svg
favicon.ico
apple-touch-icon.png
og-image.png
```

### 輸出檔案命名規則
**一定要加台灣時間時間戳**：`TZ='Asia/Taipei' date '+%Y%m%d_%H%M'`
例：`index_20260416_1516.html`

---

## 技術架構

### CSS 設計原則
- **RWD 優先**：完全禁用 `px` 單位（除非框架強制），一律用 `rem`、`em`、`%`、`dvh`、`dvw`、`clamp()`
- breakpoint：`@media(min-width:37.5rem)` 寬版
- PWA standalone：`@media(display-mode:standalone)`
- **Design tokens**（`:root`）：

```css
--bg:        #272a26
--bg-ad:     #20231f
--surface:   #343832
--border:    #3e433c
--ink:       #dae5d8
--muted:     #7a8a78
--accent:    #5e8f58
--accent-dk: #4a7244
--accent-cta:#72b06b   /* CTA 按鈕用，比 accent 亮 */
--wrong:     #b09050
--wrong-bg:  #38342e
--correct:   #dae5d8
--font:      'Inter', sans-serif
--word-size: 1.5rem
--word-lh:   2.6
```

### 防止文字選取 / 反白規則
- 全域：`body, button, a, div, span, p, header, footer { user-select:none; -webkit-user-select:none; }`
- 全域：`-webkit-tap-highlight-color:transparent`（在 `*` selector 上）
- 所有 `:hover` 規則必須包在 `@media(hover:hover){}` 裡（觸控裝置不觸發 hover）
- 所有互動元件都要有 `:focus, :focus-visible { outline:none; 還原原始顏色 }` 防止長按後殘留變色
- JS `touchend` 監聽：300ms 後 `blur()` 被點到的 button/a

### 捲動鎖定策略
- **CSS 層**：`html/body` **不**加 `overflow:hidden`（會破壞 PTR 和 input focus）
- **打字時**：`resetGame()` 裡設 `document.documentElement.style.touchAction='none'` + `document.body.style.overflow='hidden'`
- **遊戲結束 / 回首頁**：`endGame()` / `goHome()` 各自還原為 `touchAction='pan-y'` + `overflow=''`
- **touchmove listener**：`passive:false`，偵測到 `touchAction==='none'` 時呼叫 `preventDefault()`（白名單：`.lb-list`）
- Pull-to-refresh 依賴 body 能 overscroll，**不能**在 CSS 鎖 body

---

## 頁面結構（index.html）

### 畫面狀態
全部畫面都是 `position:fixed; inset:0`，靠 JS 切換 display/class：

| 畫面 | ID | 觸發條件 |
|---|---|---|
| 首頁 | `#start-screen` | 預設顯示 |
| 遊戲 | `#game-screen` | GO 按鈕後（無 show class，直接設 display） |
| 成績 | `#result-screen` | 時間結束，加 `.show` class |
| Leaderboard overlay | `#lb-overlay` | 遊戲中右上角 LEADERBOARD（仍保留，未移除） |
| Mode picker | `#mode-picker` | 部分流程觸發 |

### 首頁 flex 間距（start-screen）
- 兩個 spacer div：`style="flex:1"` 和 `style="flex:2"`
- PWA standalone 用 `@media(display-mode:standalone)` 微調 flex 比例，讓視覺間距與網頁版一致
- **不**用 px 計算，用 flex 比例吸收多餘高度

### 成績頁結構
```
#result-screen (position:fixed, overflow-y:auto, scrollbar hidden)
  ├── result-top-bar (Home btn)
  ├── result-label / result-wpm / result-sub
  ├── rank-badge (條件顯示)
  ├── result-grid (4格統計)
  ├── #result-spacer (flex:1，把後面群組往下推)
  ├── ad-placeholder
  ├── nickname-row (input)
  ├── result-btns (🏆 LEADERBOARD + SHARE)
  ├── again-btn (PLAY AGAIN)
  └── site-footer (margin-top:auto 固定底部)
```

---

## Leaderboard

### 重要改動（本輪）
- **獨立頁面** `leaderboard.html`，支援 `?t=15/30/60` URL 參數
- 首頁 LEADERBOARD 按鈕改為 `<a href="leaderboard.html?t=...">` (`.start-lb-btn`)，需加 `text-decoration:none`
- 成績頁 LEADERBOARD 按鈕：先呼叫 `submitOnLeave()`，再 `location.href='leaderboard.html?t=...'`
- 遊戲畫面右上角 LEADERBOARD overlay（`#lb-overlay`）仍保留

### 資料庫路徑
```
scores/15/   scores/30/   scores/60/
```
每筆資料：`{ name, wpm, acc, ts }`
只儲存前 100 筆（submitScore 會先查，若排名 >100 則不寫入）

### checkRank 邏輯
- 遊戲結束後立即呼叫一次（不等 nickname）
- `allScores.filter(s => s.wpm > wpm).length + 1` = 排名
- 只有排名 ≤ 10 才顯示 badge
- emoji：🏆 #1 / 🥈 #2 / 🥉 #3 / 其他顯示 `#N on LEADERBOARD`

---

## Firebase

```js
apiKey: "AIzaSyClQ0SV1vuQiy_2Ji3_1YpnYJcmmt_WXlQ"
databaseURL: "https://typefire-e5c68-default-rtdb.asia-southeast1.firebasedatabase.app"
projectId: "typefire-e5c68"
appId: "1:1065566297610:web:c109b00d44a8cbb3fec9f3"
```
SDK 版本：`firebase@10.12.2`（index.html）/ `10.12.0`（leaderboard.html，可統一）

---

## Passages 載入

- 頁面頂部（module 外）先 fetch `passages.json`，存入 `window._passagesPromise`，AbortController 15s timeout
- Module 內再等這個 promise；若失敗，`_attemptFetch()` retry，12s/8s timeout，每 2s 重試
- `window._passagesReady`、`window._allPassages`、`window._getPassage()` 都在 window scope
- 若 passages 未 ready，GO 後顯示空白，2s 後顯示 `LOADING…`，每 100ms poll 直到 ready

---

## theme-color（網址列）

- 預設：`#272a26`（深灰，HTML meta 固定）
- 打字中（`resetGame`）：`setThemeColor('#5e8f58')`（主題綠）
- 結束 / 回首頁：`setThemeColor('#272a26')`
- `setThemeColor()` 定義在非 module `<script>` 裡（所以全域可用）

---

## Footer 設計規範（四個頁面統一）

```css
footer {
  padding: .6rem 1.2rem max(.9rem, env(safe-area-inset-bottom));
  display: flex; align-items: center; justify-content: center;
  gap: .1rem; flex-wrap: wrap;
  border-top: 1px solid var(--border);
}
footer a {
  font-size: .8rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase;
  color: var(--muted); text-decoration: none;
  padding: .6rem .45rem;
}
```
- 分隔符 `.sep` / `.footer-sep`：`color:var(--border); font-size:.8rem`
- `:hover` 包在 `@media(hover:hover)`
- `justify-content:center`（水平置中）

---

## manifest.json 重點

- `icons` 陣列：每個尺寸要有 `"purpose":"any"` 和 `"purpose":"maskable"` 各一條（共 4 條）
- 目前只有 `icon-512.png`，用同一個檔案服務 192x192 和 512x512 兩個尺寸
- **不要**只有 `maskable`（會導致通知出現兩個圖示）
- **不要**只有 SVG（通知系統不支援）

---

## 已知待處理事項

1. **PWA standalone 首頁間距**：目前 `@media(display-mode:standalone)` 調整了 spacer flex 比例，但實際值（`flex:1.6`/`flex:3.2`）未經 PWA 實機驗證，需 owner 測試後微調
2. **成績頁「廣告到 PLAY AGAIN」底部對齊首頁 GO**：用 `#result-spacer { flex:1 }` 實作，實機可能需微調

---

## 注意事項

- Owner 匿名，**不**在程式碼或 commit 中出現個人資訊
- **禁用 px**（RWD 原則），一律 rem/em/%/dvh
- 修改前先確認問題根源，優先參考舊版本正確寫法，不疊床架屋
- 每次輸出前先問 `TZ='Asia/Taipei' date` 取時間戳
- 不需要把 manifest.json 內容完整貼出，浪費 token
- 交接文件只輸出 .md，不要同時輸出其他檔案
