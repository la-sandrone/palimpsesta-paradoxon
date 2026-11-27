#!/usr/bin/env python3
# 文件名: diff_symbol_docs.py
# 摘要: 比对两次 script_documentation 导出，判定差异属于哪一类：
#       「逐字节相同」/「只有顺序变了」/「内容真的变了」。
#       顺序不稳定是 P 社导出的正常现象（见 05-符号表导出.md §4.4），
#       按行 diff 会把小事报成灾难，所以这里按集合比。
# 依赖: 同目录的 parse_script_docs.py（仅标准库）
# 用法: python3 diff_symbol_docs.py <目录A> <目录B> [--game ck3|stellaris] [-v]
#
# 退出码: 0 = 全部一致（含「只有顺序不同」）  1 = 存在内容差异  2 = 参数/目录错误

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse_script_docs as psd


def key_of(sym):
    """条目身份 + 内容的指纹。顺序不参与。"""
    return (
        sym.get("name", ""),
        tuple(sym.get("scopes") or []),
        tuple(sym.get("targets") or []),
        sym.get("traits", ""),
        sym.get("doc", ""),
        json.dumps(sym.get("props") or {}, sort_keys=True, ensure_ascii=False),
    )


def load(d, game):
    parsed = psd.parse_ck3(d) if game == "ck3" else psd.parse_stellaris(d)
    out = {}
    for fname, syms in parsed.items():
        out[fname] = [key_of(s) for s in syms]
    return out


def compare(a, b):
    """返回 (状态, 明细)"""
    if a == b:
        return "相同（含顺序）", {}
    if sorted(a) == sorted(b):
        # 同多重集合：只有顺序不同
        return "仅顺序不同", {}
    sa, sb = set(a), set(b)
    only_b = sorted(sb - sa)
    only_a = sorted(sa - sb)
    return "内容不同", {"新增": only_b, "消失": only_a}


def main():
    ap = argparse.ArgumentParser(
        prog="diff_symbol_docs.py",
        description="比对两次 script_documentation 导出（按集合，不按行）",
        epilog="顺序不稳定是正常现象；详见 05-符号表导出.md §4.4",
    )
    ap.add_argument("a", help="旧导出目录")
    ap.add_argument("b", help="新导出目录")
    ap.add_argument("--game", choices=("ck3", "stellaris"), help="强制指定游戏；默认自动识别")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印差异条目名（最多各 20 条）")
    args = ap.parse_args()

    for d in (args.a, args.b):
        if not os.path.isdir(d):
            raise SystemExit("目录不存在: %s" % d)

    game = args.game or psd.detect_game(args.a)
    da, db = load(args.a, game), load(args.b, game)

    files = sorted(set(da) | set(db))
    worst = 0
    print("%-26s %8s %8s  %s" % ("file", "A", "B", "结论"))
    print("-" * 72)
    for f in files:
        if f not in da or f not in db:
            # 变体目录可能只存差异文件（见 符号表/README.md 第 5 条），不算内容差异
            print("%-26s %8s %8s  仅一侧存在（跳过）" % (f, len(da.get(f, [])), len(db.get(f, []))))
            continue
        a, b = da.get(f, []), db.get(f, [])
        state, detail = compare(a, b)
        print("%-26s %8d %8d  %s" % (f, len(a), len(b), state))
        if state == "内容不同":
            worst = 1
            print("      新增 %d / 消失 %d" % (len(detail["新增"]), len(detail["消失"])))
            if args.verbose:
                for k in detail["新增"][:20]:
                    print("      + %s" % k[0])
                for k in detail["消失"][:20]:
                    print("      - %s" % k[0])
    print("-" * 72)
    print("结论：%s" % ("存在内容差异" if worst else "无内容差异（顺序差异不算）"))
    return worst


if __name__ == "__main__":
    sys.exit(main())
