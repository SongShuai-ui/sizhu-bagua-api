#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""六爻预测 CLI"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.liuyao import compute_liuyao, to_markdown


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print("用法:")
        print("  python liuyao_cli.py q <问题>              # 随机铜钱起卦")
        print("  python liuyao_cli.py <6个数字> [问题]       # 数字起卦")
        print("  python liuyao_cli.py 3 6 8 4 2 9 --json    # JSON 输出")
        sys.exit(0)

    json_mode = '--json' in args
    output_file = None
    for i, a in enumerate(args):
        if a == '--output' and i + 1 < len(args):
            output_file = args[i + 1]
            break

    positional = [a for a in args if not a.startswith('--')]

    try:
        if positional and positional[0] == 'q':
            question = positional[1] if len(positional) > 1 else ''
            chart = compute_liuyao(question=question)
        elif len(positional) >= 6:
            nums = [int(x) for x in positional[:6]]
            question = positional[6] if len(positional) > 6 else ''
            chart = compute_liuyao(numbers=nums, question=question)
        else:
            print("错误: 需要6个数字或 'q' 模式。示例: python liuyao_cli.py 3 6 8 4 2 9", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        print("错误: 数字必须是整数", file=sys.stderr)
        sys.exit(1)
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
