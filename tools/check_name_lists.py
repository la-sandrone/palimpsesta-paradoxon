#!/usr/bin/env python3
# 文件名: check_name_lists.py
# 摘要: 校验一个 Stellaris 名字包（name_lists + localisation）能不能用。
#       查的四项都是「坏了也不报错」的那类：旧编号语法、sequential_name 写法、
#       key 定义完整性、括号平衡。
# 依赖: 仅标准库
# 用法: python3 check_name_lists.py <mod 目录> [--langs english simp_chinese]
#
# 退出码: 0 = 四项全过   1 = 有失败项   2 = 参数/目录问题

import argparse
import os
import re
import sys

OLD_SYNTAX = re.compile(r"%[A-Z]+%")                 # %R% %O% %C% %HEX%
SEQ_REF = re.compile(r"sequential_name\s*=\s*([^\s}]+)")
LOC_LINE = re.compile(r"^\s+([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*\"(.*)\"\s*$")


def read(p):
    with open(p, encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def collect_lists(mod_dir):
    d = os.path.join(mod_dir, "common", "name_lists")
    if not os.path.isdir(d):
        return {}
    return {n: read(os.path.join(d, n)) for n in sorted(os.listdir(d)) if n.endswith(".txt")}


def collect_loc(mod_dir, langs):
    out = {}
    for lang in langs:
        d = os.path.join(mod_dir, "localisation", lang)
        table = {}
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                if n.endswith(".yml"):
                    for ln in read(os.path.join(d, n)).split("\n"):
                        m = LOC_LINE.match(ln.rstrip())
                        if m:
                            table[m.group(1)] = m.group(2)
        out[lang] = table
    return out


def brace_balance(text):
    return text.count("{"), text.count("}")


def main():
    ap = argparse.ArgumentParser(
        prog="check_name_lists.py",
        description="校验 Stellaris 名字包的四项「静默失效」风险",
        epilog="背景见仓库根目录 07-名字表与名字包.md",
    )
    ap.add_argument("mod", help="mod 目录（含 common/name_lists 与 localisation/）")
    ap.add_argument("--langs", nargs="+", default=["english", "simp_chinese"],
                    help="必须都有定义的语种（默认 english simp_chinese）")
    args = ap.parse_args()

    if not os.path.isdir(args.mod):
        raise SystemExit("目录不存在: %s" % args.mod)

    lists = collect_lists(args.mod)
    if not lists:
        raise SystemExit("没找到 common/name_lists/*.txt —— 也可能内容锁在 .zip 里（引擎不解压）")

    loc = collect_loc(args.mod, args.langs)
    fail = 0

    # ① 旧编号语法残留
    old = {n: OLD_SYNTAX.findall(t) for n, t in lists.items()}
    old = {n: v for n, v in old.items() if v}
    print("[1] 旧编号语法 %%X%% 残留: %s" % ("0 处" if not old else "命中"))
    for n, v in old.items():
        print("    %-24s %s" % (n, sorted(set(v))))
    fail += bool(old)

    # ② sequential_name 必须是裸 key
    quoted = []
    refs = {}
    for n, t in lists.items():
        for raw in SEQ_REF.findall(t):
            v = raw.strip()
            if v.startswith('"') or v.startswith("'"):
                quoted.append((n, v))
            else:
                refs.setdefault(n, set()).add(v.strip('"').strip())
    print("[2] sequential_name 带引号: %d 处%s" % (
        len(quoted), "" if not quoted else "  <- 必须是裸 key"))
    for n, v in quoted[:6]:
        print("    %-24s %s" % (n, v))
    fail += bool(quoted)

    # ③ key 定义完整性
    all_refs = set()
    for s in refs.values():
        all_refs |= s
    print("[3] 引用 key 共 %d 个；语种: %s" % (len(all_refs), " ".join(args.langs)))
    for lang in args.langs:
        miss = sorted(k for k in all_refs if k not in loc[lang])
        status = "缺失 0" if not miss else "缺失 %d" % len(miss)
        print("    %-14s %s%s" % (lang, status, "" if not miss else "  <- 会直接把 key 名显示到界面上"))
        for k in miss[:8]:
            print("        - %s" % k)
        fail += bool(miss)

    # ④ 括号平衡
    bad_brace = []
    for n, t in lists.items():
        o, c = brace_balance(t)
        if o != c:
            bad_brace.append((n, o, c))
    print("[4] 括号平衡: %s" % ("全部 OK" if not bad_brace else "不平衡 %d 个文件" % len(bad_brace)))
    for n, o, c in bad_brace:
        print("    %-24s { = %d, } = %d" % (n, o, c))
    fail += bool(bad_brace)

    print("-" * 60)
    print("结论：%s" % ("四项全过" if not fail else "%d 项有问题（都不会报错，只会静默失效）" % fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
