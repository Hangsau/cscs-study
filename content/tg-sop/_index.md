---
title: "TG Talos SOP"
description: "透過 @HangTalos_Bot 跟 Claude Code 對話複習 CSCS"
date: 2026-06-25
---

# TG Talos SOP

> **前提**：claude-tg-bot（`~/projects/claude-tg-bot/`）24/7 跑著，bot username 是 `@HangTalos_Bot`。手機打開 TG 傳訊息，Claude Code 會在 VM 上執行並回。
>
> **CSCS 複習對 Claude 來說 = 讀 `~/cscs-study/` 下的書 + 寫/更新 yaml + 寫筆記。** 直接用自然語言說要做什麼就行，Claude 會自己 grep 書、寫 markdown、改 yaml。

---

## 快速指令模板

複製貼上，改成你要的內容。

### 1. 讀 + 寫筆記（開始新 topic）

```
我要開始讀 NSCA ch07（Age- and Sex-Related Differences）。

請幫我：
1. 讀 ~/cscs-study/by_book/doc_df238de65892_ch07_*.md
2. 用我的話寫一篇個人學習筆記存到 ~/cscs-study/content/notes/2026-MM-DD-ch07-first-read.md
3. 寫一篇 ch07 topic-card 到 ~/cscs-study/content/mastered/ch07-sex-related-differences.md
   （先放 learning 狀態，等我確認）
4. 更新 ~/cscs-study/data/topics.yaml 把 ch07 的 mastery_status 改成 learning
```

### 2. 讓 Talos 出選擇題（free recall 強化）

```
我要練習 ch03（Bioenergetics）。

請出 10 題選擇題（4 選 1），考 ATP-PC / 糖酵解 / 有氧三大能量系統時間表。
每題先給題幹，等我答完再給答案跟詳解。
```

### 3. 標記 topic 為 mastered

```
我覺得 ch03 我已經熟了，請把 ~/cscs-study/data/topics.yaml
ch03 的 mastery_status 改成 mastered，review_count +1。
```

### 4. 查今天該複習什麼

```
請看 ~/cscs-study/data/topics.yaml，列出所有 next_review <= 今天的 topic。
每個 topic 給我 3 題關鍵問題測試我自己。
```

### 5. 講解 + 被糾正（teach back）

```
我要用 teach back 練習 ch17。

我會用 3 分鐘講阻力訓練計畫設計的 SET 原則。
講完你告訴我哪裡講錯、哪裡缺漏、用 Talos 簡短語氣回我。
```

### 6. 寫錯題筆記

```
我剛做完 ch11 的題目，錯了這題：

題目：[題幹]
我答：[我的答案]
正解：[正解]

請把這個錯題寫到 ~/cscs-study/content/notes/2026-MM-DD-mistake-ch11.md，
包含：題目、我的答案、正解、為什麼錯（你幫我分析）、這個 topic 我還沒掌握的概念。
```

### 7. 跨章節應用題

```
請出 3 題變式應用題，套用以下：
- ch07（年齡性別差異）
- ch14（熱身柔軟度）
- ch17（阻力訓練計畫設計）

情境：60 歲女性、有骨質疏鬆、初學者。
```

### 8. 模擬考前一天回顧

```
幫我做考前快速回顧：
1. 列出 24 個 topic 裡 mastery_status 還不是 mastered 的
2. 對每個不是 mastered 的 topic，給我 1 句最關鍵的核心概念要記住
3. 列成口訣格式方便考前最後掃一眼
```

---

## 建議對話節奏

| 時段 | 動作 | 用哪個 prompt |
|------|------|--------------|
| 早上 | 開新 topic | (1) |
| 下午 | 練習提取 | (2) 或 (7) |
| 晚上 | 標記進度 + 寫錯題 | (3) + (6) |
| 週末 | 跨章節 + 講解 | (5) + (4) |
| 考前 | 快速回顧 | (8) |

---

## 注意事項

1. **claude-tg-bot 不會自動 commit**：所有改檔要 user 自己 `git add . && git commit`
2. **claude-tg-bot 不會自動跑 hugo server**：但會 build static。若 user 用 `hugo server -D` 跑著，瀏覽器會自動 reload
3. **claude-tg-bot 走 bypassPermissions**：可以直接寫檔（小心 token / secrets）
4. **每次對話建議明確指定檔案路徑**：避免 Claude 寫到別處

---

## 如果要進階：寫 slash command

目前 `@HangTalos_Bot` 沒設 slash command。要加可以：

1. 在 `~/projects/claude-tg-bot/` 加 `commands/cscs.py`
2. 註冊 `/cscs quiz` `/cscs review` `/cscs note` 等
3. 對應到上面的 prompt 模板

**為什麼先不寫**：自然語言 prompt 已能涵蓋 90% 情境，加 slash command 增加 bot 維護成本。等真的每天用、發現重複輸入的 prompt 多再寫。
