#!/usr/bin/env python3
# 文件名: parse_script_docs.py
# 摘要: 把 Paradox 游戏自己导出的 script_documentation 解析成 symbols-<game>.json。
#       名字、文档、作用域全部来自游戏自己打印的表，不经过二手转述。
# 依赖: 仅标准库（argparse / json / os / re / sys）
# 用法: python3 parse_script_docs.py [导出目录] [--game ck3|stellaris] [-o 输出.json]
#
# 支持的两种导出格式（自动识别）：
#   CK3        —— 7 个文件，块用 ---------- 分隔
#   Stellaris  —— 5 个文件，块用空行分隔、首行是日志前缀、CRLF
#
# 识别依据：CK3 有 event_targets.log；Stellaris 有 scopes.log 而无 event_targets.log。
# 导出方法见仓库根目录 05-符号表导出.md。

import argparse
import json
import os
import re
import sys

# ---------------- 通用 ----------------

# CK3 的块分隔线
SEP = re.compile(r"^-{10,}\s*$")

# Stellaris 每个文件第 1 行是日志前缀，如 [17:27:06][game_application.cpp:1419]:
LOG_PREFIX = re.compile(r"^\[\d{2}:\d{2}:\d{2}\]\[[^\]]*\]:\s?$")
# 任何以 [HH:MM:SS] 开头的行都当噪音丢掉
ANY_LOG_PREFIX = re.compile(r"^\[\d{2}:\d{2}:\d{2}\]")
# 小节标题，如 == TRIGGER DOCUMENTATION ==
SECTION_HEADER = re.compile(r"^==+\s*.*\s*==+$")

FORMAT_A = re.compile(r"^([a-z0-9_]+)\s+-\s+(.*)$")
FORMAT_B = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")
KV = re.compile(r"^([A-Za-z][A-Za-z0-9 _/]*):\s*(.*)$")
NAME_ONLY = re.compile(r"^[A-Za-z0-9_]+:\s*$")

# Stellaris 的条目起始行：name - 文档
SX_ENTRY = re.compile(r"^([a-z0-9_]+)\s+-\s+(.*)$")
# Stellaris modifiers 的单行条目：- 名字, Category: 类别
SX_MODIFIER = re.compile(r"^-\s+([A-Za-z0-9_]+)\s*,\s*Category:\s*(.*)$")
# Stellaris localizations 的分节：--Base Scope--
SX_LOC_SECTION = re.compile(r"^--(.+)--$")

CK3_FILES = {
    "triggers.log": "trigger",
    "effects.log": "effect",
    "event_targets.log": "event_target",
    "on_actions.log": "on_action",
    "event_scopes.log": "event_scope",
    "modifiers.log": "modifier",
    "custom_localization.log": "custom_localization",
}

SX_FILES = {
    "triggers.log": "trigger",
    "effects.log": "effect",
    "scopes.log": "scope",
    "modifiers.log": "modifier",
    "localizations.log": "loc_command",
}


