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

## 🚀 自動化工作流（Talos 主動版）

```
步驟 1（user 開頭）
  你：「我要開始 ch07」

步驟 2（Talos 自動讀書 + 摘要）
  Talos 自動：
  - 讀 ~/cscs-study/by_book/doc_*_ch07_*.md 整章
  - 寫個人摘要到 content/notes/YYYY-MM-DD-ch07-summary.md
    （用自己的話講重點，不抄原文 — 這是「理解」的關鍵）
  - 標 ch07 status: learning
  - 跑 cscs-mark.py ch07 learning

步驟 3（Talos 出選擇題）
  Talos：「我寫完摘要了（連結）。現在出 5 題選擇題考你 ch07 重點...」

步驟 4（user 答題）
  你：「1A 2C 3B 4D 5A」

步驟 5（Talos 自動判斷 + 自我更新）
  Talos 內部自動：
  - 判斷對錯（假設你答對 4/5）
  - 問你：「ch07 我覺得你可以標記為 mastered，要標嗎？」
  - 你說「好」→ Talos 跑：
    python3 scripts/cscs-mark.py ch07 mastered
  - 寫一則 content/notes/YYYY-MM-DD-ch07-quiz-result.md（你錯的題）

步驟 6（自動 commit + push）
  Talos 自動問：「要 commit + push 嗎？」
  你說「好」→ Talos 跑：
    cd ~/cscs-study
    git add data/topics.yaml content/notes/
    git commit -m "ch07 mastered + 摘要 + quiz"
    git push origin master   # → https://hangsau.github.io/cscs-study/ ~60s 更新

步驟 7（間隔重複 — 1 天後）
  Talos 在 daily review 提醒你：「ch07 next_review 到了」
  → 7 天後建議用 teach back（講 3 分鐘給 Talos 聽）確認真會
```

**為什麼 Talos 主動讀書有效？**

- 你不需要自己先讀，**節省時間**
- Talos 寫的摘要是**自己消化過的**（不是 highlight），所以有用
- 你讀 Talos 的摘要 → free recall（30 秒用自己的話講）→ 比直接讀書效果好（書第 4 章「能力的錯覺」）
- 出題是**讓你主動回想**（不是被動讀），最強學習

**Talos 自己判斷「會 / 不會」的依據**：
- 4-5 題對 → 標 `mastered`
- 2-3 題對 → 標 `learning`
- 0-1 題對 → 留 `todo` 或 `learning` + 寫錯題 notes

---

## 📋 快速指令模板（copy-paste 用）

### 0. 開始新章節（Talos 自動讀書）⭐ 主推

```
我要開始 ch07（年齡性別差異與阻力訓練意涵）。

請幫我：
1. 讀 ~/cscs-study/by_book/doc_df238de65892_ch07_*.md 整章
2. 寫個人摘要到 content/notes/YYYY-MM-DD-ch07-summary.md
   （用自己的話，不要抄原文）
3. 標 ch07 status: learning（跑 cscs-mark.py ch07 learning）
4. 出 5 題選擇題考 ch07 重點
5. 寫完摘要後給我看連結
```

### 1. 只寫摘要（不跳到練習）

```
幫我讀 ~/cscs-study/by_book/doc_df238de65892_ch07_*.md
寫摘要到 content/notes/YYYY-MM-DD-ch07-summary.md
（用自己的話，3 段以內）
```

### 2. 只出選擇題

```
我剛讀完 ch03 的摘要（~/cscs-study/content/notes/YYYY-MM-DD-ch03-summary.md）。

請出 10 題選擇題（4 選 1）考 ATP-PC / 糖酵解 / 有氧三大能量系統時間表。
每題先給題幹，等我答完再給答案 + 詳解。
```

### 3. 標記 topic 為 mastered

```
我答完 ch03 的題目了，4/5 對。

請跑：
  python3 /home/hangsau/cscs-study/scripts/cscs-mark.py ch03 mastered
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
