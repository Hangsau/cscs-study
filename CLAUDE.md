# CSCS Study Hub — 交接單

> **本檔受眾**：未來接手 cscs-study 專案的 Claude session
> **不是**：README（看 README.md）
> **建立**：2026-06-25（從原本散落三處整合 + 升級為 Hugo 站）

---

## 0. 目標

協助 Hang 準備 NSCA CSCS（Certified Strength and Conditioning Specialist）考試，方法論基於 A Mind for Numbers（大腦喜歡這樣學），並透過 Hugo 靜態站即時追蹤進度。

**🌐 Live 站**：https://hangsau.github.io/cscs-study/（GitHub Pages，自動從 master rebuild）

## 1. 技術棧

| 元件 | 版本 | 用途 |
|------|------|------|
| Hugo | 0.163.3 extended | 靜態站生成（已有 `which hugo` 確認） |
| 內容格式 | Markdown + YAML | Hugo 標準 |
| 部署 | `hugo server -D`（開發）+ `hugo`（build）| 本地為主 |
| 書源 | `/home/hangsau/books/`（VirtualBox 唯讀掛載） | grep 用 |

## 2. 內容來源（書）

| 書 | 路徑 | 角色 |
|----|------|------|
| Essentials of Strength Training and Conditioning 4th | `/home/hangsau/books/Essentials_of_Strength_Training_and_Conditioning,_Fourth_Edition/` | **CSCS 官方教材**，24 章 .md 已在 `by_book/` |
| 大腦喜歡這樣學（A Mind for Numbers 中譯） | `/home/hangsau/books/大腦喜歡這樣學/` | **學習方法論**：PART 3 記憶、P5 應考 |
| 大腦喜歡這樣學・強效教學版 | `/home/hangsau/books/大腦喜歡這樣學・強效教學版/` | **補強**：記憶法 + 鷹架教學 |

注意：`/home/hangsau/books/` 是 **VirtualBox 唯讀共享資料夾**（host: `C:\claudehome\resources\books`），要改改 host。

## 3. 目錄結構

```
~/cscs-study/
├── CLAUDE.md                    # 本檔（交接單）
├── README.md                    # 給人看
├── hugo.yaml                    # Hugo config
├── content/                     # Hugo content
│   ├── _index.md                # 首頁（儀表板）
│   ├── progress/                # 進度頁
│   ├── topics/                  # 24 個 CSCS topic 卡
│   ├── mastered/                # 已學會章節（讀書心得 + 練習記錄）
│   ├── learning/                # 正在學
│   ├── todo/                    # 待學
│   ├── notes/                   # 個人學習筆記（時間序列）
│   ├── plan/                    # 複習計畫 + 方法論
│   └── tg-sop/                  # Telegram Talos SOP
├── data/
│   ├── topics.yaml              # 24 topic + mastery_status
│   └── progress.yaml            # 進度彙總
├── layouts/                     # Hugo layouts（root-level，會覆蓋 theme）
├── themes/cscs/                 # 自寫 Hugo theme
├── static/css/                  # 自訂 CSS
├── by_book/                     # 既有 NSCA 24 章 .md（git tracked）
├── archive/
│   ├── legacy-hermes-notes/     # 從 hermes_notes/cscs_study 來的舊版
│   └── non-cscs-readings/       # alice-in-wonderland 等無關
└── reading-reflections/         # （保留為空，舊檔已移走）
```

## 4. 維護機制

### 開發（隨時更新網站）

```bash
cd ~/cscs-study
hugo server -D --port 1313 --baseURL http://localhost:1313   # 開發模式，瀏覽器 http://localhost:1313 自動 reload
```

注意：本地 dev 跑要加 `--baseURL http://localhost:1313` 覆蓋 hugo.yaml 的 prod URL，否則 CSS 會指到 GitHub Pages。

### Build 靜態站

```bash
cd ~/cscs-study
hugo --minify                 # 產 ~/cscs-study/public/
```

### Deploy（自動）

推 master → GitHub Actions 自動 build + deploy Pages（`.github/workflows/hugo.yaml`）。
約 60 秒後 https://hangsau.github.io/cscs-study/ 更新。

### 更新進度

- **手動更新**：編輯 `data/topics.yaml` 把對應 topic 的 `mastery_status` 從 `todo` 改 `learning` 或 `mastered`。
- **TG 更新**：見 `content/tg-sop/` SOP（透過 @HangTalos_Bot 跟 Claude Code 對話，由 Claude 幫更新 yaml）。

### Topic → 章節筆記流程

1. 從 `data/topics.yaml` 看到 status 為 `learning` 的 topic
2. 讀 `by_book/doc_*_chXX_*.md`（NSCA 書原始內容）
3. 寫 `content/mastered/chXX-name.md`（讀書心得 + 個人理解）
4. 寫 `content/notes/YYYY-MM-DD-chXX-first-read.md`（時間序列筆記）
5. 把 topic status 改 `mastered`
6. `hugo server -D` 自動 rebuild

## 5. 已知問題

- **K-C01**: `.hermes/notes/cscs_study/exercise_science/anatomy_basics.md` 整合進 `content/notes/2026-06-25-anatomy-basics-start.md`，原始檔保留在 `archive/legacy-hermes-notes/exercise_science/` 供查。
- **K-C02**: `hermes_notes/cscs_study/`（`/home/hangsau/hermes_notes/cscs_study/`）整體 mojibake 嚴重，不採內容。整個目錄搬到 `archive/legacy-hermes-notes/`。
- **K-C03**: `reading-reflections/alice-in-wonderland-reflection.md` 跟 CSCS 無關，移到 `archive/non-cscs-readings/`。
- **K-C04**: NSCA 書 ch07/ch11/ch16/ch24 等少數章節檔名被 truncate（如 `ch07_age-_and_sex-related_differences_...`），`data/topics.yaml` 用章節序號 mapping 不依賴檔名。

## 6. 不要做的事

1. ❌ **不要 push `by_book/` 內容到 GitHub**：NSCA 書 24 章有版權（已在 `.gitignore` 排除，本地保留）
2. ❌ **不要 push `archive/non-cscs-readings/`**（個人私人反思，已在 `.gitignore` 排除）
3. ❌ **不要改 `/home/hangsau/books/`**：VirtualBox 唯讀
4. ❌ **不要 commit 任何 token / `.env` / `secrets.env`**
5. ❌ **不要把學習筆記當研究報告寫**：個人理解優先，不是百科全書
6. ❌ **不要自動更新 topics.yaml 的 mastery_status**：由 user 自己決定，或透過 TG 對話 SOP 改

## 7. TG Talos SOP（摘要）

`content/tg-sop/_index.md` 有完整 prompt 範本。核心：
- 自由對話：`「我要練習 ch07，請出 5 題選擇題」`
- 自由對話：`「幫我把 ch03 標記為 learning 狀態」`
- 自由對話：`「寫一則學習筆記：[...]」`

不修改 `claude-tg-bot` 程式（已 24/7 跑著），純 prompt 範本。

## 8. 接手 Claude 必讀

1. 讀 `data/topics.yaml` 看當前進度
2. 讀 `content/plan/study-methodology.md` 理解方法論
3. 讀 `content/plan/8-week-sprint.md` 理解時程
4. 跑 `hugo server -D` 確認站能起來