def read_text(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def detect_game(src):
    """按文件指纹判断是哪款游戏的导出。"""
    has = lambda n: os.path.exists(os.path.join(src, n))
    if has("event_targets.log") or has("on_actions.log"):
        return "ck3"
    if has("scopes.log") and has("triggers.log"):
        return "stellaris"
    raise SystemExit("无法识别 %s 属于哪个游戏（既没有 event_targets.log 也没有 scopes.log）" % src)


def split_list(v):
    """作用域列表的分隔符两款游戏不同：
    CK3 用逗号（\"character, landed_title\"），Stellaris 用空格
    （\"spy_network espionage_operation agreement situation\"）。
    统一按「逗号或空白」切，两者都能吃。"""
    v = (v or "").strip()
    if v.lower() in ("none", "", "no"):
        return []
    return [x for x in re.split(r"[,\s]+", v) if x]


# ---------------- CK3 ----------------

def split_blocks(path):
    """优先按 ---------- 切；若文件没有分隔线（event_scopes / modifiers），
    改按「独占一行的 name:」二次切分。"""
    raw = read_text(path)
    lines = raw.split("\n")
    blocks, cur = [], []
    for ln in lines:
        if SEP.match(ln):
            if cur:
                blocks.append(cur)
            cur = []
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    if "Printing Modifier Definitions" in raw[:400]:
        blocks, cur = [], []
        for ln in lines:
            if ln.startswith("Tag:") and cur:
                blocks.append(cur)
                cur = [ln]
            else:
                cur.append(ln)
        if cur:
            blocks.append(cur)
        return blocks

    if len(blocks) <= 1:
        blocks, cur = [], []
        for ln in lines:
            if NAME_ONLY.match(ln) and cur:
                blocks.append(cur)
                cur = [ln]
            else:
                cur.append(ln)
        if cur:
            blocks.append(cur)
    return blocks


def parse_block(block):
    body = [l.rstrip() for l in block if l.strip()]
    if not body:
        return None

    first = body[0]
    m = FORMAT_A.match(first)
    if m and " - " in first:
        name, doc = m.group(1), m.group(2)
        scopes, targets, traits = [], [], []
        for ln in body[1:]:
            if ln.startswith("Supported Scopes:"):
                scopes = split_list(ln.split(":", 1)[1])
            elif ln.startswith("Supported Targets:"):
                targets = split_list(ln.split(":", 1)[1])
            elif ln.startswith("Traits:"):
                traits.append(ln.split(":", 1)[1].strip())
            else:
                doc += " " + ln.strip()
        return {"name": name, "doc": doc.strip(), "scopes": scopes,
                "targets": targets, "traits": "; ".join(traits), "props": {}}

    if first.startswith("Tag:"):
        tag = first.split(":", 1)[1].strip()
        props = {}
        for ln in body[1:]:
            kv = KV.match(ln)
            if kv:
                props[kv.group(1).strip()] = kv.group(2).strip()
        areas = split_list(props.get("Use areas", ""))
        return {"name": tag, "doc": "", "scopes": areas, "targets": [],
                "traits": "", "props": props}

    m = FORMAT_B.match(first)
    if m:
        name = m.group(1)
        props = {}
        if m.group(2).strip():
            props["_"] = m.group(2).strip()
        for ln in body[1:]:
            kv = KV.match(ln)
            if kv:
                props[kv.group(1).strip()] = kv.group(2).strip()
        return {"name": name, "doc": props.pop("_", ""), "scopes": [],
                "targets": [], "traits": "", "props": props}
    return None


def parse_ck3(src):
    out = {}
    for fname, kind in CK3_FILES.items():
        path = os.path.join(src, fname)
        if not os.path.exists(path):
            continue
        got = [s for s in (parse_block(b) for b in split_blocks(path)) if s]
        for s in got:
            s["kind"] = kind
        out[fname] = got
    return out


# ---------------- Stellaris ----------------

def strip_sx_noise(text):
    """去掉 UTF-8 BOM、首行日志前缀、== 小节标题、CR。
    首行前缀必须剥：它是唯一每次运行都变的内容，留着会污染解析与 diff。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    for i, ln in enumerate(lines):
        if i == 0 and LOG_PREFIX.match(ln):
            continue
        if ANY_LOG_PREFIX.match(ln):
            continue
        if SECTION_HEADER.match(ln):
            continue
        out.append(ln)
    return out


def split_blank_blocks(lines):
    """按空行切块，再把「不以 name - 开头」的块并回上一块。
    Stellaris 没有 ---------- 分隔线，且用法示例可能跨行。"""
    blocks, cur = [], []
    for ln in lines:
        if not ln.strip():
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    merged = []
    for b in blocks:
        if merged and not SX_ENTRY.match(b[0]):
            merged[-1].extend(b)
        else:
            merged.append(list(b))
    return merged


def parse_sx_block(block):
    body = [l.rstrip() for l in block if l.strip()]
    if not body:
        return None
    m = SX_ENTRY.match(body[0])
    if not m:
        return None  # 文件头部的说明段落，不是条目

    name, doc = m.group(1), m.group(2).strip()
    scopes, targets, usage, props = [], [], [], {}

    for ln in body[1:]:
        s = ln.strip()
        if s.startswith("Supported Scopes:"):
            scopes = split_list(s.split(":", 1)[1])
        elif s.startswith("Supported Targets:"):
            targets = split_list(s.split(":", 1)[1])
        elif s.startswith("Output Scope:"):
            props["Output Scope"] = s.split(":", 1)[1].strip()
        elif re.match(r"^[A-Za-z][A-Za-z0-9 _/-]*:", s) and not usage:
            props[s.split(":", 1)[0].strip()] = s.split(":", 1)[1].strip()
        else:
            usage.append(s)

    return {"name": name, "doc": doc, "scopes": scopes, "targets": targets,
            "traits": "", "props": props, "usage": "\n".join(usage)}


def parse_sx_modifiers(lines):
    """modifiers.log 不是块结构：一行一条 —— '- 名字, Category: 类别'。"""
    got = []
    for ln in lines:
        m = SX_MODIFIER.match(ln.strip())
        if not m:
            continue
        got.append({"name": m.group(1), "doc": "", "scopes": [], "targets": [],
                    "traits": "", "props": {"Category": m.group(2).strip()},
                    "usage": ""})
    return got


def parse_sx_localizations(lines):
    """localizations.log 是分节清单，不是 name - 文档 结构。
    按 '--分节--' 切，节内缩进行视为命令，'Foo:' 行视为分组标题。"""
    got = []
    section = ""
    group = ""
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        sm = SX_LOC_SECTION.match(s.strip())
        if sm:
            section, group = sm.group(1).strip(), ""
            continue
        if not s.startswith(" "):
            # 顶格的 'Promotions:' / 'Properties' 之类是分组标题
            group = s.strip().rstrip(":")
            continue
        token = s.strip()
        if not token:
            continue
        got.append({"name": token, "doc": "", "scopes": [], "targets": [],
                    "traits": "", "props": {"Section": section, "Group": group},
                    "usage": ""})
    return got


def parse_stellaris(src):
    out = {}
    for fname, kind in SX_FILES.items():
        path = os.path.join(src, fname)
        if not os.path.exists(path):
            continue
        lines = strip_sx_noise(read_text(path))

        if fname == "modifiers.log":
            got = parse_sx_modifiers(lines)
        elif fname == "localizations.log":
            got = parse_sx_localizations(lines)
        else:
            got = [s for s in (parse_sx_block(b) for b in split_blank_blocks(lines)) if s]

        for s in got:
            s["kind"] = kind
        out[fname] = got
    return out


# ---------------- 入口 ----------------

def main():
    here = os.path.dirname(os.path.abspath(__file__))

    ap = argparse.ArgumentParser(
        prog="parse_script_docs.py",
        description="把 Paradox 游戏导出的 script_documentation 解析成 symbols-<game>.json",
        epilog="导出方法见仓库根目录 05-符号表导出.md",
    )
    ap.add_argument("src", nargs="?",
                    default=os.path.join(here, "script-docs", "ck3-1.20.1"),
                    help="script_documentation 目录（默认: 脚本旁的 script-docs/ck3-1.20.1）")
    ap.add_argument("--game", choices=("ck3", "stellaris"),
                    help="强制指定游戏；默认按文件名指纹自动识别")
    ap.add_argument("-o", "--out",
                    help="输出 JSON 路径（默认: 脚本同目录 symbols-<game>.json，写不出时请用本选项）")
    a = ap.parse_args()

    src = a.src
    if not os.path.isdir(src):
        raise SystemExit("目录不存在: %s（先用游戏导出一次，见 05-符号表导出.md）" % src)

    game = a.game or detect_game(src)
    parsed = parse_ck3(src) if game == "ck3" else parse_stellaris(src)

    out = {
        "source_kind": "script_documentation（游戏自动导出）",
        "game": game,
        "source_dir": os.path.abspath(src),
        "files": {},
        "symbols": [],
    }
    total = 0
    for fname, got in parsed.items():
        out["files"][fname] = len(got)
        out["symbols"].extend(got)
        total += len(got)
        print("  %-24s %6d" % (fname, len(got)))
    out["total"] = total

    dst = a.out or os.path.join(here, "symbols-%s.json" % game)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("合计 %d 条 -> %s" % (total, dst))


if __name__ == "__main__":
    main()
