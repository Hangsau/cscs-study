---
title: "學習方法論（基於 A Mind for Numbers）"
date: 2026-06-25
description: "間隔重複 / 提取練習 / 變式練習 — 套用到 CSCS 24 章"
---

# CSCS 學習方法論

> 書源：`/home/hangsau/books/大腦喜歡這樣學/`（A Mind for Numbers 中譯）+ `大腦喜歡這樣學・強效教學版/`
>
> 核心精神：**大腦不是裝滿東西的容器，是會改變的肌肉。**

---

## 0. 出處與學術基礎（為什麼這套方法有效）

這套方法論不是隨意湊的，**兩層依據**：

### 層 1：A Mind for Numbers 原文

Barbara Oakley 著（2014），中譯「大腦喜歡這樣學」，結構：

| PART | 章節 | 主題 | 對應到我們 SOP |
|------|------|------|--------------|
| P1 | 1-4 | 大腦學習機制、能力的錯覺 | §8 反模式（不要 highlight）|
| P3 | 10-11 | 增強記憶力（組塊 + 間隔）| §1 間隔重複 |
| P4 | 12 | 提取練習（free recall）| §2 提取練習（主推 free recall）|
| P4 | 13-15 | 學得更深入（teach back / 變式）| §2 teach back + §3 變式練習 |
| P5 | 16-18 | 自信校正 + 應考策略 + 好壞讀書法 | §6 自信校正 + §7 考前衝刺 |

### 層 2：書中引用的學術研究

- **Roediger, H. L., & Karpicke, J. D. (2006)**「Test-Enhanced Learning」*Psychological Science* — 讀一遍+提取 vs 讀兩遍，一週後測驗**提取組高 50%**（這是選擇題/自我測驗有效的硬證據）
- **Karpicke, J. D., & Roediger, H. L. (2008)**「The Critical Importance of Retrieval for Learning」*Science* — 多次短提取 > 一次長時段反覆練習
- **Bjork, R. A., & Bjork, E. L. (1992)**「A New Theory of Disuse and an Old Theory of Stress」— **Desirable Difficulties** 理論：學習時越難提取 = 記得越久（難度是 feature 不是 bug）
- **Ebbinghaus (1885)** 遺忘曲線 — 沒複習 1 天後忘 50-70%，但**間隔重複後遺忘大幅減緩**

### 我 SOP 簡化了什麼

書強調**多模式組合**（free recall + practice test + teach back + variation）。TG bot 環境下我簡化成「讀→出選擇題→記錄」主流程。**簡化的代價**：少了 free recall（書裡說**最關鍵**）和 teach back 的實作。

**修正**（見 §2）：free recall 從「隔天複習」拉回「**讀完當下立即**」，才是書原文意思。

---

## 1. 間隔重複（Spaced Repetition）— PART 3 第 10-11 章

**核心**：不要在一天內連續重複同一個 topic，要分散到不同天。遺忘曲線在間隔後反彈最強。

### 套用到 CSCS

每個 topic 設 6 個複習節點：

| 複習次序 | 時機 | 動作 | 為什麼這個時機 |
|---------|------|------|--------------|
| **T+0 讀完當下** | **立刻** | **free recall**（不看書用自己的話講）| Ebbinghaus 遺忘曲線最陡，馬上提取最關鍵 |
| 第一次複習 | **1 天後** | practice test（Talos 出選擇題）| 24h 後遺忘 60%，測驗強化記憶 |
| 第二次複習 | **3 天後** | free recall + 寫錯題 notes | 第 2 個遺忘谷，鞏固弱點 |
| 第三次複習 | **7 天後** | teach back（講給 Talos 聽）| 確認能教別人 = 真的會了 |
| 第四次複習 | **14 天後** | 變式練習（換情境套用）| 跨情境 transfer |
| 第五次複習 | **30 天後** | 跨章節應用（ch17 套用 ch03 等）| 長期 retention 鞏固 |

`data/topics.yaml` 的 `next_review` 欄位會自動推進。

---

## 2. 提取練習（Retrieval Practice）— PART 4 第 12-15 章

**核心**：不要 highlight、不要重讀。要**強迫自己回想**。錯誤是學習最有效的訊號。

### 四種提取練習（依效果排序 — 書原文推薦順序）

**書原文（P4 第 12 章「Recite」一節）**：先 Recite（free recall），不行才看書，再來才做練習題。所以排序是 free recall > practice test > teach back > variation。

| 排序 | 方法 | 書中權重 | TG 環境適合度 | 何時用 |
|------|------|---------|------------|-------|
| **1** | **Free Recall**（自由回想）| ★★★★★ **最關鍵** | ⚠️ 需 voice 或打字（但最有效）| **讀完當下立刻** |
| **2** | **Practice Test**（模擬測驗）| ★★★★ | ✅ 短題短答友善 | 1 天後 / 對 free recall 沒把握時 |
| **3** | **Teach Back**（教別人）| ★★★★ | ⚠️ 適合 voice message | 7 天後 / 確認「真的會了」|
| **4** | **Variation**（換情境）| ★★★ | ✅ 寫應用題模板 | 14 天後 / 跨章節整合 |

#### 1️⃣ Free Recall（**最關鍵** — 書說這是「recite」的核心）

- 讀完一個 section 後**立刻閉眼**用 30 秒用自己的話講剛學的
- 卡住的地方 = 真正沒懂的地方
- **TG 環境下**：用 voice message（最自然）或打字重點
- **不在 SOP 主流程是因為**：Talos 出選擇題更好自動化。但**這是書裡說最有效的**，TG 也應該用

