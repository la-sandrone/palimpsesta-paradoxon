#!/usr/bin/env python3
# 文件名: determinism_check.py
# 摘要: 判断两次导出「是否可复现」——逐文件比较原始字节，
#       并把「首行日志前缀」这种每次运行都变的东西单独剥掉再比。
#       目的：区分「顺序不稳定」（正常）与「内容不稳定」（要警惕）。
# 依赖: 仅标准库
# 用法: python3 determinism_check.py <目录A> <目录B> [-q]
#
# 判据（每文件三档）:
#   原始相同        字节完全一致
#   仅首行不同      剥掉首行后一致（首行是时间戳，每次都变）
#   **正文不同**    剩下还有差异 -> 该文件不可复现
#
# 退出码: 0 = 没有正文差异   1 = 存在正文差异   2 = 参数/目录错误

import argparse
import hashlib
import os
import re
import sys

LOG_PREFIX = re.compile(rb"^\[\d{2}:\d{2}:\d{2}\]\[[^\]]*\]:[ \t]*\r?\n")


def read(p):
    with open(p, "rb") as f:
        return f.read()


def strip_first_timestamp(raw):
    """只剥「首行是日志前缀」的情况；CK3 的首行是标题行，不能剥。"""
    return LOG_PREFIX.sub(b"", raw, count=1)


def h(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(
        prog="determinism_check.py",
        description="判断两次 script_documentation 导出是否可复现（剥掉首行时间戳再比）",
        epilog="顺序不稳定的说明见 05-符号表导出.md §4.4",
    )
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("-q", "--quiet", action="store_true", help="只打印结论行")
    args = ap.parse_args()

    for d in (args.a, args.b):
        if not os.path.isdir(d):
            raise SystemExit("目录不存在: %s" % d)

    files = sorted(
        f for f in set(os.listdir(args.a)) & set(os.listdir(args.b))
        if f.endswith(".log")
    )
    if not files:
        raise SystemExit("两个目录里没有同名 .log 文件可比较")

    bad = 0
    for f in files:
        ra, rb = read(os.path.join(args.a, f)), read(os.path.join(args.b, f))
        if ra == rb:
            print("%-22s 原始相同            %s" % (f, h(ra)))
            continue
        sa, sb = strip_first_timestamp(ra), strip_first_timestamp(rb)
        if sa == sb:
            print("%-22s 仅首行不同          %s -> %s" % (f, h(ra), h(rb)))
            continue
        bad += 1
        la, lb = sa.count(b"\n"), sb.count(b"\n")
        print("%-22s **正文不同**        %s -> %s  行数 %d -> %d" % (f, h(sa), h(sb), la, lb))

    print("-" * 66)
    if bad:
        print("结论：%d 个文件正文不可复现 —— 这些文件的字节不能当基准" % bad)
        if not args.quiet:
            print("下一步：用 diff_symbol_docs.py 按集合比，判断是「仅顺序」还是「内容真变」")
    else:
        print("结论：全部可复现（顺序差异不算 —— 那是运行时决定的，见 05 章 §4.4）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
