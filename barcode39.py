#!/usr/bin/env python3
"""barcode39 - 把文本编码成 Code 39 条形码的 ASCII 艺术图。

纯标准库,无第三方依赖。
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Code 39 标准字符表
#
# 每个字符由 9 个元素组成:5 条 bars + 4 个 spaces,交替排列,以 bar 开头。
# 9 个元素中恰好 3 个是宽的(wide),其余 6 个是窄的(narrow) —— 这就是
# "Code 39 / 3 of 9" 名字的由来。
#
# 表中每个字符记为 9 个字符的字符串,'n' = 窄,'w' = 宽,
# 偶数下标(0,2,4,6,8)是 bars,奇数下标(1,3,5,7)是 spaces。
#
# 本表依据公开规范:
#   - Wikipedia "Code 39" 词条的编码规则描述(两条宽 bars 的 2-of-5 编码,
#     宽 space 位置决定分组)与字符表
#   - ISO/IEC 16388:2023 (Code 39 的现行国际标准)
#   - 与 Scribus 的 code39.py 脚本中的字符表逐项交叉核对一致
#
# 分组规则:宽 space 的位置(1-4,从左数)决定字符分组:
#   位置 1 -> +30 组(U-Z)及 -, ., 空格, 起始/终止符
#   位置 2 -> +0 组(数字 1-9,0)
#   位置 3 -> +10 组(A-J)
#   位置 4 -> +20 组(K-T)
# $, /, +, % 四个字符比较特殊:5 条 bars 全窄,3 个宽 spaces + 1 个窄 space。
# ---------------------------------------------------------------------------

PATTERNS = {
    ' ': 'nwwnnnwnn',
    '$': 'nwnwnwnnn',
    '%': 'nnnwnwnwn',
    '*': 'nwnnwnwnn',
    '+': 'nwnnnwnwn',
    '-': 'nwnnnnwnw',
    '.': 'wwnnnnwnn',
    '/': 'nwnwnnnwn',
    '0': 'nnnwwnwnn',
    '1': 'wnnwnnnnw',
    '2': 'nnwwnnnnw',
    '3': 'wnwwnnnnn',
    '4': 'nnnwwnnnw',
    '5': 'wnnwwnnnn',
    '6': 'nnwwwnnnn',
    '7': 'nnnwnnwnw',
    '8': 'wnnwnnwnn',
    '9': 'nnwwnnwnn',
    'A': 'wnnnnwnnw',
    'B': 'nnwnnwnnw',
    'C': 'wnwnnwnnn',
    'D': 'nnnnwwnnw',
    'E': 'wnnnwwnnn',
    'F': 'nnwnwwnnn',
    'G': 'nnnnnwwnw',
    'H': 'wnnnnwwnn',
    'I': 'nnwnnwwnn',
    'J': 'nnnnwwwnn',
    'K': 'wnnnnnnww',
    'L': 'nnwnnnnww',
    'M': 'wnwnnnnwn',
    'N': 'nnnnwnnww',
    'O': 'wnnnwnnwn',
    'P': 'nnwnwnnwn',
    'Q': 'nnnnnnwww',
    'R': 'wnnnnnwwn',
    'S': 'nnwnnnwwn',
    'T': 'nnnnwnwwn',
    'U': 'wwnnnnnnw',
    'V': 'nwwnnnnnw',
    'W': 'wwwnnnnnn',
    'X': 'nwnnwnnnw',
    'Y': 'wwnnwnnnn',
    'Z': 'nwwnwnnnn',
}
"""44 个图案:43 个可编码字符 + 起始/终止符 '*'。"""

DATA_CHARS = frozenset(PATTERNS) - {'*'}
"""43 个可编码的数据字符(不含起始/终止符)。"""


def _check_table():
    """导入时自检:表结构必须符合 Code 39 规范。"""
    assert len(DATA_CHARS) == 43, "数据字符必须是 43 个"
    assert all(len(p) == 9 for p in PATTERNS.values()), "每个字符必须是 9 个元素"
    assert all(p.count('w') == 3 for p in PATTERNS.values()), "每字符恰好 3 个宽元素"
    assert len(set(PATTERNS.values())) == len(PATTERNS), "图案必须互不相同"


_check_table()


def validate(text):
    """检查文本是否可编码,返回规范化后的大写文本。

    小写字母会被拒绝(Code 39 只有大写),并给出中文提示。
    """
    if not text:
        raise ValueError("输入为空,请提供要编码的文本")
    bad = sorted({ch for ch in text if ch not in DATA_CHARS})
    if bad:
        lower = [ch for ch in bad if ch.islower()]
        hint = ""
        if lower:
            hint = " (Code 39 只支持大写字母,请把 %s 改成大写)" % "".join(
                ch.upper() for ch in lower
            )
        raise ValueError("不支持的字符: %s%s" % (" ".join(repr(c) for c in bad), hint))
    return text


def encode(text):
    """把文本编码成带起始/终止符的图案序列,元素之间用窄空隙分隔。"""
    text = validate(text)
    full = '*' + text + '*'
    return full, [PATTERNS[ch] for ch in full]


def render(text, height=3, ratio=3, show_text=True):
    """渲染 ASCII 条形码,返回字符串列表(每行等宽)。

    narrow bar 用 1 个 '█',wide bar 用 ratio 个 '█';
    narrow space 1 个空格,wide space ratio 个空格;字符间 1 个窄空隙。
    """
    if ratio < 2:
        raise ValueError("ratio 至少为 2")
    _, patterns = encode(text)
    bar_n, bar_w = '█', '█' * ratio
    sp_n, sp_w = ' ', ' ' * ratio
    line = []
    for i, pat in enumerate(patterns):
        for j, elt in enumerate(pat):
            is_bar = (j % 2 == 0)
            line.append((bar_w if elt == 'w' else bar_n) if is_bar else (sp_w if elt == 'w' else sp_n))
        if i < len(patterns) - 1:
            line.append(sp_n)  # 字符间窄空隙
    barcode = ''.join(line)
    rows = [barcode] * height
    if show_text:
        rows.append(text.center(len(barcode)))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='barcode39',
        description='把文本编码成 Code 39 条形码的 ASCII 艺术图(纯标准库)。',
    )
    parser.add_argument('text', nargs='?', help='要编码的文本(只支持 Code 39 的 43 个字符)')
    parser.add_argument('--height', type=int, default=3, help='条形码高度(行数),默认 3')
    parser.add_argument('--ratio', type=int, default=3, help='宽窄比(宽元素宽度),默认 3,至少 2')
    parser.add_argument('--no-text', action='store_true', help='不打印下方的人眼可读文本')
    args = parser.parse_args(argv)

    if args.text is None:
        parser.print_usage(sys.stderr)
        print("error: 请提供要编码的文本,例如: barcode39 \"HELLO-123\"", file=sys.stderr)
        return 2
    if args.height < 1:
        print("error: --height 至少为 1", file=sys.stderr)
        return 2
    try:
        rows = render(args.text, height=args.height, ratio=args.ratio,
                      show_text=not args.no_text)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    print('\n'.join(rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
