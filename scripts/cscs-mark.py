#!/usr/bin/env python3
"""
cscs-mark.py — 標記 CSCS topic 狀態 + 自動 spaced repetition
給 TG Talos 在對話結尾自動跑，用法：

    python3 scripts/cscs-mark.py ch03 mastered
    python3 scripts/cscs-mark.py ch07 learning
    python3 scripts/cscs-mark.py ch15 review      # +review_count，不改 status

功能：
1. 讀 data/topics.yaml
2. 更新指定 topic 的 mastery_status / review_count
3. 根據 review_count 推進 next_review（spaced repetition 1/3/7/14/30 天節奏）
4. 寫回 yaml（保留註解 — 用最簡單的「整檔覆寫」方式，不保留原註解）
5. 印出 git commit 建議指令（不自動 commit — user 自己決定）

Spaced repetition 節奏：
- review_count 1 → +1 天
- review_count 2 → +3 天
- review_count 3 → +7 天
- review_count 4 → +14 天
- review_count 5+ → +30 天

std-lib only — 跨環境可跑，不需 pip install
"""

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
TOPICS_YAML = ROOT / "data" / "topics.yaml"

SPACED_INTERVALS = [1, 3, 7, 14, 30]  # days after each review


def parse_topics(path: Path) -> list[dict]:
    """簡單 YAML list parser — 適用於本專案固定結構的 topics.yaml"""
    content = path.read_text(encoding="utf-8")
    # 用 findall 抓每個 topic block（從 "- id:" 到下一個 "- id:" 或 EOF）
    blocks = re.findall(r"- id:.*?(?=\n- id: |\Z)", content, re.DOTALL)
    topics = []
    for b in blocks:
        if "- id:" not in b:
            continue
        fields = {}
        for key in ["id", "title", "title_zh", "domain", "domain_zh", "section",
                     "mastery_status", "next_review", "source_file", "notes"]:
            m = re.search(rf'\b{key}:\s*"([^"]*)"', b)
            if m:
                fields[key] = m.group(1)
            else:
                m2 = re.search(rf"\b{key}:\s*(\S+)", b)
                if m2:
                    fields[key] = m2.group(1).strip('"')
        for key in ["priority", "review_count"]:
            m = re.search(rf"\b{key}:\s*(\d+)", b)
            if m:
                fields[key] = int(m.group(1))
        if "id" in fields:
            topics.append(fields)
    return topics


def write_topics(path: Path, topics: list[dict]) -> None:
    """把 topics 寫回 yaml — 固定格式覆寫"""
    lines = ["# CSCS 24 Topic 狀態（NSCA Essentials 4th Edition 章節對應）",
             "# mastery_status: todo / learning / mastered",
             "# priority: 1=最高（先學）, 2=中, 3=最低（最後）",
             "# next_review: YYYY-MM-DD，spaced repetition 節奏",
             "# notes: 個人簡短註記",
             "#",
             "# NSCA CSCS 考試兩大 section + 7 domain 對應：",
             "#   F = Foundational Knowledge (~31%)",
             "#   A = Apply Science to Training (~30%)",
             "#   N = Nutrition (~10%)",
             "#   T = Testing & Evaluation (~10%)",
             "#   O = Organization & Administration (~10%)",
             "#   R = Risk Management / Rehab (~5%)",
             ""]
    for t in topics:
        lines.append(f"- id: {t['id']}")
        lines.append(f'  title: "{t.get("title", "")}"')
        lines.append(f'  title_zh: "{t.get("title_zh", "")}"')
        lines.append(f'  domain: {t.get("domain", "")}')
        lines.append(f'  domain_zh: "{t.get("domain_zh", "")}"')
        lines.append(f"  section: {t.get('section', '')}")
        lines.append(f"  priority: {t.get('priority', 3)}")
        lines.append(f"  mastery_status: {t.get('mastery_status', 'todo')}")
        lines.append(f"  last_review: {t.get('last_review', 'null')}")
        lines.append(f"  next_review: {t.get('next_review', '')}")
        lines.append(f"  review_count: {t.get('review_count', 0)}")
        lines.append(f'  source_file: "{t.get("source_file", "")}"')
        lines.append(f'  notes: "{t.get("notes", "")}"')
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def compute_next_review(review_count: int, from_date: date | None = None) -> date:
    """根據 review_count 推進 next_review（spaced repetition）"""
    if from_date is None:
        from_date = date.today()
    idx = min(review_count - 1, len(SPACED_INTERVALS) - 1)
    if idx < 0:
        idx = 0
    return from_date + timedelta(days=SPACED_INTERVALS[idx])


def main() -> int:
    parser = argparse.ArgumentParser(description="標記 CSCS topic 狀態")
    parser.add_argument("topic_id", help="topic id，如 ch03")
    parser.add_argument("action", choices=["todo", "learning", "mastered", "review"],
                        help="要做的動作：todo / learning / mastered / review（review = 只 +review_count，不改 status）")
    parser.add_argument("--dry-run", action="store_true", help="只印出結果不寫檔")
    args = parser.parse_args()

    if not TOPICS_YAML.exists():
        print(f"ERROR: {TOPICS_YAML} not found", file=sys.stderr)
        return 1

    topics = parse_topics(TOPICS_YAML)
    target = None
    for t in topics:
        if t["id"] == args.topic_id:
            target = t
            break
    if target is None:
        print(f"ERROR: topic {args.topic_id} not found in {TOPICS_YAML}", file=sys.stderr)
        print(f"  available: {', '.join(t['id'] for t in topics)}", file=sys.stderr)
        return 2

    today = date.today()
    old_status = target.get("mastery_status", "todo")
    old_review = target.get("review_count", 0)

    if args.action == "review":
        new_review = old_review + 1
        new_next = compute_next_review(new_review, today).isoformat()
        target["review_count"] = new_review
        target["last_review"] = today.isoformat()
        target["next_review"] = new_next
        print(f"  {args.topic_id} {target.get('title_zh', '')}")
        print(f"  review_count: {old_review} → {new_review}")
        print(f"  last_review:  {today.isoformat()}")
        print(f"  next_review:  {new_next}（+{SPACED_INTERVALS[min(new_review-1, len(SPACED_INTERVALS)-1)]} 天）")
        print(f"  mastery_status: {old_status}（不變）")
    else:
        new_review = old_review + 1
        new_next = compute_next_review(new_review, today).isoformat()
        target["mastery_status"] = args.action
        target["review_count"] = new_review
        target["last_review"] = today.isoformat()
        target["next_review"] = new_next
        print(f"  {args.topic_id} {target.get('title_zh', '')}")
        print(f"  mastery_status: {old_status} → {args.action}")
        print(f"  review_count: {old_review} → {new_review}")
        print(f"  last_review:  {today.isoformat()}")
        print(f"  next_review:  {new_next}")

    if args.dry_run:
        print("\n  (--dry-run: 不寫檔)")
        return 0

    write_topics(TOPICS_YAML, topics)
    print(f"\n  ✓ wrote {TOPICS_YAML}")
    print(f"\n  下一步：")
    print(f"    git add data/topics.yaml")
    print(f"    git commit -m \"{args.topic_id} 標記為 {args.action}\"")
    print(f"    git push origin master    # → 站自動 ~60s rebuild")
    return 0


if __name__ == "__main__":
    sys.exit(main())
