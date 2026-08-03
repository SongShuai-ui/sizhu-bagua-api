#!/usr/bin/env python3
"""将八字简批 Markdown 报告直接生成排版精良的 PDF"""

import sys, re, os
from pathlib import Path
from fpdf import FPDF

FONT_FILE = 'C:/Windows/Fonts/simhei.ttf'


class BaziPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('CN', '', FONT_FILE)
        self.add_font('CN', 'B', FONT_FILE)  # 粗体用同一字体
        self.set_auto_page_break(True, 18)
        self._w = self.w - self.l_margin - self.r_margin

    @property
    def pw(self):
        """有效页面宽度"""
        return self.w - self.l_margin - self.r_margin

    def ttl(self, txt):
        self.ln(4)
        self.set_font('CN', 'B', 18)
        self.multi_cell(self.pw, 10, txt, align='C')
        self.ln(2)

    def meta_line(self, txt):
        self.set_font('CN', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(self.pw, 6, txt, align='C', new_x="LMARGIN", new_y="NEXT")

    def sec(self, txt):
        self.ln(3)
        self.set_font('CN', 'B', 13)
        self.set_text_color(30, 30, 30)
        self.multi_cell(self.pw, 8, txt)
        self.ln(1)

    def subsec(self, txt):
        self.ln(1)
        self.set_font('CN', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(self.pw, 7, txt)
        self.ln(0.5)

    def txt(self, text):
        self.set_font('CN', '', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self.pw, 6.5, text, align='L')

    def bold(self, text):
        self.set_font('CN', 'B', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self.pw, 6.5, text, align='L')

    def qt(self, text):
        self.set_font('CN', '', 10)
        self.set_text_color(110, 110, 110)
        x0 = self.l_margin + 8
        self.set_x(x0)
        self.multi_cell(self.pw - 8, 6, text, align='L')

    def cd(self, text):
        self.set_font('CN', '', 9)
        self.set_text_color(90, 90, 90)
        x0 = self.l_margin + 8
        self.set_x(x0)
        self.multi_cell(self.pw - 8, 5, text, align='L')

    def hr(self):
        self.ln(1)
        self.set_draw_color(190, 190, 190)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.l_margin + self.pw, y)
        self.ln(4)

    def ft(self, text):
        self.set_font('CN', '', 8)
        self.set_text_color(160, 160, 160)
        self.multi_cell(self.pw, 5, text, align='C')


def generate_pdf(md_path: str, output_path: str = None):
    md_path = Path(md_path)
    if output_path is None:
        output_path = md_path.with_suffix('.pdf')

    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')

    pdf = BaziPDF()
    pdf.add_page()

    report_title = ''
    in_code = False

    for line in lines:
        s = line.strip()

        if not s:
            pdf.ln(1.5)
            continue

        # 主标题
        if s.startswith('# ') and not s.startswith('## '):
            report_title = s[2:].strip()
            pdf.ttl('八字命理简批报告')
            pdf.meta_line(report_title)
            pdf.hr()
            continue

        # 章节标题
        if s.startswith('## '):
            pdf.sec(s[3:].strip())
            continue

        # 小节标题
        if s.startswith('### '):
            pdf.subsec(s[4:].strip())
            continue

        # 代码块
        if s == '```':
            in_code = not in_code
            pdf.ln(0.5)
            continue
        if in_code:
            pdf.cd(s)
            continue

        # 分割线
        if s == '---':
            pdf.hr()
            continue

        # 引用
        if s.startswith('> '):
            pdf.qt(s[2:].strip())
            continue

        # 粗体行
        if s.startswith('**') and s.endswith('**'):
            pdf.bold(s[2:-2].strip())
            continue

        # 元数据行（粗体内嵌）
        if s.startswith('**') and '：' in s and ':**' not in s and ': **' not in s:
            cleaned = re.sub(r'\*+', '', s)
            pdf.meta_line(cleaned)
            continue

        # 普通文本
        pdf.txt(s)

    # 页脚
    pdf.ln(8)
    pdf.hr()
    pdf.ft('以上分析基于传统命理学，仅供参考。人生选择请结合现实独立判断。')

    pdf.output(str(output_path))
    print(f'[OK] PDF已生成: {output_path}')
    return str(output_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python generate_bazi_pdf.py <md_path> [output_path]')
        sys.exit(1)
    generate_pdf(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
