#!/usr/bin/env python3
"""Check explicit shot headings and their following action ranges, not video quality."""
import argparse
import json
import re
from pathlib import Path

RANGE = re.compile(r"^\s*【(\d+(?:\.\d+)?)\s*[—–\-~～至]\s*(\d+(?:\.\d+)?)秒】")
SHOT = re.compile(r"^\s*镜头\s*(\d+)\s*[:：]\s*(.*)$")
FACE = re.compile(r"(?:脸部|面部|头像).*(?:近景|特写)|(?:近景|特写).*(?:脸部|面部)")
EPS = 1e-6


def analyse(text, duration=30, opening_min_shots=4):
    errors, warnings, ranges, shots = [], [], [], []
    if "【时间线】" not in text or "【BGM】" not in text:
        return {"ok": False, "errors": ["缺少时间线或BGM段"], "warnings": [], "shots": []}
    timeline = text.split("【时间线】", 1)[1].split("【BGM】", 1)[0]
    current = None
    for line in timeline.splitlines():
        heading = SHOT.match(line)
        if heading:
            current = {"number": int(heading[1]), "camera": heading[2], "start": None, "end": None}
            shots.append(current)
            continue
        match = RANGE.match(line)
        if not match:
            continue
        start, end = map(float, match.groups())
        ranges.append((start, end))
        if end <= start:
            errors.append(f"动作段{start:g}—{end:g}非正时长")
        if current is None:
            errors.append(f"动作段{start:g}—{end:g}之前没有镜头标题")
        else:
            if current["start"] is None:
                current["start"] = start
            current["end"] = end
    if not ranges:
        errors.append("没有可识别的动作时间段；使用【0—2秒】格式")
    else:
        if abs(ranges[0][0]) > EPS:
            errors.append("时间线未从0秒开始")
        for (_, previous_end), (start, _) in zip(ranges, ranges[1:]):
            if abs(previous_end - start) > EPS:
                errors.append(f"时间线在{previous_end:g}→{start:g}处有缺口或重叠")
        if abs(ranges[-1][1] - duration) > EPS:
            errors.append(f"时间线未结束于{duration:g}秒")
    if not shots:
        errors.append("没有明确的镜头N：标题，不能核验镜长")
    durations = []
    for expected, shot in enumerate(shots, 1):
        if shot["number"] != expected:
            errors.append(f"镜头编号不连续：应为{expected}，实际{shot['number']}")
        if shot["start"] is None:
            errors.append(f"镜头{shot['number']}没有动作时段")
            continue
        length = shot["end"] - shot["start"]
        shot["seconds"] = round(length, 4)
        durations.append(length)
        if length > 4 + EPS:
            errors.append(f"镜头{shot['number']}长{length:g}秒，超过4秒")
        if FACE.search(shot["camera"]) and length > 2 + EPS:
            errors.append(f"镜头{shot['number']}脸部近景长{length:g}秒，超过2秒")
        if length < 0.8 - EPS:
            warnings.append(f"镜头{shot['number']}短于0.8秒，人工核对是否无依据碎切")
    opening_count = sum(shot["start"] is not None and shot["start"] < min(10, duration) - EPS for shot in shots)
    if opening_count < opening_min_shots:
        errors.append(f"前10秒仅{opening_count}镜，少于默认{opening_min_shots}镜")
    return {
        "ok": not errors, "errors": errors, "warnings": warnings,
        "action_segments": len(ranges), "shot_count": len(shots),
        "opening_shot_count": opening_count, "max_shot_seconds": round(max(durations), 4) if durations else None,
        "shots": shots,
        "manual_review_required": ["前10秒机位/景别与主运镜多样性", "源舞动作/节拍/幅度及衔接", "单次wink", "背景空间布局与切点光色连续", "生成成片实际镜长与效果"]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", type=Path)
    parser.add_argument("--duration", type=float, default=30)
    parser.add_argument("--opening-min-shots", type=int, default=4)
    args = parser.parse_args()
    if args.duration <= 0 or args.opening_min_shots < 0:
        parser.error("时长必须为正数，镜头下限不能为负数")
    result = analyse(args.prompt.read_text(encoding="utf-8"), args.duration, args.opening_min_shots)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
