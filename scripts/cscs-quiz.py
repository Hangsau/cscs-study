#!/usr/bin/env python3
"""
cscs-quiz.py — 記錄 CSCS topic quiz 對錯 + 自動算弱點 + 自動標記

給 TG Talos 在分段問答結束後跑，用法：

    python3 scripts/cscs-quiz.py ch03 --result A,B,A,D,C --correct A,B,D,A,C
    python3 scripts/cscs-quiz.py ch03 --result A,B,A,D,C --correct A,B,D,A,C \
        --section "Energy Systems Overview"
    python3 scripts/cscs-quiz.py --dry-run ch03 --result A,B,A,D,C --correct A,B,D,A,C

互動模式（Talos 出題 → user 答 → 一題一題記）：

    python3 scripts/cscs-quiz.py ch03 --interactive

功能：
1. 寫入 data/quiz_log.yaml（每題對錯歷史）
2. 算該 topic 累積答對率（從 quiz_log 全部 entry）
3. 自動跑 cscs-mark.py 標記狀態：
   - 答對率 ≥ 80% → mastered
   - 答對率 50-79% → learning
   - 答對率 < 50% → 留 todo
4. 列出答錯的子題（讓 /weak/ 頁面顯示）

std-lib only
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUIZ_LOG = ROOT / "data" / "quiz_log.yaml"
TOPICS_YAML = ROOT / "data" / "topics.yaml"


def parse_yaml_list(path: Path) -> list[dict]:
    """最簡單的 yaml list of dict parser — 每個 entry 一組 `key: value`"""
    content = path.read_text(encoding="utf-8")
    # 先處理：用 --- 分隔的 entry
    entries = []
    for chunk in re.split(r"(?=\n- )", "\n" + content):
        chunk = chunk.strip()
        if not chunk.startswith("- "):
            continue
        entry = {}
        # 第一行是 "- key: value"
        first = chunk[2:].split("\n", 1)[0]
        if ":" in first:
            k, v = first.split(":", 1)
            entry[k.strip()] = _coerce(v.strip())
        # 後續行 "  key: value"
        for line in chunk.split("\n")[1:]:
            if ":" in line and not line.startswith("  #"):
                k, v = line.strip().split(":", 1)
                entry[k.strip()] = _coerce(v.strip())
        if entry:
            entries.append(entry)
    return entries


def _coerce(v: str):
    """字串 → bool / int / str"""
    if v == "true":
        return True
    if v == "false":
        return False
    if v == "null" or v == "":
        return None
    try:
        return int(v)
    except ValueError:
        v = v.strip('"').strip("'")
        return v


def write_quiz_log(path: Path, entries: list[dict]) -> None:
    """把 entries 寫回 yaml — 簡單格式"""
    lines = ["# CSCS quiz 對錯歷史", "# Talos 每次分段問答後跑 cscs-quiz.py 記錄", "# 結構：date / topic / section / q_index / user_answer / correct_answer / is_correct", ""]
    for e in entries:
        lines.append(f"- date: {e['date']}")
        lines.append(f"  topic: {e['topic']}")
        lines.append(f'  section: "{e.get("section", "")}"')
        lines.append(f"  q_index: {e['q_index']}")
        lines.append(f"  user_answer: \"{e.get('user_answer', '')}\"")
        lines.append(f"  correct_answer: \"{e.get('correct_answer', '')}\"")
        lines.append(f"  is_correct: {str(e.get('is_correct', False)).lower()}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def aggregate_topic(entries: list[dict], topic: str) -> tuple[int, int, float]:
    """回傳 (correct, total, percent)"""
    topic_entries = [e for e in entries if e.get("topic") == topic]
    if not topic_entries:
        return 0, 0, 0.0
    correct = sum(1 for e in topic_entries if e.get("is_correct"))
    total = len(topic_entries)
    return correct, total, (correct / total) * 100 if total else 0.0


def find_weak_sections(entries: list[dict], topic: str) -> list[tuple[str, int, int]]:
    """回傳 [(section, wrong, total)] 答錯率最高的 sections"""
    sections = defaultdict(lambda: [0, 0])  # [correct, total]
    for e in entries:
        if e.get("topic") != topic:
            continue
        sec = e.get("section", "(no section)")
        sections[sec][1] += 1
        if e.get("is_correct"):
            sections[sec][0] += 1
    weak = []
    for sec, (correct, total) in sections.items():
        wrong = total - correct
        weak.append((sec, wrong, total))
    weak.sort(key=lambda x: (-x[1], x[0]))
    return weak


def auto_mark(topic: str, percent: float, dry_run: bool = False) -> str:
    """根據答對率決定 status"""
    if percent >= 80:
        new_status = "mastered"
    elif percent >= 50:
        new_status = "learning"
    else:
        new_status = "todo"
    if dry_run:
        return new_status
    # 呼叫 cscs-mark.py
    cmd = ["python3", str(ROOT / "scripts" / "cscs-mark.py"), topic, new_status]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        # 不印 subprocess 輸出（會混淆）
        return new_status if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="記錄 CSCS quiz 對錯")
    parser.add_argument("topic_id", help="topic id，如 ch03")
    parser.add_argument("--result", help="user 答案逗號分隔，如 A,B,A,D,C")
    parser.add_argument("--correct", help="正確答案逗號分隔，如 A,B,D,A,C")
    parser.add_argument("--section", default="", help="這批題目的 section 名（單一 section 用）")
    parser.add_argument("--sections", default="", help="每題 section 對應，逗號分隔（覆寫 --section）")
    parser.add_argument("--interactive", action="store_true", help="互動模式：一題一題問")
    parser.add_argument("--dry-run", action="store_true", help="只計算不寫檔")
    args = parser.parse_args()

    # 讀現有 quiz log
    if QUIZ_LOG.exists():
        entries = parse_yaml_list(QUIZ_LOG)
    else:
        entries = []

    today = date.today().isoformat()

    # 收集新 entries
    new_entries = []
    if args.interactive:
        print(f"互動模式：ch{args.topic_id[2:]} 逐題記錄")
        print("輸入正確答案 A/B/C/D，user 答對按 y 錯按 n（quit 離開）")
        i = 1
        while True:
            sec = args.section or input(f"  Q{i} section（空白跳過）: ").strip() or "(no section)"
            ans_user = input(f"  Q{i} user 答案: ").strip().upper()
            if ans_user == "QUIT":
                break
            ans_correct = input(f"  Q{i} 正確答案: ").strip().upper()
            is_correct = ans_user == ans_correct
            new_entries.append({
                "date": today,
                "topic": args.topic_id,
                "section": sec,
                "q_index": i,
                "user_answer": ans_user,
                "correct_answer": ans_correct,
                "is_correct": is_correct,
            })
            print(f"    {'✓' if is_correct else '✗'}")
            i += 1
    elif args.result and args.correct:
        user_ans = [a.strip().upper() for a in args.result.split(",")]
        correct_ans = [a.strip().upper() for a in args.correct.split(",")]
        if len(user_ans) != len(correct_ans):
            print(f"ERROR: --result ({len(user_ans)}) 跟 --correct ({len(correct_ans)}) 數量不符", file=sys.stderr)
            return 2
        sections = []
        if args.sections:
            sections = [s.strip() for s in args.sections.split(",")]
        elif args.section:
            sections = [args.section] * len(user_ans)
        else:
            sections = ["(no section)"] * len(user_ans)
        for i, (u, c, s) in enumerate(zip(user_ans, correct_ans, sections), 1):
            new_entries.append({
                "date": today,
                "topic": args.topic_id,
                "section": s,
                "q_index": i,
                "user_answer": u,
                "correct_answer": c,
                "is_correct": u == c,
            })
    else:
        parser.error("需要 --result + --correct 或 --interactive")

    if not new_entries:
        print("no entries to record")
        return 0

    # 合併舊 + 新
    all_entries = entries + new_entries

    # 印這次結果
    new_correct = sum(1 for e in new_entries if e["is_correct"])
    print(f"\n  本次 quiz：{args.topic_id}")
    print(f"  新增 {len(new_entries)} 題，對 {new_correct} 題")
    print(f"  本次答對率：{new_correct}/{len(new_entries)} = {new_correct/len(new_entries)*100:.0f}%")

    # 寫入 quiz_log.yaml
    if not args.dry_run:
        write_quiz_log(QUIZ_LOG, all_entries)
        print(f"  ✓ wrote {QUIZ_LOG}")

    # 算 topic 累積
    cum_correct, cum_total, cum_percent = aggregate_topic(all_entries, args.topic_id)
    print(f"\n  累積（含舊記錄）：{cum_correct}/{cum_total} = {cum_percent:.0f}%")

    # 自動標記
    new_status = auto_mark(args.topic_id, cum_percent, dry_run=args.dry_run)
    print(f"\n  自動標記：mastery_status → {new_status}")
    if not args.dry_run:
        print(f"\n  下一步：")
        print(f"    git add data/quiz_log.yaml data/topics.yaml")
        print(f"    git commit -m \"{args.topic_id} quiz 答對率 {cum_percent:.0f}% → {new_status}\"")
        print(f"    git push origin master    # → 站自動 ~60s rebuild")

    # 顯示弱點 sections
    weak_sections = find_weak_sections(all_entries, args.topic_id)
    if weak_sections and any(w > 0 for _, w, _ in weak_sections):
        print(f"\n  弱點 sections（按錯題數排序）：")
        for sec, wrong, total in weak_sections[:5]:
            if wrong > 0:
                print(f"    ✗ {sec}: 錯 {wrong}/{total}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
