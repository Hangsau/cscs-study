#!/usr/bin/env python3
"""
annotate_section.py — 為 chapters 的 sections 加 tags / key_points / recall_prompts

為什麼需要這支：
- split_chapter.py 只切 sections 不加 metadata
- user 想用「回想」+「觀念命中」而不是預存題目
- key_points = 觀念命中點（考試最常出現）
- recall_prompts = 想 trigger 想回想的觸發問題

用法：
    python3 scripts/annotate_section.py ch01          # 套預設的 ch01 metadata
    python3 scripts/annotate_section.py ch03 --set custom.yaml  # 從 yaml 讀 metadata

格式（從 split_chapter.py 產的 yaml）：
    - id: "ch01-musculoskeletal-system"
      title: "..."
      tags: [tag1, tag2, ...]
      key_points:
        - "..."
      recall_prompts:
        - "..."

實作：
- 直接替換 yaml 中 `tags: []` / `key_points:` / `recall_prompts:` 區塊
- 不解析完整 yaml，避免重排格式（保留原文完整內容）
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SECTIONS_DIR = ROOT / "data" / "sections"


def annotate_ch01() -> dict[str, dict]:
    """ch01 示範 metadata：8 個 sections（5 H2 + 3 H3 sub of neuromuscular）"""
    return {
        "ch01-musculoskeletal-system": {
            "tags": ["anatomy", "skeleton", "bone", "muscle", "joint", "leverage"],
            "key_points": [
                "人體約 206 塊骨頭，分軸心骨骼（80）+ 附肢骨骼（126）",
                "肌肉只能 pull 不能 push，靠 bony lever 轉換成 push 動作",
                "骨骼在 heavy load + impact 訓練下密度增加（gymnasts 骨密度最高）",
                "三種關節：fibrous（不動）/ cartilaginous（微動）/ synovial（多動）",
                "synovial joint 特徵：hyaline cartilage + synovial fluid capsule",
                "關節分三類 by axis：uniaxial（elbow）/ biaxial（ankle, wrist）/ multiaxial（shoulder, hip）",
            ],
            "recall_prompts": [
                "人體有幾塊骨頭？軸心 vs 附肢各幾塊？",
                "為什麼肌肉只能 pull 但能做出 push 動作？",
                "fibrous / cartilaginous / synovial 三種關節差別？",
                "uniaxial / biaxial / multiaxial 各舉一個例子",
                "骨密度最高的人是哪類運動員？為什麼？",
            ],
        },
        "ch01-neuromuscular-system-activation-of-muscles": {
            "tags": ["anatomy", "muscle-contraction", "motor-unit", "action-potential"],
            "key_points": [
                "motor unit = 一個 motor neuron + 它控制的肌纖維（可能數百到數千條）",
                "動作電位從 motor neuron 經 axon 到達 neuromuscular junction (NMJ)",
                "NMJ 釋放 acetylcholine (ACh) 與 receptors 結合 → 肌纖維膜 depolarization",
                "sarcoplasmic reticulum 釋放 Ca²⁺ → crossbridge cycling 啟動",
                "動作完成後 ACh 被 acetylcholinesterase 分解，避免持續收縮",
            ],
            "recall_prompts": [
                "motor unit 定義？",
                "動作電位如何從神經傳到肌纖維？",
                "Ca²⁺ 的角色？",
                "acetylcholine 怎麼被清除？",
            ],
        },
        "ch01-neuromuscular-system-muscle-fiber-types": {
            "tags": ["muscle-fiber", "type-i", "type-ii", "slow-twitch", "fast-twitch"],
            "key_points": [
                "Type I：慢縮紅肌，耐力為主（有氧），myosin ATPase 慢但 oxidative capacity 高",
                "Type IIa：快縮紅白介面，兼具速度 + 耐力（oxidative + glycolytic）",
                "Type IIx：快縮白肌，爆發力（glycolytic），最易疲勞",
                "肌纖維比例由基因決定（平均 50% Type I + 25% IIa + 25% IIx）",
                "訓練可改變 IIa ↔ IIx 比例（但不會增加 Type I 數量）",
            ],
            "recall_prompts": [
                "Type I / IIa / IIx 三型差別？",
                "哪型肌纖維比例可以靠訓練改變？",
                "Type I 適合作什麼運動？Type IIx 呢？",
            ],
        },
        "ch01-neuromuscular-system-motor-unit-recruitment-patterns": {
            "tags": ["motor-unit", "recruitment", "size-principle", "rate-coding"],
            "key_points": [
                "size principle：低強度動員 Type I 小 motor unit，強度↑ 才動員 Type II 大 motor unit",
                "rate coding：增加 motor neuron firing rate（每秒 6-8 次 → 60+ 次）增加收縮力",
                "低速動作（slow twitch exercise）偏 Type I 動員，高速動作偏 Type II 動員",
                "訓練效果：長期訓練可改善 recruitment 效率（同一強度動員更少 unit）",
            ],
            "recall_prompts": [
                "size principle 是什麼？",
                "rate coding 怎麼運作？",
                "低速 vs 高速動作動員的肌纖維有何不同？",
            ],
        },
        "ch01-neuromuscular-system-proprioception": {
            "tags": ["proprioception", "golgi-tendon-organ", "muscle-spindle", "kinesthesis"],
            "key_points": [
                "proprioception = 不靠視覺就知道自己肢體位置的能力",
                "muscle spindle 偵測肌肉長度變化 → 反射收縮避免拉傷",
                "Golgi tendon organ (GTO) 偵測肌肉張力 → 過強時抑制收縮避免撕裂",
                "本體感覺對舉重 / 體操 / 球類技術動作至關重要",
                "訓練可強化 proprioception（單腳站立、閉眼平衡、震動訓練）",
            ],
            "recall_prompts": [
                "proprioception 定義？",
                "muscle spindle 和 GTO 差別？",
                "為什麼閉眼平衡訓練能強化本體感覺？",
            ],
        },
        "ch01-cardiovascular-system": {
            "tags": ["anatomy", "heart", "cardiovascular", "cardiac-output", "blood"],
            "key_points": [
                "心臟 4 腔：左右心房 + 左右心室，血液單向流動靠瓣膜",
                "cardiac output (Q) = HR × SV，心輸出量 ≈ 5 L/min 靜止",
                "心率限制因素：SA node 內在節律 (~100 bpm) + 副交感抑制（vagus）→ 靜止 70 bpm",
                "動靜脈氧差 (a-vO2 diff) = 動脈血氧 - 混合靜脈血氧，運動時增加",
                "VO2 max = Q × a-vO2 diff，是有氧能力的上限指標",
                "動脈血氧含量約 20 ml O2 / 100 ml blood（Hb 15 g/dL × 1.34 ml O2/g）",
            ],
            "recall_prompts": [
                "cardiac output 公式？靜止約多少？",
                "心率限制的兩個因素？",
                "a-vO2 diff 是什麼？運動時會增加還是減少？",
                "VO2 max 公式兩個因子？",
                "動脈血氧含量約多少 ml/100ml blood？",
            ],
        },
        "ch01-respiratory-system": {
            "tags": ["anatomy", "respiration", "ventilation", "gas-exchange", "lung"],
            "key_points": [
                "呼吸道 upper（鼻/咽/喉）vs lower（氣管/支氣管/肺）",
                "肺泡是 gas exchange 單位，表面積極大 (~70 m²)",
                "ventilation = tidal volume × respiratory rate，靜止約 6 L/min",
                "gas exchange 靠 diffusion（Fick's law）：面積↑、距離↓、分壓差↑ → diffusion↑",
                "O2 從肺泡到血液靠 partial pressure gradient（肺泡 PO2 ≈ 104 mmHg，血液進入肺泡前 PO2 = 40 mmHg）",
                "CO2 排出也靠 partial pressure（靜脈 PCO2 ≈ 46 mmHg，肺泡 PCO2 = 40 mmHg）",
            ],
            "recall_prompts": [
                "呼吸道 upper vs lower 各包含哪些？",
                "肺泡表面積極大約多少 m²？",
                "ventilation 公式？靜止約多少？",
                "Fick's law 三個影響 diffusion 的因素？",
                "肺泡 PO2 vs 靜脈血液 PO2 各約多少 mmHg？",
            ],
        },
        "ch01-conclusion": {
            "tags": ["summary", "integration", "training-application"],
            "key_points": [
                "CSCS 教練必須了解 musculoskeletal + neuromuscular + cardiovascular + respiratory 系統才能設計有效訓練",
                "骨骼肌收縮（neuromuscular）+ 能量供應（cardiovascular/respiratory 帶 O2 + 營養）= 運動表現",
                "理解這些系統才能：設計 progressive overload、解釋訓練適應、預測恢復時間、預防傷害",
                "後續章節會用到本章術語：ch03 bioenergetics 講能量系統、ch05/06 講訓練適應",
            ],
            "recall_prompts": [
                "為什麼 CSCS 教練必須了解這 4 個系統？",
                "運動表現的三個環節：收縮 + 能量 + 恢復的關係？",
                "本章哪 3 個術語會在後續章節出現？",
            ],
        },
    }


def replace_section_metadata(yaml_path: Path, metadata: dict[str, dict]) -> None:
    """讀 yaml，找到每個 section 的 tags/key_points/recall_prompts 空 list 並替換"""
    content = yaml_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    out_lines = []
    i = 0
    current_section_id = None

    while i < len(lines):
        line = lines[i]

        # 偵測 section 開始：- id: "ch01-xxx"
        m = re.match(r'^\s*- id:\s*"([^"]+)"', line)
        if m:
            current_section_id = m.group(1)
            out_lines.append(line)
            i += 1
            continue

        # 偵測空 tags: [] — 替換為有內容
        if current_section_id and current_section_id in metadata:
            md = metadata[current_section_id]

            if re.match(r"^\s*tags:\s*\[\]\s*$", line):
                tag_str = ", ".join(md["tags"])
                out_lines.append(line.replace("[]", f"[{tag_str}]"))
                i += 1
                continue

            if re.match(r"^\s*key_points:\s*$", line):
                # 把這行 + 替換為 list
                out_lines.append(line)
                for kp in md["key_points"]:
                    out_lines.append(f'      - "{_escape(kp)}"')
                i += 1
                continue

            if re.match(r"^\s*recall_prompts:\s*$", line):
                out_lines.append(line)
                for rp in md["recall_prompts"]:
                    out_lines.append(f'      - "{_escape(rp)}"')
                i += 1
                continue

        out_lines.append(line)
        i += 1

    yaml_path.write_text("\n".join(out_lines), encoding="utf-8")


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def update_index_after_annotation(chapter_id: str, has_tags: bool, has_kp: bool, has_rp: bool) -> None:
    """更新 _index.yaml 標記 tags/key_points/recall_prompts 完成"""
    index_path = SECTIONS_DIR / "_index.yaml"
    if not index_path.exists():
        return
    content = index_path.read_text(encoding="utf-8")
    # 找對應 chapter 區塊更新
    pattern = rf"({re.escape(chapter_id)}:\n(?:.*\n)*?  yaml_file: \"ch{chapter_id[2:]}\.yaml\"\n)  has_tags: \w+\n  has_key_points: \w+\n  has_recall_prompts: \w+\n"
    new_block = f"\\1  has_tags: {str(has_tags).lower()}\n  has_key_points: {str(has_kp).lower()}\n  has_recall_prompts: {str(has_rp).lower()}\n"
    content = re.sub(pattern, new_block, content, flags=re.MULTILINE)
    index_path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_id", help="ch01 / ch02 / ...")
    parser.add_argument("--set", help="從 yaml 讀 metadata（未實作，先用 hard-coded）")
    args = parser.parse_args()

    if args.chapter_id != "ch01":
        print(f"目前只有 ch01 預設 metadata。ch{args.chapter_id[2:]} 還沒寫。")
        return 1

    yaml_path = SECTIONS_DIR / f"{args.chapter_id}.yaml"
    if not yaml_path.exists():
        print(f"ERROR: {yaml_path} not found. 先跑 split_chapter.py {args.chapter_id}")
        return 1

    metadata = annotate_ch01()
    replace_section_metadata(yaml_path, metadata)

    # 更新 _index.yaml
    has_tags = True
    has_kp = True
    has_rp = True
    update_index_after_annotation(args.chapter_id, has_tags, has_kp, has_rp)

    # 統計
    total_tags = sum(len(m["tags"]) for m in metadata.values())
    total_kp = sum(len(m["key_points"]) for m in metadata.values())
    total_rp = sum(len(m["recall_prompts"]) for m in metadata.values())

    print(f"✓ annotated {args.chapter_id}")
    print(f"  sections: {len(metadata)}")
    print(f"  tags: {total_tags}")
    print(f"  key_points: {total_kp}")
    print(f"  recall_prompts: {total_rp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
