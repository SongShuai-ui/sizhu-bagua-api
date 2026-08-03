#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""梅花易数 CLI"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.meihua import compute_meihua, to_markdown


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print("用法: python meihua_cli.py <数字1> <数字2> <数字3> [问题] [--json] [--output path]")
        print("示例: python meihua_cli.py 5 2 0 问事业")
        print("      python meihua_cli.py 3 8 6 --json")
        sys.exit(0)

    json_mode = '--json' in args
    output_file = None
    for i, a in enumerate(args):
        if a == '--output' and i + 1 < len(args):
            output_file = args[i + 1]
            break

    positional = [a for a in args if not a.startswith('--')]
    try:
        a, b, c = int(positional[0]), int(positional[1]), int(positional[2])
    except (ValueError, IndexError):
        print("错误: 需要三个数字。示例: python meihua_cli.py 5 2 0", file=sys.stderr)
        sys.exit(1)

    question = positional[3] if len(positional) > 3 else ''

    try:
        chart = compute_meihua(a, b, c, question)
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
