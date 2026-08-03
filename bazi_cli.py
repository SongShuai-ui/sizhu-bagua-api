#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字排盘 CLI - 产品化版本 v2

用法:
    python bazi_cli.py 1989 6 28 5:30 男 林州
    python bazi_cli.py 1990 3 15 8:00 女 --json
    python bazi_cli.py 2000 1 1 12:00 男 --json --output result.json
    python bazi_cli.py 1989 6 28 5:30 男 --compare

依赖: pip install lunar-python
"""

import sys
import os
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.engine import compute_bazi
from src.report import to_json, to_markdown


class BaziError(Exception):
    """八字计算错误"""
    pass


def parse_args(args: list[str]) -> dict:
    """解析命令行参数，返回 dict。

    Raises:
        BaziError: 参数无效时给出友好提示
    """
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    # 分离参数和标志
    positional = []
    flags = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith('--'):
            if a == '--output' and i + 1 < len(args):
                flags['output'] = args[i + 1]
                i += 2
            else:
                flags[a.lstrip('-')] = True
                i += 1
        else:
            positional.append(a)
            i += 1

    if len(positional) < 4:
        raise BaziError(
            '参数不足。最少需要：年 月 日 时 性别\n'
            '示例: python bazi_cli.py 1989 6 28 5:30 男'
        )

    # 年月日
    try:
        year = int(positional[0])
        month = int(positional[1])
        day = int(positional[2])
    except ValueError:
        raise BaziError('年月日必须是整数。示例: 1989 6 28')

    if year < 1900 or year > 2100:
        raise BaziError(f'年份 {year} 超出支持范围（1900-2100）')
    if month < 1 or month > 12:
        raise BaziError(f'月份 {month} 无效，应为 1-12')
    if day < 1 or day > 31:
        raise BaziError(f'日期 {day} 无效，应为 1-31')

    # 时间
    time_str = positional[3]
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        else:
            hour = int(time_str)
            minute = 0
    except ValueError:
        raise BaziError(f'时间格式无效: {time_str}。请使用 HH:MM 或 HH')

    if hour < 0 or hour > 23:
        raise BaziError(f'小时 {hour} 无效，应为 0-23')
    if minute < 0 or minute > 59:
        raise BaziError(f'分钟 {minute} 无效，应为 0-59')

    # 性别（支持 男/女，位置灵活——在第5个或任意位置）
    gender = '男'  # 默认
    birthplace = ''
    for p in positional[4:]:
        if p in ('男', '女'):
            gender = p
        elif not p.startswith('-'):
            birthplace = p

    # 验证日期有效性
    import datetime
    try:
        datetime.datetime(year, month, day)
    except ValueError as e:
        raise BaziError(f'日期无效: {year}-{month:02d}-{day:02d} ({e})')

    return {
        'year': year, 'month': month, 'day': day,
        'hour': hour, 'minute': minute,
        'gender': gender, 'birthplace': birthplace,
        'json_mode': flags.get('json', False),
        'compare_mode': flags.get('compare', False),
        'output_file': flags.get('output', None),
    }


def main():
    try:
        opts = parse_args(sys.argv[1:])
    except BaziError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)

    try:
        chart = compute_bazi(
            opts['year'], opts['month'], opts['day'],
            opts['hour'], opts['minute'],
            opts['gender'], opts['birthplace'],
        )
    except Exception as e:
        print(f'计算失败: {e}', file=sys.stderr)
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(2)

    # 输出
    output_file = opts['output_file']
    if opts['json_mode']:
        result = to_json(chart)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'OK: {output_file}')
        else:
            print(result)
    else:
        md = to_markdown(chart)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f'OK: {output_file}')
        else:
            print(md)

    # 对比模式
    if opts['compare_mode']:
        qy = chart['luck']['qiyun_age']
        print()
        print('=' * 60)
        print('新旧引擎差异')
        print('=' * 60)
        print(f'起运年龄: 新={qy["years"]}岁{qy["months"]}个月  vs  旧=3岁(硬编码)')
        print(f'身强身弱: 按{chart["day_master"]["element"]}日主动态计算  vs  旧=写死土日主')
        print(f'年柱切换: 真实立春  vs  旧=公历1月1日')
        print(f'节气数据: lunar-python天文计算  vs  旧=固定日期表')
        print(f'真太阳时: 预留(false)  vs  旧=未实现')


if __name__ == '__main__':
    main()
