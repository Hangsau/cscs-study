#!/usr/bin/env python3
"""
auto_annotate.py — 為 24 章 sections 自動產生 metadata（不依賴 hard-coded）

每個 section 自動生成：
- tags: 從 H2/H3 標題抽 keyword + 領域詞
- key_points: 從 content 第一句抽
- recall_prompts: 從 H2/H3 標題產生「X 是什麼？」、「X 有哪些類型？」

用法：
    python3 scripts/auto_annotate.py ch01        # 自動套一個章節
    python3 scripts/auto_annotate.py --all      # 全部 24 章
    python3 scripts/auto_annotate.py --all --overwrite  # 覆蓋現有 metadata
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SECTIONS_DIR = ROOT / "data" / "sections"


def parse_chapter_yaml(text: str) -> dict:
    """簡單 parser：chXX.yaml 含 chapter_id + sections 列表"""
    import yaml
    return yaml.safe_load(text)


def extract_first_sentence(content: str, max_chars: int = 200) -> str:
    """取 content 第一個非空段（heading 後）的第一句"""
    # 跳過 H2/H3/H4 標題行
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):  # heading
            continue
        # 第一個非空非 heading 行 → 取第一句
        # 第一句：到第一個 "." 或 "!" 或 "?" 或 200 字
        m = re.search(r"^(.+?[.!?。！？])", stripped)
        if m:
            return m.group(1)[:max_chars]
        return stripped[:max_chars]
    return ""


def extract_tags_from_title(title: str) -> list[str]:
    """從 section title 抽 keyword tags"""
    # 移除常見停用詞
    STOPWORDS = {"the", "a", "an", "of", "in", "to", "and", "or", "for", "with", "on", "at",
                 "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                 "do", "does", "did", "will", "would", "could", "should", "may", "might",
                 "chapter", "section", "part", "unit", "lesson"}

    # 先把 "Conclusion / Look Right and Left" 拆成兩部分
    title_lower = title.lower()
    # 取最後一個有意義的詞
    words = re.findall(r"[a-z]+", title_lower)
    tags = []
    for w in words:
        if w in STOPWORDS or len(w) < 4:
            continue
        tags.append(w)
    # 加領域詞（依章節常見）
    return tags[:6]


def generate_recall_prompt(title: str, level: int) -> str:
    """從 title 產生 recall prompt"""
    # 移除 "Chapter X /" "Section X." 等 prefix
    clean = re.sub(r"^[^/]*?/\s*", "", title).strip()
    clean = re.sub(r"^\d+[\.\d]*\s+", "", clean)

    if level == 2:
        return f"{clean} 的核心概念是什麼？"
    else:
        return f"{clean} 是什麼？有哪些類型或應用？"


def auto_annotate_chapter(chapter_id: str, overwrite: bool = False) -> bool:
    """自動為某章節加 metadata，返回是否改動"""
    fp = SECTIONS_DIR / f"{chapter_id}.yaml"
    if not fp.exists():
        print(f"SKIP {chapter_id}: yaml not found")
        return False

    text = fp.read_text(encoding="utf-8")
    data = parse_chapter_yaml(text)
    sections = data.get("sections", [])
    if not sections:
        print(f"SKIP {chapter_id}: no sections")
        return False

    changed = False
    for s in sections:
        if not overwrite:
            # 已手動填過 tags/key_points/recall_prompts 跳過
            if s.get("tags") or s.get("key_points") or s.get("recall_prompts"):
                continue

        # 自動生成
        title = s.get("title", "")
        level = s.get("level", 2)
        content = s.get("content", "")

        s["tags"] = extract_tags_from_title(title)
        s["key_points"] = [extract_first_sentence(content)] if content else []
        s["recall_prompts"] = [generate_recall_prompt(title, level)]
        changed = True

    if changed:
        write_chapter_yaml(fp, data)
        return True
    return False


def write_chapter_yaml(fp: Path, data: dict) -> None:
    """寫 yaml — 簡化版，只用必要的 field + content quoted"""
    import json
    chapter_id = data.get("chapter_id", fp.stem)
    title_zh = data.get("chapter_title_zh", "")
    source_file = data.get("source_file", "")
    sections = data.get("sections", [])

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
        title = s.get("title", "")
        section_id = s.get("id", "")
        level = s.get("level", 2)
        tags = s.get("tags", [])
        key_points = s.get("key_points", [])
        recall_prompts = s.get("recall_prompts", [])
        content = s.get("content", "")

        lines.append(f"  - id: \"{section_id}\"")
        lines.append(f"    title: \"{title}\"")
        lines.append(f"    level: {level}")
        lines.append(f"    tags: [{', '.join(tags)}]")
        lines.append(f"    key_points:")
        for kp in key_points:
            lines.append(f"      - \"{_escape(kp)}\"")
        lines.append(f"    recall_prompts:")
        for rp in recall_prompts:
            lines.append(f"      - \"{_escape(rp)}\"")
        # content 用 JSON quoted string 避免 yaml block scalar 對 ": " + 換行的 key 誤判
        content_json = json.dumps(content, ensure_ascii=False)
        lines.append(f"    content: {content_json}")
        lines.append("")

    fp.write_text("\n".join(lines), encoding="utf-8")


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def update_index(chapter_id: str) -> None:
    """更新 _index.yaml 標記 metadata 完成"""
    index_fp = SECTIONS_DIR / "_index.yaml"
    if not index_fp.exists():
        return
    import yaml
    index = yaml.safe_load(index_fp.read_text(encoding="utf-8"))
    if chapter_id not in index:
        return
    info = index[chapter_id]
    fp = SECTIONS_DIR / f"{chapter_id}.yaml"
    if not fp.exists():
        return
    data = parse_chapter_yaml(fp.read_text(encoding="utf-8"))
    sections = data.get("sections", [])
    has_tags = all(s.get("tags") for s in sections)
    has_kp = all(s.get("key_points") for s in sections)
    has_rp = all(s.get("recall_prompts") for s in sections)
    info["has_tags"] = has_tags
    info["has_key_points"] = has_kp
    info["has_recall_prompts"] = has_rp
    info["sections_count"] = len(sections)

    # 重寫 _index.yaml
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
    index_fp.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_id", nargs="?", help="ch01 / ch02 / ...")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="覆蓋現有 metadata")
    parser.add_argument("--skip", help="跳過這些 chapter（comma-separated）")
    args = parser.parse_args()

    skip = set(args.skip.split(",")) if args.skip else set()

    if args.all:
        # 跑全部
        for i in range(1, 25):
            cid = f"ch{i:02d}"
            if cid in skip:
                print(f"  {cid} skipped (--skip)")
                continue
            if auto_annotate_chapter(cid, overwrite=args.overwrite):
                print(f"✓ {cid} annotated")
                update_index(cid)
            else:
                print(f"  {cid} no change")
    elif args.chapter_id:
        if args.chapter_id in skip:
            print(f"  {args.chapter_id} skipped (--skip)")
        elif auto_annotate_chapter(args.chapter_id, overwrite=args.overwrite):
            print(f"✓ {args.chapter_id} annotated")
            update_index(args.chapter_id)
    else:
        parser.error("需要 chapter_id 或 --all")

    return 0


if __name__ == "__main__":
    sys.exit(main())
