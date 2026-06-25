#!/usr/bin/env python3
"""
split_chapter.py — 把 NSCA by_book/ 章節拆成 sections 結構存到 data/sections/

用途：
    python3 scripts/split_chapter.py ch01         # 自動從 by_book/ 找檔 + 拆
    python3 scripts/split_chapter.py ch01 --tags   # 開互動模式讓 user 加 tags/key_points/recall_prompts
    python3 scripts/split_chapter.py --all         # 一次拆全部 24 章

輸出：
    data/sections/chXX.yaml  # 每章一個 yaml，含 sections list
    data/sections/_index.yaml # 全章節清單（追蹤進度用）

Section 結構：
    - id: ch01-musculoskeletal
      title: "Musculoskeletal System"
      level: 2
      content: |        # 原文完整內容（H2 下所有 H3 + paragraph）
        ...
      tags: [anatomy, bone, muscle, joint]   # 手動加或後續互動
      key_points: [ ... ]                    # 手動加或後續互動
      recall_prompts: [ ... ]                # 手動加（user 想要的回想觸發）
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
BY_BOOK = ROOT / "by_book"
SECTIONS_DIR = ROOT / "data" / "sections"


def find_chapter_file(chapter_id: str) -> Path | None:
    """從 by_book/ 找對應章節 .md（檔名 pattern: doc_*_chXX_*.md）"""
    if not BY_BOOK.exists():
        return None
    # 數字 padding: ch01 -> 01
    num = chapter_id.replace("ch", "").zfill(2)
    pattern = f"_ch{num}_"
    for f in BY_BOOK.iterdir():
        if pattern in f.name and f.suffix == ".md":
            return f
    return None


def split_by_headings(content: str, max_size: int = 15000, auto_sub: bool = True) -> list[dict]:
    """依 H2 (##) 切 sections，過大 (>max_size) 自動用 H3 細切。
    排除 Key Terms / Study Questions / Summary / References 等非學習段落。
    """
    # 排除清單（不學內容，通常章節末）
    EXCLUDE_TITLES = [
        "key terms", "study questions", "summary", "references",
        "key concepts", "review questions", "discussion questions",
        "recommended readings", "bibliography", "key points",
    ]

    h2_pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    h2_matches = list(h2_pattern.finditer(content))

    if not h2_matches:
        return [{"id": "content", "title": "Full chapter", "level": 2, "content": content, "tags": [], "key_points": [], "recall_prompts": []}]

    sections = []
    for i, m in enumerate(h2_matches):
        title = m.group(1).strip()

        # 排除非學習內容
        if title.lower().strip() in EXCLUDE_TITLES:
            continue

        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(content)
        body = content[start:end].rstrip()

        # 過大且啟用 auto_sub → 用 H3 細切
        if auto_sub and len(body) > max_size:
            sub_sections = _split_h3(body, title, EXCLUDE_TITLES)
            sections.extend(sub_sections)
        else:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
            sections.append({
                "id": slug,
                "title": title,
                "level": 2,
                "content": body,
                "tags": [],
                "key_points": [],
                "recall_prompts": [],
            })
    return sections


def _split_h3(body: str, parent_title: str, exclude_titles: list[str]) -> list[dict]:
    """H3 細切一個過大的 H2 section"""
    h3_pattern = re.compile(r"^### (.+)$", re.MULTILINE)
    h3_matches = list(h3_pattern.finditer(body))

    # 沒有 H3 或只有 1-2 個 H3（細切沒意義）— 保持原樣
    if len(h3_matches) < 3:
        slug = re.sub(r"[^a-z0-9]+", "-", parent_title.lower()).strip("-")[:40]
        return [{
            "id": slug,
            "title": parent_title,
            "level": 2,
            "content": body,
            "tags": [],
            "key_points": [],
            "recall_prompts": [],
        }]

    sections = []
    for i, m in enumerate(h3_matches):
        sub_title = m.group(1).strip()
        if sub_title.lower().strip() in exclude_titles:
            continue

        start = m.end()
        end = h3_matches[i + 1].start() if i + 1 < len(h3_matches) else len(body)
        sub_body = body[start:end].rstrip()

        # sub_slug
        sub_slug = re.sub(r"[^a-z0-9]+", "-", sub_title.lower()).strip("-")[:40]
        sections.append({
            "id": sub_slug,
            "title": f"{parent_title} / {sub_title}",  # 帶 parent 前綴避免重複
            "level": 3,
            "content": sub_body,
            "tags": [],
            "key_points": [],
            "recall_prompts": [],
        })
    return sections


def write_chapter_yaml(chapter_id: str, source_file: str, title_zh: str, sections: list[dict]) -> Path:
    """寫 chXX.yaml

    Block scalar writer 修正：
    - 計算 content 內所有非空行的最大 leading whitespace (max_lead)
    - base indent = max_lead + 2
    - 每個非空行加 base indent 前綴（保留原 leading → 保留 list 結構）
    - 空行不縮排
    - 這樣所有行 indent ≥ base，yaml parser 不會因淺縮排提早結束 block
    """
    fp = SECTIONS_DIR / f"{chapter_id}.yaml"
    SECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# CSCS {chapter_id.upper()} sections",
        f"# 從 by_book/ 拆出（split_chapter.py 自動生成）",
        f"# chapter: {title_zh}",
        f"# source: {source_file}",
        f"# sections: {len(sections)}",
        "",
        f"chapter_id: {chapter_id}",
        f"chapter_title_zh: \"{title_zh}\"",
        f"source_file: \"{source_file}\"",
        f"sections:",
    ]
    for s in sections:
        lines.append(f"  - id: \"{chapter_id}-{s['id']}\"")
        lines.append(f"    title: \"{s['title']}\"")
        lines.append(f"    level: {s['level']}")
        lines.append(f"    tags: [{', '.join(s['tags'])}]")
        lines.append(f"    key_points:")
        for kp in s["key_points"]:
            lines.append(f"      - \"{kp}\"")
        lines.append(f"    recall_prompts:")
        for rp in s["recall_prompts"]:
            lines.append(f"      - \"{rp}\"")

        # content 用 JSON quoted scalar（避免 yaml block scalar 對 ": " + 換行 的 key 誤判）
        import json
        content_json = json.dumps(s["content"], ensure_ascii=False)
        lines.append(f"    content: {content_json}")
    fp.write_text("\n".join(lines), encoding="utf-8")
    return fp


def write_index_yaml(index: dict) -> Path:
    """寫 _index.yaml 追蹤所有章節進度"""
    fp = SECTIONS_DIR / "_index.yaml"
    lines = [
        "# CSCS 章節 sections 清單（追蹤拆解進度）",
        "# 格式：chapter_id: {title_zh, source_file, sections_count, has_yaml, has_tags, has_key_points, has_recall_prompts}",
        "",
    ]
    for cid in sorted(index.keys()):
        info = index[cid]
        lines.append(f"{cid}:")
        lines.append(f"  title_zh: \"{info['title_zh']}\"")
        lines.append(f"  source_file: \"{info['source_file']}\"")
        lines.append(f"  sections_count: {info['sections_count']}")
        lines.append(f"  yaml_file: \"{info['yaml_file']}\"")
        lines.append(f"  has_tags: {str(info['has_tags']).lower()}")
        lines.append(f"  has_key_points: {str(info['has_key_points']).lower()}")
        lines.append(f"  has_recall_prompts: {str(info['has_recall_prompts']).lower()}")
        lines.append("")
    fp.write_text("\n".join(lines), encoding="utf-8")
    return fp


def load_topics_yaml() -> dict:
    """從 data/topics.yaml 讀 24 chapter 基本資料"""
    import yaml
    fp = ROOT / "data" / "topics.yaml"
    if not fp.exists():
        return {}
    return {t["id"]: t for t in yaml.safe_load(fp.read_text(encoding="utf-8")) if "id" in t}


def load_index_yaml() -> dict:
    """讀現有 _index.yaml"""
    import yaml
    fp = SECTIONS_DIR / "_index.yaml"
    if not fp.exists():
        return {}
    return yaml.safe_load(fp.read_text(encoding="utf-8")) or {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_id", nargs="?", help="ch01 / ch02 / ...")
    parser.add_argument("--all", action="store_true", help="一次拆全部 24 章（僅內容，不加 tags/key_points/recall_prompts）")
    parser.add_argument("--update-index", action="store_true", help="只更新 _index.yaml 不拆")
    args = parser.parse_args()

    topics = load_topics_yaml()
    index = load_index_yaml()

    if args.all or (not args.chapter_id and not args.update_index):
        # 一次拆全部
        chapter_ids = sorted(topics.keys()) if topics else [f"ch{i:02d}" for i in range(1, 25)]
    elif args.update_index:
        write_index_yaml(index)
        print(f"✓ wrote {SECTIONS_DIR / '_index.yaml'}")
        return 0
    else:
        chapter_ids = [args.chapter_id]

    for cid in chapter_ids:
        if cid not in topics:
            print(f"WARN: {cid} not in topics.yaml, skip")
            continue
        t = topics[cid]
        source = find_chapter_file(cid)
        if not source:
            print(f"WARN: {cid} source file not found in by_book/, skip")
            continue
        print(f"\n拆 {cid} ({t.get('title_zh', '')})")
        print(f"  source: {source.name}")
        content = source.read_text(encoding="utf-8")
        sections = split_by_headings(content)
        print(f"  sections: {len(sections)}")
        for s in sections:
            print(f"    - {s['title']} ({len(s['content'])} chars)")

        # 寫 yaml
        yaml_path = write_chapter_yaml(cid, source.name, t.get("title_zh", ""), sections)
        print(f"  ✓ wrote {yaml_path}")

        # 更新 index
        has_tags = any(s["tags"] for s in sections)
        has_kp = any(s["key_points"] for s in sections)
        has_rp = any(s["recall_prompts"] for s in sections)
        index[cid] = {
            "title_zh": t.get("title_zh", ""),
            "source_file": source.name,
            "sections_count": len(sections),
            "yaml_file": yaml_path.name,
            "has_tags": has_tags,
            "has_key_points": has_kp,
            "has_recall_prompts": has_rp,
        }

    write_index_yaml(index)
    print(f"\n✓ wrote {SECTIONS_DIR / '_index.yaml'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