#### 2️⃣ Practice Test（最容易在 TG 執行）

- 讓 Talos 出 5-10 題選擇題（4 選 1）
- 做完**不要看答案前先自己講為什麼選這個**
- Talos 自動判斷對錯 → 4/5 對標 mastered，2-3 對標 learning，0-1 對留 todo + 寫錯題

#### 3️⃣ Teach Back（確認真懂）

- 用 3 分鐘把 topic 解釋給 Talos 聽（voice 或打字）
- Talos 聽完告訴你哪裡講錯、哪裡缺漏
- 「能教別人」= 真會（書 P4 第 15 章）

#### 4️⃣ Variation（換情境套用）

- 換章節套用：ch17 阻力訓練的 SET 原則能不能套用到 ch20 有氧？
- 換情境：同概念套到不同族群（青少年 / 女性 / 老年 — ch07）
- 換表徵：文字 ↔ 表格 ↔ 圖 ↔ 口述

### 反模式 ❌

- ❌ **不要 highlight 滿書**：highlight 製造「我以為我會了」的錯覺（A Mind for Numbers 第 4 章「能力的錯覺」）
- ❌ **不要重新讀同一段**：重新讀比 recall 慢、效果差
- ❌ **不要看到答案才想**：先想完再看
- ❌ **不要死背**沒理解的東西：理解後的記憶比死背強 5-10 倍
- ❌ **不要只用 practice test 跳過 free recall**：書原文強調 free recall 才是最關鍵的

---

## 3. 變式練習（Variation）— PART 5 第 17 章

**核心**：換個角度問同一概念。比反覆練習同一題型更有效。

### 三種變式

1. **換章節套用**：ch17 阻力訓練的 SET 原則，能不能套用到 ch20 有氧？
2. **換情境**：同概念套到不同族群（青少年 / 女性 / 老年 — ch07）
3. **換表徵**：文字 ↔ 表格 ↔ 圖 ↔ 口述

---

## 4. 心智模型 / 組塊（Chunks）— PART 3 第 7 章

**核心**：把零散資訊壓縮成有意義的「組塊」，才能放進長期記憶。

### CSCS 必組塊

| 概念 | 組塊內容 |
|------|---------|
| 三大能量系統時間表 | ATP-PC 0-10s / 糖酵解 10s-2min / 有氧 2min+ |
| 1RM 百分比 | 100/95/90/85/80/75/70% = 1/2/4/6/8/10/12 RM |
| 肌纖維類型 | Type I（慢縮紅肌，耐力） / Type IIa（快縮紅白介面） / Type IIx（快縮白肌，爆發） |
| 三大訓練原則 | 專項化 / 漸進式超負荷 / 變式 |
| SET 原則 | Set / Exercise order（multi-joint 先） / Tempo / Loading（1RM %） |
| 週期化三類型 | 線性（傳統） / 波動（每週變） / 塊狀（4-8 週聚焦單一能力） |

每個組塊要能**脫口而出**才算內化。

---

## 5. 番茄 + 專注模式（Focused Mode）— PART 1 第 2 章

**核心**：專注模式（focuse）和發散模式（diffuse）交替使用。25 分鐘專注 + 5 分鐘散步 = 最佳學習節奏。

### 每日節奏

- 09:00 - 09:25 **專注模式**：讀一段 + free recall
- 09:25 - 09:30 **發散模式**：散步 / 喝水 / 看窗外
- 09:30 - 09:55 **專注模式**：換個角度（Talos 出題）
- 09:55 - 10:00 **發散模式**
- 10:00 - 10:25 **專注模式**：寫筆記（自己的話）
- 10:25 - 10:30 **發散模式**

每日 3 個循環 = 約 90 分鐘，讀 2-3 個 section。

---

## 6. 自信校正（Confidence Calibration）— PART 5 第 16 章

**核心**：人對「自己會了」跟「實際會了」嚴重脫節。

### 校正方法

1. **每次複習前**：先預測「我覺得我會幾題」
2. **做完測驗後**：對照實際
3. **差距大 = 要多 recall**（而不是再讀一遍）

寫到 `content/notes/YYYY-MM-DD-calibration.md` 追蹤。

---

## 7. 考前衝刺（P5 第 17 章「應考策略」）

- **考前 1 週**：只做 practice test，不讀新東西
- **考前 1 天**：完全休息，不碰書
- **考試當天**：早睡飽、咖啡因中等、別改作息
- **考試策略**：先跳過不會的（標記），全部做完再回頭
- **猜題策略**：完全不會的也要選（不留白）

---

## 8. 反模式清單（明確禁止）

1. ❌ 一次讀完一整章不中斷
2. ❌ Highlight 重點 → 覺得會了 → 跳過 recall
3. ❌ 連續 3 天複習同一個 topic（浪費 spaced repetition）
4. ❌ 看答案才知道自己錯哪（沒訓練 self-correction）
5. ❌ 把筆記寫得跟書一樣（沒有自己消化）

---

## 9. 配套工具

- **Talos (TG bot)**：出選擇題、聽你講解、糾正錯誤
- **本網站**：追蹤 `mastery_status`、`next_review`、累計 `review_count`
- **NSCA 書 `by_book/`**：原始內容 source of truth
- **`content/notes/`**：時間序列個人筆記
