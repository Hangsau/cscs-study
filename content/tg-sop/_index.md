---
title: "TG Talos SOP"
description: "透過 @HangTalos_Bot 跟 Claude Code 對話複習 CSCS"
date: 2026-06-25
last_updated: 2026-06-25
---

# TG Talos SOP

> **核心概念**：**Talos 主動讀 NSCA 書 + 寫個人摘要 + 出題 + 標記狀態 + commit + push**。**User 不需要自己讀書**。你只要跟 Talos 講「我要開始 chXX」，剩下的 Talos 做。
>
> **前提**：`claude-tg-bot`（`~/projects/claude-tg-bot/`）24/7 跑著，bot 是 `@HangTalos_Bot`。手機打開 TG 傳訊息，Claude Code 會在 VM 上跑並回應。
>
> **書本使用範圍**：
> - ✅ Talos 讀 `~/cscs-study/by_book/`（合法電子書，個人學習使用）
> - ✅ Talos 寫個人摘要 / 出題 / 標記（衍生作品，不算侵權）
> - ❌ 不 push `by_book/` 上 GitHub（書本原文不上 public）
> - ❌ 不在網站顯示書本原文（content/notes/ 是 Talos 衍生的個人筆記）

---

## 🚀 自動化工作流（Talos 主動版，**分段問答**）

**核心**：**不要一次餵整章摘要給 user**（違反「能力錯覺」書第 4 章）。改成 Talos 拆成 6-10 sections，**每段寫摘要 + 立刻出 1 題**。

```
步驟 1（user 開頭）
  你：「我要開始 ch03」

步驟 2（Talos 讀書 + 拆 sections）
  Talos 自動：
  - 讀 ~/cscs-study/by_book/doc_*_ch03_*.md 整章
  - 拆成 6-10 個 sections（H2 / H3 標題）
  - 標 ch03 status: learning

步驟 3（分段問答 — 重要）
  Talos 對每個 section：
  a. Talos：「section 1: Energy Systems Overview（5 分鐘讀完）」
     → Talos 寫 1-2 句話摘要
     → Talos：「問題：ATP-PC 系統時間範圍？」

  b. 你：「A」

  c. Talos：「對/錯，本 section 重點是 X」→ 進入下一個 section

  d. 重複直到所有 sections 跑完

步驟 4（章節結束算答對率）
  Talos 跑：
    python3 scripts/cscs-quiz.py ch03 --result A,B,A,D,C --correct A,B,D,A,C

  自動：
  - 寫到 data/quiz_log.yaml（每題對錯歷史）
  - 算 ch03 答對率（假設 3/5 = 60%）
  - 自動標記：
    - ≥ 80% → mastered
    - 50-79% → learning
    - < 50% → 留 todo + 寫錯題 notes

步驟 5（自動 commit + push）
  Talos：「要 commit + push 嗎？」
  你：「好」
  → 站自動 ~60s 更新 → /weak/ 頁面看到弱點清單

步驟 6（1 天後 Talos 提醒）
  ch03 next_review 到了 → Talos 主動通知你
```

**為什麼要分段問答，不是整章一次餵？**

- 書第 12 章原文：**一個 section 一個 section 讀 + 立刻回想**
- Roediger & Karpicke 2006 研究：讀+提取 > 讀（**一週後高 50%**）
- 一次餵整章摘要 → 「覺得會了」其實沒會（書第 4 章「能力的錯覺」）

**Talos 自動判斷「會 / 不會」的依據**：
- ≥ 80% 答對 → 標 `mastered`
- 50-79% → 標 `learning`
- < 50% → 留 `todo` + 寫錯題 notes

---

## 📋 快速指令模板（copy-paste 用）

### 0. 開始新章節（分段問答）⭐ 主推

```
我要開始 ch03（Bioenergetics）。

請幫我：
1. 讀 ~/cscs-study/by_book/doc_61bb054caf00_ch03_*.md 整章
2. 拆成 6-10 個 sections（H2 / H3 標題）
3. 標 ch03 status: learning（跑 cscs-mark.py ch03 learning）
4. 對每個 section：
   - 寫 1-2 句話摘要
   - 立刻出 1 題選擇題考該 section 重點
   - 等我答完 → 給對錯 + 進到下個 section
5. 章節結束算答對率，自動標記（≥80% mastered / 50-79% learning / <50% todo）
6. 寫到 data/quiz_log.yaml（讓 /weak/ 頁面顯示弱點）
```

### 0b. 只讀一段（不拆整章）

```
我已經大概知道 ch03 三大能量系統時間，但磷酸肌酸（PCr）的恢復我還不熟。

請幫我讀 ch03 裡 PCr 恢復的段落，給我 3 題選擇題。
```

### 1. 只寫摘要（不跳到練習 — 不建議）

```
幫我讀 ~/cscs-study/by_book/doc_df238de65892_ch07_*.md
寫摘要到 content/notes/YYYY-MM-DD-ch07-summary.md
（用自己的話，3 段以內）
```

⚠️ **這個 prompt 違背學習法**（一次餵摘要會有「能力錯覺」）。建議改成 0. 分段問答。

### 2. 只出選擇題

