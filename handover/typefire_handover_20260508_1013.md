# TYPEFIRE — 交接文件
**時間戳：20260507_0904**

---

## 專案概述

TYPEFIRE 是一個純前端打字速度測試 PWA，託管在 GitHub Pages（`typefire-game.github.io`）。無後端，Firebase Realtime Database 作為 leaderboard 資料存取。使用者匿名，owner 不希望個人資訊出現在任何公開頁面。

---

## 檔案結構

```
index.html          — 主頁面（首頁 + 遊戲 + 成績）
leaderboard.html    — Leaderboard 獨立頁面
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
例：`index_20260507_0904.html`
每次出檔前都要重新取時間戳，不可沿用舊的。

### 最新輸出檔案
- `index_20260507_0846.html` — 目前最新版（有未解決問題，見下）
- `leaderboard_20260503_1351.html`
- `about_20260503_1351.html`
- `privacy_20260503_1351.html`
- `manifest_20260503_1927.json`

---

## 技術架構

### CSS 設計原則
- **RWD 優先**：完全禁用 `px` 單位（除非框架強制），一律用 `rem`、`em`、`%`、`dvh`、`dvw`、`clamp()`
- `dvh` 必須加 `vh` fallback：`min-height:100vh; min-height:100dvh;`
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
--accent-cta:#72b06b
--wrong:     #b09050
--wrong-bg:  #38342e
--correct:   #dae5d8
--font:      'Inter', sans-serif
--word-size: 1.5rem
--word-lh:   2.6
--header-h:  3.25rem
```

### 防止文字選取 / 反白規則
- 全域：`body, button, a, div, span, p, header, footer { user-select:none; -webkit-user-select:none; }`
- 全域：`-webkit-tap-highlight-color:transparent`（在 `*` selector 上）
- 所有 `:hover` 規則必須包在 `@media(hover:hover){}` 裡
- 所有互動元件都要有 `:focus, :focus-visible { outline:none; 還原原始顏色 }`
- JS `touchend` 監聽：300ms 後 `blur()` 被點到的 button/a

### 捲動鎖定策略
- **CSS 層**：`html/body` **不**加 `overflow:hidden`
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
| Leaderboard overlay | `#lb-overlay` | 遊戲中右上角 LEADERBOARD（仍保留） |
| Mode picker | `#mode-picker` | 部分流程觸發 |

### 首頁 flex 間距（start-screen）
- 兩個 spacer div：`style="flex:1"` 和 `style="flex:2"`
- PWA standalone 用 `@media(display-mode:standalone)` 微調 flex 比例
- `#start-screen` padding：`0 1.5rem 0`
- 廣告和 footer 用 `width:calc(100% + 3rem); margin:0 -1.5rem` 撐到左右邊緣

### 成績頁結構（目前版本）
```
#result-screen (position:fixed; top:0; left:0; right:0; height:100dvh; overflow:hidden)
  ├── header（sticky, z-index:1）
  │   ├── .top-ad（廣告）
  │   └── .logo（TYPEFIRE 連結，height:var(--header-h)）
  └── #result-scroll（flex:1; display:flex flex-direction:column; justify-content:center; gap:.55rem）
      ├── #result-top-area（display:contents）
      │   ├── #result-spacer（display:none）
      │   ├── .result-label（YOUR SPEED）
      │   ├── .result-wpm（大數字）
      │   ├── .result-sub（words per minute）
      │   ├── .rank-badge（條件顯示）
      │   └── .result-grid（4格統計）
      ├── #result-mid-spacer（display:none）
      ├── #result-bottom（display:contents）
      │   ├── .nickname-row（input）
      │   ├── .result-btns（🏆 LEADERBOARD + SHARE）
      │   └── .again-btn（PLAY AGAIN）
      └── .site-footer（margin:auto -1.5rem 0）
```

---

## Header 結構（所有頁面統一）

```html
<header>
  <div class="top-ad">Advertisement</div>
  <div class="header-main">
    <!-- logo、按鈕等 -->
  </div>
</header>
```

```css
header {
  display: flex; flex-direction: column;
  flex-shrink: 0; border-bottom: 1px solid var(--border);
  width: 100%; align-self: stretch;
}
.top-ad {
  width: 100%; min-height: 3.125rem; box-sizing: border-box;
  display: flex; align-items: center; justify-content: center;
  border-bottom: 1px solid var(--border);
  font-size: .7rem; font-weight: 600; letter-spacing: .12em;
  text-transform: uppercase; color: var(--border); background: var(--bg);
  flex-shrink: 0;
}
.header-main {
  height: var(--header-h); padding: 0 1.2rem;
  display: flex; align-items: center; justify-content: space-between; gap: .5rem;
  box-sizing: border-box;
}
```

