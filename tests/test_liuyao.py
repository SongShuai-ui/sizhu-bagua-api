# -*- coding: utf-8 -*-
"""六爻预测测试"""

import json, subprocess, sys, os
import pytest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from src.liuyao import compute_liuyao, to_markdown


class TestCore:
    def test_number_method_6_yaos(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        assert len(chart['yaos']) == 6

    def test_random_method_6_yaos(self):
        chart = compute_liuyao()
        assert len(chart['yaos']) == 6

    def test_yao_values_valid(self):
        chart = compute_liuyao(numbers=[1,2,3,4,5,6])
        for y in chart['yaos']:
            assert y['value'] in (6,7,8,9)

    def test_shi_yao_exists(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        assert chart['shi_yao'] is not None
        assert 1 <= chart['shi_yao'] <= 6

    def test_ying_yao_exists(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        assert chart['ying_yao'] is not None
        assert 1 <= chart['ying_yao'] <= 6

    def test_gua_name_not_empty(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        assert chart['gua_name'] != ''

    def test_moving_yaos_detected(self):
        # 2→老阳 4→老阴 → should have moving lines
        chart = compute_liuyao(numbers=[2,4,1,1,1,1])
        assert chart['moving_count'] > 0

    def test_question_preserved(self):
        chart = compute_liuyao(numbers=[1,1,1,1,1,1], question='财运')
        assert chart['question'] == '财运'

    def test_disclaimer_present(self):
        chart = compute_liuyao(numbers=[1,1,1,1,1,1])
        assert '仅供参考' in chart['disclaimer']

    def test_markdown_contains_sections(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        md = to_markdown(chart)
        assert '六爻' in md
        assert '仅供参考' in md

    def test_no_garbled(self):
        chart = compute_liuyao(numbers=[3,6,8,4,2,9])
        md = to_markdown(chart)
        for bad in ['�', '鍏', '鐢']:
            assert bad not in md


class TestCLI:
    def run(self, *args):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        return subprocess.run(
            [sys.executable, '-X', 'utf8', os.path.join(BASE, 'liuyao_cli.py')] + list(args),
            capture_output=True, text=True, errors='replace', cwd=BASE, env=env,
        )

    def test_cli_json_parses(self):
        r = self.run('3', '6', '8', '4', '2', '9', '--json')
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert 'gua_name' in data

    def test_cli_help_exits_ok(self):
        r = self.run('--help')
        assert r.returncode == 0
