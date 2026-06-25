#!/usr/bin/env python3
"""
verify_sections.py — 驗證自動拆 sections 對齊 NSCA 原書 H2/H3

用途：對照 by_book/ 章節的 H2/H3 結構跟 data/sections/chXX.yaml 的 sections list
確認切分正確。

    python3 scripts/verify_sections.py ch01
    python3 scripts/verify_sections.py --all

輸出：
- 比對 by_book/ 的 H2 標題 vs yaml 內 section title
- 列出對齊 / 不對齊
- 統計 sections 數量、size 分佈
"""

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
BY_BOOK = ROOT / "by_book"
SECTIONS_DIR = ROOT / "data" / "sections"


def get_h2_from_source(source_path: Path) -> list[str]:
    """從 by_book/chXX.md 抓所有 H2 標題"""
    content = source_path.read_text(encoding="utf-8")
    return [m.group(1).strip() for m in re.finditer(r"^## (.+)$", content, re.MULTILINE)]


def get_h3_from_source(source_path: Path) -> list[str]:
    """從 by_book/chXX.md 抓所有 H3 標題（給 reference）"""
    content = source_path.read_text(encoding="utf-8")
    return [m.group(1).strip() for m in re.finditer(r"^### (.+)$", content, re.MULTILINE)]


def find_source_file(chapter_id: str) -> Path | None:
    num = chapter_id.replace("ch", "").zfill(2)
    pattern = f"_ch{num}_"
    for f in BY_BOOK.iterdir() if BY_BOOK.exists() else []:
        if pattern in f.name and f.suffix == ".md":
            return f
    return None


def get_yaml_section_titles(yaml_path: Path) -> list[str]:
    """從 data/sections/chXX.yaml 抓所有 section title"""
    content = yaml_path.read_text(encoding="utf-8")
    titles = []
    for m in re.finditer(r'^\s*- id: "[^"]+"\s*\n\s*title: "([^"]+)"', content, re.MULTILINE):
        titles.append(m.group(1))
    return titles


def main() -> int:
    import yaml
    index_path = SECTIONS_DIR / "_index.yaml"
    if not index_path.exists():
        print(f"ERROR: {index_path} not found")
        return 1
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))

    chapter_ids = sorted(index.keys())
    print(f"驗證 {len(chapter_ids)} 章 sections 對齊 NSCA 原書 H2 結構\n")
    print(f"{'Chapter':<8} {'YAML sections':<14} {'Source H2':<12} {'Source H3':<12} {'Avg size':<10} {'Max size':<10} {'對齊？':<6}")
    print("-" * 80)

    for cid in chapter_ids:
        yaml_path = SECTIONS_DIR / f"{cid}.yaml"
        if not yaml_path.exists():
            print(f"{cid:<8} ❌ yaml not found")
            continue

        source = find_source_file(cid)
        if not source:
            print(f"{cid:<8} ❌ source file not found")
            continue

        h2_list = get_h2_from_source(source)
        h3_list = get_h3_from_source(source)
        yaml_titles = get_yaml_section_titles(yaml_path)

        # 統計 yaml section size
        content = yaml_path.read_text(encoding="utf-8")
        section_sizes = [int(m.group(1)) for m in re.finditer(r"chars\)\s*$", content, re.MULTILINE)]
        avg_size = sum(section_sizes) / len(section_sizes) if section_sizes else 0
        max_size = max(section_sizes) if section_sizes else 0

        # 對齊檢查：每個 H2 應該對應到 yaml section title（前面部分 match）
        aligned = 0
        for h2 in h2_list:
            if any(h2 in yt for yt in yaml_titles):
                aligned += 1

        alignment_status = "✓" if aligned == len(h2_list) else f"⚠ {aligned}/{len(h2_list)}"

        print(f"{cid:<8} {len(yaml_titles):<14} {len(h2_list):<12} {len(h3_list):<12} {avg_size:<10.0f} {max_size:<10} {alignment_status:<6}")

    print("\n說明：")
    print("  YAML sections: yaml 內 section 總數")
    print("  Source H2: by_book/ 章節原始 H2 數")
    print("  Source H3: by_book/ 章節原始 H3 數（reference，不計入）")
    print("  對齊 ✓：每個 H2 都能在 yaml section title 找到")
    print("  對齊 ⚠：部分 H2 沒對應（可能是 Key Terms/Study Questions 被排除）")
    print()
    print("如何人工驗證：")
    print("  1. 抽 1-2 章（如 ch01、ch15）")
    print("  2. 用 VSCode / vim 開 by_book/chXX.md 對照 data/sections/chXX.yaml")
    print("  3. 確認每個 H2 段落內容完整、title 對齊、沒漏字")
    print("  4. 如果發現錯，在 data/sections/chXX.yaml 修，或給 split_chapter.py 加規則重跑")
    return 0


if __name__ == "__main__":
    sys.exit(main())
