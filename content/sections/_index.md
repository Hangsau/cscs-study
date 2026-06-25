---
title: 章節拆解進度
description: 24 章 NSCA 書 sections 拆解追蹤 + 驗證狀態
---

> **狀態說明**：
> - **拆好**：`data/sections/chXX.yaml` 已生成
> - **對齊**：`verify_sections.py` 跑出 split 內部與 by_book/ H2 對齊（✓ 表示 100% 對齊）
> - **標籤完成**：`tags / key_points / recall_prompts` 都已填（ch01 已示範）
> - **人工驗證**：⚠ 這欄目前**還沒做**，要你對照 NSCA 原書（host 端 PDF/epub 或實體書）看

## 驗證狀態

| 章節 | Sections | H2 | H3 | 對齊？ | 標籤 | 人工驗證 |
|------|----------|----|----|--------|------|---------|
{{ range $cid, $info := (index .Site.Data.sections_index) }}| {{ $cid | upper }} | {{ $info.sections_count }} | — | — | ✓ | {{ if $info.has_tags }}✓{{ else }}—{{ end }} | ⚠ 待驗 |
{{ end }}

## 怎麼驗證

```bash
# 1. 看 split 對齊（內部一致）
python3 scripts/verify_sections.py

# 2. 抽 1-2 章對照 NSCA 原書（你要做）
# 開 ~/cscs-study/by_book/chXX.md 對照 NSCA Essentials 4th 原書
# 或對照 ~/cscs-study/data/sections/chXX.yaml 看 split 結果

# 3. 發現錯就手動修 yaml 或 split_chapter.py 加規則重跑
```

## 驗證 priority 建議

建議優先驗這 5 章（涵蓋不同結構）：
- **ch01** — 簡單 5 H2 + 11 H3（已示範加 metadata）
- **ch03** — 7 H2 含 1 大 H2（45KB）已 auto-sub（12 sections）
- **ch05** — 24 sections（auto-sub 切很多）
- **ch14** — 43 sections（Warm-Up 章節動作很多）
- **ch15** — 42 sections（Exercise Technique 章節動作很多）

驗完一張回報「chXX OK」或「chXX 有錯：...」我來處理。
