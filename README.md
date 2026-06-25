# CSCS Study Hub

NSCA CSCS 認證備考追蹤站 + 個人學習筆記本。

方法論基於 **A Mind for Numbers**（大腦喜歡這樣學）— Barbara Oakley 著，強調間隔重複、提取練習、變式練習、心智模型。

## 來源書

- `Essentials of Strength Training and Conditioning, 4th Edition` — NSCA 官方 CSCS 教材（24 章）
- `大腦喜歡這樣學`（A Mind for Numbers 中譯）— 學習方法論
- `大腦喜歡這樣學・強效教學版` — 補強版（含教師視角）

## 快速開始

```bash
# 開發模式（自動 reload）
cd ~/cscs-study
hugo server -D --port 1313

# 開瀏覽器
xdg-open http://localhost:1313   # 或 firefox / chromium
```

## 站內導覽

- **首頁** `/` — 進度儀表板
- **進度** `/progress/` — 詳細進度表
- **Topic 清單** `/topics/` — 24 章 CSCS topic 卡
- **已學會** `/mastered/` — 完成的章節筆記
- **學習中** `/learning/` — 正在學的章節
- **待學** `/todo/` — 還沒開始的章節
- **筆記本** `/notes/` — 時間序列學習筆記
- **複習計畫** `/plan/` — 方法論 + 8 週衝刺
- **TG Talos SOP** `/tg-sop/` — 透過 Telegram 跟 Claude 對話複習

## 專案交接

`CLAUDE.md` 是給接手 Claude 看的（不是 README）。
