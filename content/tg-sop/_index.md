---
title: "TG Talos SOP"
description: "透過 @HangTalos_Bot 跟 Claude Code 對話複習 CSCS"
date: 2026-06-25
last_updated: 2026-06-25
---

# TG Talos SOP

> **前提**：`claude-tg-bot`（`~/projects/claude-tg-bot/`）24/7 跑著，bot 是 `@HangTalos_Bot`。手機打開 TG 傳訊息，Claude Code 會在 VM 上跑並回應。
>
> **CSCS 複習對 Claude 來說 = 讀 `~/cscs-study/` 下的書 + 寫/更新 yaml + 寫筆記 + commit + push。** 直接用自然語言說要做什麼就行。

---

## 🚀 自動化工作流（建議主流程）

每次跟 Talos 對話複習一個章節，建議走這個流程 — **Talos 會自己判斷「會 / 不會」並更新狀態**：

```
步驟 1（user 開頭）
  你：「我要開始讀 ch07」

步驟 2（Talos 出選擇題）
  Talos：「好，給你 5 題選擇題考 ch07 重點...」

步驟 3（user 答題）
  你：「1A 2C 3B 4D 5A」

步驟 4（Talos 自動判斷 + 自我更新）
  Talos 內部自動做：
  - 判斷對錯（假設你答對 4/5）
  - 問你：「ch07 我覺得你可以標記為 mastered（或保持 learning），要標嗎？」
  - 你說「標 mastered」→ Talos 跑：
    python3 /home/hangsau/cscs-study/scripts/cscs-mark.py ch07 mastered
  - 寫一則 notes/YYYY-MM-DD-ch07-first-read.md（個人筆記 + 弱點）

步驟 5（自動 commit + push）
  Talos 自動問：「要 commit + push 嗎？（站會自動 rebuild）」
  你說「好」→ Talos 跑：
    cd /home/hangsau/cscs-study
    git add data/topics.yaml content/notes/
    git commit -m "ch07 mastered + 筆記"
    git push origin master   # → https://hangsau.github.io/cscs-study/ ~60s 更新

步驟 6（你下一個對話週期）
  1 天後 user 再回來跟 Talos 說「我要 review ch07」（spaced repetition 1/3/7/14/30 天節奏）
```

**Talos 自己判斷「會 / 不會」的依據**：
- 4-5 題對 → 建議標 `mastered`（user 確認）
- 2-3 題對 → 標 `learning`（繼續練習）
- 0-1 題對 → 留 `todo` 或 `learning`，寫錯題 notes

---

## 📋 快速指令模板（copy-paste 用）

### 1. 讀 + 寫筆記（開始新 topic）

```
我要開始讀 NSCA ch07（年齡性別差異）。

請幫我：
1. 讀 ~/cscs-study/by_book/doc_df238de65892_ch07_*.md
2. 用我的話寫一篇個人學習筆記存到 ~/cscs-study/content/notes/2026-MM-DD-ch07-first-read.md
3. 更新 ~/cscs-study/data/topics.yaml 把 ch07 的 mastery_status 改成 learning
4. 跑 scripts/cscs-mark.py ch07 learning 確認狀態
```

### 2. 讓 Talos 出選擇題

```
我要練習 ch03（Bioenergetics）。

請出 10 題選擇題（4 選 1），考 ATP-PC / 糖酵解 / 有氧三大能量系統時間表。
每題先給題幹，等我答完再給答案跟詳解。
```

### 3. 標記 topic 為 mastered

```
我覺得 ch03 我已經熟了。

請跑：
  python3 /home/hangsau/cscs-study/scripts/cscs-mark.py ch03 mastered
然後 commit + push。
```

### 4. 查今天該複習什麼（spaced repetition）

```
請跑：
  grep -E "next_review: $(date +%Y-%m-%d)" ~/cscs-study/data/topics.yaml
列出所有今天到期的 topic，每個給我 3 題關鍵問題測試我自己。
```

### 5. teach back（給 Talos 聽你講解）

```
我要用 teach back 練習 ch17。

我會用 3 分鐘講阻力訓練計畫設計的 SET 原則。
講完你告訴我哪裡講錯、哪裡缺漏。
```

### 6. 寫錯題筆記

```
我剛做完 ch11 的題目，錯了這題：

題目：[題幹]
我答：[我的答案]
正解：[正解]

請把這個錯題寫到 ~/cscs-study/content/notes/2026-MM-DD-mistake-ch11.md，
包含：題目、我的答案、正解、為什麼錯、你幫我分析、這個 topic 我還沒掌握的概念。
```

### 7. 跨章節應用題

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
3. 列成口訣格式方便考前最後掃一眼
```

---

## 🛠️ helper script：`scripts/cscs-mark.py`

`cscs-mark.py` 是 stdlib only 的 helper，Talos 在對話中跑一行就能更新狀態：

```bash
# 標記為 mastered（自動 +review_count + 計算 next_review）
python3 scripts/cscs-mark.py ch03 mastered

# 標記為 learning
python3 scripts/cscs-mark.py ch07 learning

# 只 +review_count 不改 status（單純複習過）
python3 scripts/cscs-mark.py ch15 review

# 預覽不寫檔
python3 scripts/cscs-mark.py --dry-run ch03 mastered

# 標錯了想重來
python3 scripts/cscs-mark.py ch03 todo
```

**spaced repetition 節奏**：
| review_count | next_review |
|--------------|-------------|
| 1 | +1 天 |
| 2 | +3 天 |
| 3 | +7 天 |
| 4 | +14 天 |
| 5+ | +30 天 |

---

## 對話節奏建議

| 時段 | 動作 | 用哪個 prompt |
|------|------|--------------|
| 早上 | 開新 topic | (1) |
| 下午 | 練習提取 | (2) 或 (7) |
| 晚上 | 標記進度 + 寫錯題 | (3) + (6) + commit + push |
| 週末 | 跨章節 + 講解 | (5) + (4) |
| 考前 | 快速回顧 | (8) |

---

## 注意事項

1. **claude-tg-bot 不會自動 commit / push**（除非你明確說要）— 預設保守行為
2. **claude-tg-bot 走 bypassPermissions**：可以直接寫檔（小心 token / secrets）
3. **每次對話建議明確指定檔案路徑**：避免 Claude 寫到別處
4. **站 deploy 是 GitHub Actions**：push 後約 60 秒 https://hangsau.github.io/cscs-study/ 自動更新
5. **書本內容不上 GitHub**：`by_book/` 在 `.gitignore` 排除，data/topics.yaml 的 `source_file` 路徑是本地參考用

---

## 未來可加（不急）

- **Slash command 整合**：`/cscs quiz`、`/cscs done`、`/cscs push` — 在 `~/projects/claude-tg-bot/` 加 command handler
- **背景 watcher**：TG 訊息後 1hr 沒新訊息就自動 commit + push 當天進度
- **自動錯誤偵測**：Talos 出選擇題時 user 答錯就自動寫錯題 notes（不用 user 指示）

等真的每天用、發現重複輸入的 prompt 多再寫。
