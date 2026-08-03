#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键生成报告 — 同时出 PDF + DOCX，按日期归档。

支持 Markdown 和 JSON 两种输入。
生成前自动运行安全过滤。

用法:
    python generate_report.py <md或json路径> [客户名]
    python generate_report.py 命盘.json 张三
"""

import sys, os, json
from pathlib import Path
from datetime import date

BASE_DIR = Path(r'G:\ClaudeCode\四柱八卦\客户报告')


def generate(input_path: str, client_name: str = None):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f'[ERROR] 文件不存在: {input_path}')
        return

    client_name = client_name or input_path.stem

    # 读取内容
    suffix = input_path.suffix.lower()
    if suffix == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 用 v2 engine 的 to_markdown 转换
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.report import to_markdown
        md_content = to_markdown(data)
    elif suffix == '.md':
        md_content = input_path.read_text(encoding='utf-8')
    else:
        print(f'[ERROR] 不支持的文件格式: {suffix}，需要 .md 或 .json')
        return

    # 安全过滤
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.safety import sanitize_report, has_blocked_content, format_warnings
    clean_md, warnings = sanitize_report(md_content)
    if warnings:
        print(format_warnings(warnings))
    if has_blocked_content(warnings):
        print('[WARN] 检测到禁止内容，请人工审核后再发送。')
        # 继续生成但标记风险

    # 写临时 Markdown 文件供 PDF/DOCX 生成器使用
    tmp_md = input_path.parent / f'_tmp_{client_name}.md'
    tmp_md.write_text(clean_md, encoding='utf-8')

    # 按日期建文件夹
    today = date.today()
    folder = BASE_DIR / f'{today.year}年{today.month}月' / f'{today.day:02d}日'
    folder.mkdir(parents=True, exist_ok=True)

    pdf_out = folder / f'{client_name}.pdf'
    docx_out = folder / f'{client_name}.docx'

    # 生成 PDF
    scripts_dir = str(Path(__file__).parent)
    sys.path.insert(0, scripts_dir)
    from generate_bazi_pdf import generate_pdf
    generate_pdf(str(tmp_md), str(pdf_out))

    # 生成 DOCX
    from generate_bazi_docx import generate_bazi_report
    generate_bazi_report(str(tmp_md), str(docx_out))

    # 清理临时文件
    tmp_md.unlink(missing_ok=True)

    print(f'\n[报告已生成]')
    print(f'  文件夹: {folder}')
    if pdf_out.exists():
        print(f'  PDF: {pdf_out.name}  ({pdf_out.stat().st_size / 1024:.0f} KB)')
    if docx_out.exists():
        print(f'  DOCX: {docx_out.name}  ({docx_out.stat().st_size / 1024:.0f} KB)')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
