# 網頁排版 RWD 開發指引
> 適用於手機優先（Mobile First）的網頁專案，傳給 AI 協作開發時作為參考規範。

---

## 1. Viewport Meta 標籤

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

沒有這行，手機瀏覽器會以桌機寬度（約 980px）渲染，字體縮得極小。

---

## 2. 單位選用原則

| 用途 | 推薦單位 | 避免 |
|------|----------|------|
| 字體大小 | `rem` | `px`（固定，不隨系統設定縮放） |
| 間距（padding, margin, gap） | `rem` | `px` |
| 容器寬度 | `%`、`rem`（max-width）| 固定 `px` 寬度 |
| 容器高度 | `min-height`、讓內容撐開 | 固定 `height`（會導致內容溢出） |
| 視窗高度 | `dvh`（dynamic viewport height） | `vh`（手機上包含瀏覽器 UI，會被遮住） |
| 響應式字體 | `clamp(min, 偏好值, max)` | 固定 rem（無法彈性縮放） |
| Breakpoints | `rem`（如 `37.5rem` = 600px） | `px` |

**特別注意：**
- `input` 的 `font-size` 必須 ≥ `16px`，否則 iOS 會自動觸發頁面縮放。
- Canvas 繪圖 API 只接受 `px`，是唯一可接受的例外。

---

## 3. 佈局系統

### 優先使用 Flexbox 和 Grid，不用 float

**Flexbox（一維）：** 導覽列、按鈕列、header 等橫向排列。

```css
.header {
  display: flex;
  align-items: center;
  gap: .5rem;
}
```

**防止擠壓的標準寫法：**
- 可縮的元素（標題、logo）：`flex: 1; min-width: 0;`
- 不可縮的元素（按鈕）：`flex-shrink: 0; white-space: nowrap;`
- 空間不足時自動換行：`flex-wrap: wrap;`

**Grid（二維）：** 複雜的頁面大框架，或需要對齊的格狀排列。

---

## 4. 避免 Hard-coded 高度

```css
/* ❌ 錯誤：內容換行時會溢出容器 */
.box { height: 200px; }

/* ✅ 正確：讓內容撐開，確保最小高度 */
.box { min-height: 10rem; }
```

唯一例外：打字遊戲的文字顯示區等「刻意固定顯示行數」的情境。

---

## 5. Mobile First 媒體查詢

先寫手機版樣式，再用 `min-width` 疊加大螢幕樣式：

```css
/* 手機版（預設） */
.title { font-size: 1.2rem; }

/* 平板 / 桌機（≥ 600px = 37.5rem） */
@media (min-width: 37.5rem) {
  .title { font-size: 1.6rem; }
}
```

Breakpoint 也用 `rem`，不用 `px`，與整體單位一致。

---

## 6. 手機安全區域（Safe Area）

iPhone Home Bar、Android 手勢列會遮住底部內容。底部固定元素（footer、cookie banner 等）必須加：

```css
.footer {
  padding-bottom: max(0.7rem, env(safe-area-inset-bottom));
}
```

頁面本身也建議：

```css
body {
  min-height: 100dvh; /* 不是 100vh */
}
```

---

## 7. 觸控目標大小

手機上的可點擊元素（按鈕、連結）需符合：
- **最小點擊區域：44 × 44px**（約 2.75rem × 2.75rem）
- 元素本身字體可以小，但要用 `padding` 撐大點擊區域
- 物件之間保留足夠間距，避免誤觸

```css
/* 字體小但點擊區域夠大的 footer 連結範例 */
.footer a {
  font-size: .75rem;
  padding: .75rem .5rem; /* 撐大點擊區域 */
}
```

---

## 8. 圖片與媒體

全域加入，防止圖片超出容器：

```css
img, video {
  max-width: 100%;
  height: auto;
}
```

Canvas 不需要，因為通常是 hidden 或有獨立邏輯控制尺寸。

---

## 9. 防止橫向溢出

```css
html {
  overscroll-behavior-x: none;
  overflow-x: hidden;
}
body {
  overflow-x: hidden;
}
```

---

## 10. 彈性字體（三個物件同一行時）

同一行有「標題 + 按鈕群」時，標題字體應隨可用空間縮放：

```css
/* 方法一：container query（最精準，字體相對於容器寬度）*/
.header {
  container-type: inline-size;
}
.header-title {
  font-size: max(1rem, 6cqi); /* 最小 1rem，隨容器放大 */
}

/* 方法二：clamp（簡單，字體相對於 viewport）*/
.header-title {
  font-size: clamp(1rem, 4vw, 1.6rem);
}
```

注意：`cqi` 是相對於**容器**寬度，`vw` 是相對於**視窗**寬度。`file://` 本機開啟時 `vw` 計算可能與部署後不同，建議用 `cqi` 或 `max(固定值, cqi)`。

---

## 11. 測試建議

- 用瀏覽器 DevTools 的裝置模擬器，測試 320px、375px、390px、430px、768px 等常見寬度
- 特別注意「斷點邊緣」的尺寸，確保排版過渡平滑
- 在真實手機上測試，確認 safe area、觸控目標、Chrome UI 遮擋等問題
- `file://` 本機開啟與實際部署後，部分 CSS 單位行為可能不同，以部署版為準

---

## 快速 Checklist

開始開發或 review 時，逐項確認：

- [ ] `<meta name="viewport">` 已設定
- [ ] 容器寬度用 `%` 或 `max-width: Xrem`，不用固定 `px`
- [ ] 字體、間距全用 `rem`
- [ ] 頁面高度用 `100dvh`，不用 `100vh`
- [ ] 底部固定元素加 `env(safe-area-inset-bottom)`
- [ ] 按鈕 / 連結點擊區域 ≥ 44px
- [ ] 同一行多物件：可縮元素有 `flex:1; min-width:0`，不可縮元素有 `flex-shrink:0`
- [ ] 沒有 hard-coded `height`（除非有明確理由）
- [ ] `img` 加了 `max-width:100%; height:auto`
- [ ] Media query 用 `min-width`（Mobile First），breakpoint 用 `rem`