**重要**：寬版 `@media(min-width:37.5rem)` 中，side padding 要設在 `.top-ad` 和 `.header-main` 上，**不可**設在 `header` 本身，否則 `border-bottom` 會縮短，造成上下橫線長度不一致。

---

## Footer 設計規範（四個頁面統一）

```css
.site-footer / footer {
  padding: .3rem 1.5rem max(.7rem, env(safe-area-inset-bottom));
  display: flex; align-items: center; justify-content: center;
  gap: .1rem; flex-wrap: wrap;
  border-top: 1px solid var(--border);
}
footer a {
  font-size: .8rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase;
  color: var(--muted); text-decoration: none;
  padding: .6rem .45rem;  /* 上下對稱，這是置中的關鍵 */
}
```
- **高度以首頁為準**：`max(.7rem, env(safe-area-inset-bottom))`
- **垂直置中做法以 about 頁為準**：link `padding:.6rem .45rem` 上下對稱
- about / privacy / leaderboard：`position:sticky; bottom:0`
- index 首頁：`margin-top:auto`

---

## 打字頁間距規則

- `stats-row`（WPM/ACC/ERRORS）：`padding:.7rem 1.2rem .7rem`（上下對稱）
- 綠色 progress bar：`padding:0 1.2rem .4rem`
- words-wrap：`padding:1.2rem 1.2rem .7rem`（**不可更改**，這是綠線到題目的距離）

---

## Leaderboard

### 重要規則
- **獨立頁面** `leaderboard.html`，支援 `?t=15/30/60` URL 參數
- 首頁 LEADERBOARD 按鈕改為 `<a href="leaderboard.html?t=...">` (`.start-lb-btn`)
- 成績頁 LEADERBOARD 按鈕：先呼叫 `submitOnLeave()`，再 `location.href='leaderboard.html?t=...'`
- 遊戲畫面右上角 LEADERBOARD overlay（`#lb-overlay`）仍保留
- `.lb-tabs` 的 `position:sticky` top：`calc(3.125rem + var(--header-h))`

### PLAY 按鈕預設模式
`openPicker()` 呼叫時，`pickerTime` 要設為 `currentTime`（當前瀏覽的 tab），並同步更新按鈕 active 狀態。

### 資料庫路徑
```
scores/15/   scores/30/   scores/60/
```
每筆資料：`{ name, wpm, acc, ts }`
只儲存前 100 筆。

### checkRank 邏輯
- 遊戲結束後立即呼叫一次
- 排名 ≤ 10 才顯示 badge
- popstate `nav==='result'` 分支：**只有 `lastResult.wpm > 0` 才顯示成績頁**，否則 `showHome()`

---

## Firebase

```js
apiKey: "AIzaSyClQ0SV1vuQiy_2Ji3_1YpnYJcmmt_WXlQ"
databaseURL: "https://typefire-e5c68-default-rtdb.asia-southeast1.firebasedatabase.app"
projectId: "typefire-e5c68"
appId: "1:1065566297610:web:c109b00d44a8cbb3fec9f3"
```

---

## manifest.json

已加入 `"orientation": "portrait"` 限制 PWA 安裝後僅顯示直向。瀏覽器中無法強制。

---

## Share 按鈕行為

- 行動裝置：`navigator.share({ files:[imageFile] })` 原生分享
- 電腦（非行動裝置，用 `navigator.maxTouchPoints > 0` 判斷）：直接下載圖片

---

## Passages 載入

- 頁面頂部先 fetch `passages.json`，存入 `window._passagesPromise`
- Module 內再等這個 promise；若失敗則 retry
- `window._passagesReady`、`window._allPassages`、`window._getPassage()` 都在 window scope

---

## theme-color（網址列）

- 預設：`#272a26`
- 打字中：`setThemeColor('#5e8f58')`
- 結束 / 回首頁：`setThemeColor('#272a26')`

---

## 已確認解決的問題（本輪）

1. **`--header-h` 未定義**：加入 `:root { --header-h: 3.25rem }`，修正打字頁 header 壓扁、成績頁 logo 不置中
2. **stats-row 間距**：`padding:.45rem → .7rem`（上下對稱加大）
3. **成績頁分群拆除**：移除 `#result-top-area`/`#result-bottom` 的不合理群組，改為單一 flex column（`#result-scroll`），`display:contents` 保留 HTML 相容性
4. **footer 垂直置中**：所有頁面 link `padding:.6rem .45rem`（以 about 頁為準），container padding 上下對稱，safe-area 單獨處理
5. **footer 高度統一**：各頁面 `max(.7rem, env(...))` 統一
6. **寬版橫線長度不一致**：`@media(min-width:37.5rem)` 中 side padding 從 `header` 移到 `.top-ad`/`.header-main`，修正所有頁面
7. **popstate 顯示空白成績**：`nav==='result'` 分支加 `lastResult.wpm > 0` 判斷
8. **leaderboard PLAY 預設模式**：`openPicker()` 改為 `pickerTime = currentTime`
9. **成績頁不可 scroll**：`#result-screen { overflow:hidden }`
10. **成績頁 rank-badge 推擠**：`display:contents` 讓所有物件在同一 flex column，rank-badge 自然佔位

