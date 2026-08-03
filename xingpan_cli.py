#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""占星星盘 CLI"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.xingpan import compute_xingpan, to_markdown


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print("用法: python xingpan_cli.py <年> <月> <日> <时:分> [出生地] [--json] [--output path]")
        print("示例: python xingpan_cli.py 1989 6 28 5:30 林州")
        print("      python xingpan_cli.py 1990 3 15 8:00 女 北京 --json")
        sys.exit(0)

    json_mode = '--json' in args
    output_file = None
    for i, a in enumerate(args):
        if a == '--output' and i + 1 < len(args):
            output_file = args[i + 1]
            break

    positional = [a for a in args if not a.startswith('--')]
    if len(positional) < 4:
        print("错误: 至少需要年月日时。示例: python xingpan_cli.py 1989 6 28 5:30", file=sys.stderr)
        sys.exit(1)

    try:
        year, month, day = int(positional[0]), int(positional[1]), int(positional[2])
        t = positional[3]
        if ':' in t:
            hour, minute = int(t.split(':')[0]), int(t.split(':')[1])
        else:
            hour, minute = int(t), 0
    except ValueError:
        print("错误: 年月日时必须是数字", file=sys.stderr)
        sys.exit(1)

    birthplace = positional[4] if len(positional) > 4 else ''

    try:
        chart = compute_xingpan(year, month, day, hour, minute, birthplace)
    except Exception as e:
        print(f"计算失败: {e}", file=sys.stderr)
        sys.exit(2)

    if json_mode:
        result = json.dumps(chart, indent=2, ensure_ascii=False)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"OK: {output_file}")
        else:
            print(result)
    else:
        md = to_markdown(chart)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"OK: {output_file}")
        else:
            print(md)


if __name__ == '__main__':
    main()
