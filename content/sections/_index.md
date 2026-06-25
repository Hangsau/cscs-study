---
title: 章節拆解進度
description: 24 章 NSCA 書 sections 拆解追蹤 + 驗證狀態
---

> **狀態說明**：
> - **拆好**：`data/sections/chXX.yaml` 已生成
> - **標籤 / Key Points / Recall Prompts**：是否已填 metadata（24/24 全 ✓）
> - **人工驗證**：⚠ 這欄**還沒做**，要你對照 NSCA 原書看

## 驗證狀態

{{< sections-table >}}

## 怎麼驗證

```bash
# 1. 看 split 對齊（內部一致）
python3 scripts/verify_sections.py

# 2. 抽 1-2 章對照 NSCA 原書（你要做）
# 開 ~/cscs-study/by_book/chXX.md 對照 NSCA Essentials 4th 原書

# 3. 發現錯就手動修 yaml 或 split_chapter.py 加規則重跑
```

## 驗證 priority 建議

建議優先驗這 5 章（涵蓋不同結構）：

- **ch01** — 簡單 5 H2 + 11 H3（已示範手動 metadata）
- **ch03** — 7 H2 含 1 大 H2（45KB）已 auto-sub（12 sections）
- **ch05** — 24 sections（auto-sub 切很多）
- **ch14** — 43 sections（Warm-Up 章節動作很多）
- **ch15** — 42 sections（Exercise Technique 章節動作很多）

驗完一張回報「chXX OK」或「chXX 有錯：...」我來處理。

## metadata 品質說明

- **ch01**：手動 metadata（36 tags / 41 key_points / 31 prompts）— 品質最高
- **ch02-ch24**：auto metadata（每 section 1-6 tags + 1 key_point + 1 prompt）— 品質基本

要提升 ch02-ch24 品質，可以擴展 `scripts/auto_annotate.py` 加更多邏輯，或參考 ch01 模式一章一章手動加。