---

## 未解決問題（需繼續處理）

### 1. 成績頁 YOUR SPEED 上方空間太大
**現象**：YOUR SPEED 上方的空間，明顯大於其他物件之間的 gap（`.55rem`）。要求：「header 下緣到 YOUR SPEED 上緣」= 「words per minute 下緣到 accuracy 那排上緣（有 rank-badge 時改為 rank-badge 上緣）」。

**嘗試過的方向**：
- `padding-top:.55rem / .45rem / .65rem` — 都不正確
- `justify-content:flex-end` + `padding-top` — 因 `flex-end` 計算邏輯複雜且不穩定
- `#result-spacer { flex:1 }` 作為第一個子元素 — 有效果但 spacer 在特定條件下行為不符
- `justify-content:center` + `flex:1` on `#result-scroll` — 目前版本，但 YOUR SPEED 上方空間仍偏大

**目前狀態**：`#result-scroll { flex:1; justify-content:center; gap:.55rem }`，footer 用 `margin:auto -1.5rem 0`。

**建議方向**：重新確認 `#result-scroll` 高度是否確實等於 header 以下的空間；若 `justify-content:center` 仍有偏差，考慮改用固定 `padding-top` 讓 YOUR SPEED 緊跟在 header 下方 `.55rem` 處，其餘空間留在底部（靠 `margin-top:auto` on footer 消化）。

### 2. 成績頁 nickname focus 時的鍵盤處理
**需求**：
- focus nickname 時，所有物件一起往上平移
- footer 上方橫線對齊瀏覽器底部工具列上緣（typefire-game.github.io 綠色橫條上緣）
- 鍵盤出現/消失動畫要跟原生動畫同步，不要跳動

**目前做法**：
```js
// visualViewport resize 時，對 #result-scroll 套用 transform:translateY
if(window.visualViewport){
  function onResultVV(){
    const rs=$('result-screen');
    if(!rs||!rs.classList.contains('show'))return;
    const scroll=document.getElementById('result-scroll');
    const nf=$('nickname-input');
    const vv=window.visualViewport;
    if(document.activeElement!==nf){
      setTimeout(()=>{ if(document.activeElement!==nf) scroll.style.transform=''; }, 300);
      return;
    }
    scroll.style.transform='';
    requestAnimationFrame(()=>{
      const footer=rs.querySelector('.site-footer');
      const footerTop=footer.getBoundingClientRect().top;
      const shift=footerTop-vv.height;
      if(shift<0) scroll.style.transform=`translateY(${-shift}px)`;
    });
  }
  visualViewport.addEventListener('resize',onResultVV);
  visualViewport.addEventListener('scroll',onResultVV);
}
```

**已知問題**：
- footer 未完全對齊綠色橫條上緣（差一點）
- 鍵盤消失時仍有輕微跳動（`setTimeout(300ms)` 不完全同步原生動畫）

**關鍵決定**：
- 移動 `#result-scroll`（不移動 `#result-screen`），避免 `#result-screen` 移動後露出後面的答題頁
- `#result-screen { overflow:hidden }` 阻止 Chrome 在 fixed 容器內的自動捲動
- 用 `document.activeElement === nickname-input` 判斷鍵盤是否因 nickname focus 而出現（不猜測）
- `300ms` delay reset 讓鍵盤消失動畫完成後再清 transform

---

## 注意事項

- Owner 匿名，**不**在程式碼或 commit 中出現個人資訊
- **禁用 px**（RWD 原則），一律 rem/em/%/dvh；動態計算的 px 值（如 `getBoundingClientRect()`）例外
- 修改前先確認問題根源，不疊床架屋
- 每次出檔前重新取時間戳：`TZ='Asia/Taipei' date '+%Y%m%d_%H%M'`
- 不需要把 manifest.json 內容完整貼出，浪費 token
- 交接文件只輸出 .md，不要同時輸出其他檔案
- 回答時不要大量自言自語，只呈現對 owner 有用的內容
- 回答一律使用繁體中文，不可混入日語或其他語言
- 不要急，想清楚再改；有問題先提出討論，取得共識後再動程式碼
