# -*- coding: utf-8 -*-
"""梅花易数测试"""

import json, subprocess, sys, os
import pytest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from src.meihua import compute_meihua, to_markdown

# 已知卦象验证
KNOWN_CASES = [
    # (a,b,c, expected_bengua_name) — key=(下卦,上卦)
    (5, 2, 0, '风泽中孚'),   # 上巽(5)下兑(2) → key(2,5)=61 风泽中孚
    (3, 8, 6, '火地晋'),     # 上离(3)下坤(8) → key(8,3)=35 火地晋
    (1, 1, 1, '乾为天'),
    (8, 8, 8, '坤为地'),
    (6, 6, 6, '坎为水'),
    (3, 3, 3, '离为火'),
]


class TestCore:
    @pytest.mark.parametrize('a,b,c,expected', KNOWN_CASES)
    def test_bengua_name(self, a, b, c, expected):
        chart = compute_meihua(a, b, c)
        assert chart['bengua']['name'] == expected

    def test_has_hugua(self):
        chart = compute_meihua(5, 2, 0)
        assert chart['hugua']['name'] != ''

    def test_has_biangua(self):
        chart = compute_meihua(5, 2, 0)
        assert chart['biangua']['name'] != ''

    def test_tiyong_result(self):
        chart = compute_meihua(5, 2, 0)
        assert chart['tiyong']['result'] in ('比和','用生体（大吉）','体生用（耗泄）','用克体（凶）','体克用（小吉）')

    def test_question_preserved(self):
        chart = compute_meihua(1, 2, 3, '能否成功')
        assert chart['input']['question'] == '能否成功'

    def test_dong_yao_range(self):
        for a, b, c in [(1,1,1),(5,2,0),(8,8,9)]:
            chart = compute_meihua(a, b, c)
            assert 1 <= chart['dong_yao'] <= 6

    def test_disclaimer_present(self):
        chart = compute_meihua(1, 2, 3)
        assert '仅供参考' in chart['disclaimer']

    def test_markdown_contains_sections(self):
        chart = compute_meihua(5, 2, 0, '问事业')
        md = to_markdown(chart)
        assert '梅花易数' in md
        assert '本卦' in md or 'bengua' in md.lower()
        assert '仅供参考' in md

    def test_no_garbled_in_markdown(self):
        chart = compute_meihua(5, 2, 0)
        md = to_markdown(chart)
        for bad in ['�', '鍏', '鐢']:
            assert bad not in md

    def test_no_garbled_in_json(self):
        chart = compute_meihua(5, 2, 0)
        js = json.dumps(chart, ensure_ascii=False)
        for bad in ['�', '鍏', '鐢']:
            assert bad not in js


class TestCLI:
    def run(self, *args):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        return subprocess.run(
            [sys.executable, '-X', 'utf8', os.path.join(BASE, 'meihua_cli.py')] + list(args),
            capture_output=True, text=True, errors='replace', cwd=BASE, env=env,
        )

    def test_cli_json_parses(self):
        r = self.run('5', '2', '0', '--json')
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert 'bengua' in data

    def test_cli_help_exits_ok(self):
        r = self.run('--help')
        assert r.returncode == 0

    def test_cli_bad_input_fails(self):
        r = self.run('abc', 'def', 'ghi')
        assert r.returncode != 0