```
我剛讀完 ch03 的摘要（~/cscs-study/content/notes/YYYY-MM-DD-ch03-summary.md）。

請出 10 題選擇題（4 選 1）考 ATP-PC / 糖酵解 / 有氧三大能量系統時間表。
每題先給題幹，等我答完再給答案 + 詳解。
```

### 3. 記錄 quiz 對錯 + 自動標記

```
我答完 ch03 的題目了，我的答案依序是：A,B,A,D,C
正確答案是：A,B,D,A,C

請跑：
  python3 /home/hangsau/cscs-study/scripts/cscs-quiz.py ch03 \
    --result A,B,A,D,C --correct A,B,D,A,C
然後 commit + push。
```

### 4. 查今天該複習什麼（spaced repetition）

```
請跑：
  grep -E "next_review: $(date +%Y-%m-%d)" ~/cscs-study/data/topics.yaml
列出今天到期的 topic，每個給我 3 題關鍵問題。
```

### 5. teach back（7 天後用）

```
我要用 teach back 練習 ch17（我上次 mastery 是 7 天前）。

我會用 3 分鐘講阻力訓練計畫設計的 SET 原則。
講完你告訴我哪裡講錯、哪裡缺漏。
```

### 6. 寫錯題筆記

```
我剛做完 ch11 的題目，錯了這題：

題目：[題幹]
我答：[我的答案]
正解：[正解]

請寫到 content/notes/YYYY-MM-DD-mistake-ch11.md。
```

### 7. 跨章節應用題（14 天後用）

```
請出 3 題變式應用題，套用：
- ch07（年齡性別差異）
- ch14（熱身柔軟度）
- ch17（阻力訓練計畫設計）

情境：60 歲女性、有骨質疏鬆、初學者。
```

### 8. 模擬考前一天回顧

```
幫我做考前快速回顧：
1. 跑 cscs-mark.py --dry-run 看哪些不是 mastered
2. 對每個不是 mastered 的 topic，給我 1 句最關鍵的核心概念要記住
3. 列成口訣格式
```

---

### 4. 查今天該複習什麼（spaced repetition）

```
請跑：
  grep -E "next_review: $(date +%Y-%m-%d)" ~/cscs-study/data/topics.yaml
列出今天到期的 topic，每個給我 3 題關鍵問題。
```

### 5. teach back（7 天後用）

```
我要用 teach back 練習 ch17（我上次 mastery 是 7 天前）。

我會用 3 分鐘講阻力訓練計畫設計的 SET 原則。
講完你告訴我哪裡講錯、哪裡缺漏。
```

### 6. 寫錯題筆記

```
我剛做完 ch11 的題目，錯了這題：

題目：[題幹]
我答：[我的答案]
正解：[正解]

請寫到 content/notes/YYYY-MM-DD-mistake-ch11.md。
```

### 7. 跨章節應用題（14 天後用）

```
請出 3 題變式應用題，套用：
- ch07（年齡性別差異）
- ch14（熱身柔軟度）
- ch17（阻力訓練計畫設計）

情境：60 歲女性、有骨質疏鬆、初學者。
```

### 8. 模擬考前一天回顧

```
幫我做考前快速回顧：
1. 跑 cscs-mark.py --dry-run 看哪些不是 mastered
2. 對每個不是 mastered 的 topic，給我 1 句最關鍵的核心概念要記住
3. 列成口訣格式
```

---

## 🛠️ helper script：`scripts/cscs-mark.py`

```bash
python3 scripts/cscs-mark.py ch03 mastered   # 標 mastered
python3 scripts/cscs-mark.py ch07 learning  # 標 learning
python3 scripts/cscs-mark.py ch15 review    # 只 +review_count
python3 scripts/cscs-mark.py --dry-run ch03 mastered  # 預覽
python3 scripts/cscs-mark.py ch03 todo      # 改回 todo
```

**spaced repetition 節奏**：review 1→+1天 / 2→+3天 / 3→+7天 / 4→+14天 / 5+→+30天

---

## 對話節奏建議

| 時段 | 動作 | 用哪個 prompt |
|------|------|--------------|
| 早上 | 開新 topic（Talos 讀書 + 摘要 + 練習）| (0) |
| 下午 | 出題練習 | (2) |
| 晚上 | 標記進度 + commit + push | (3) |
| 7 天後 | teach back | (5) |
| 14 天後 | 跨章節應用 | (7) |
| 30 天後 | 模擬考 | (8) |

---

## 注意事項

1. **Talos 預設不會自動 commit / push**（除非你明確說要）— 保守行為
2. **Talos 走 bypassPermissions**：可以直接寫檔（小心 token / secrets）
3. **每次對話建議明確指定檔案路徑**：避免 Talos 寫到別處
4. **站 deploy 是 GitHub Actions**：push 後約 60 秒 https://hangsau.github.io/cscs-study/ 自動更新
5. **書本內容不上 GitHub**：`by_book/` 在 `.gitignore` 排除，Talos 讀書後只寫「個人摘要」不抄原文
6. **你不用自己讀書**：Talos 主動讀 + 摘要，你只需要讀摘要 + 答題

---

## 未來可加（不急）

- **Slash command 整合**：`/cscs quiz`、`/cscs done`、`/cscs push`
- **背景 watcher**：TG 訊息後 1hr 沒新訊息就自動 commit + push
- **Talos 主動 daily review 提醒**：每天早上 TG 通知「今天該複習什麼」
