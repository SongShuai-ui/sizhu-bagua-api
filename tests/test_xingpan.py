# -*- coding: utf-8 -*-
"""占星星盘测试"""

import json, subprocess, sys, os
import pytest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from src.xingpan import compute_xingpan, to_markdown


class TestCore:
    def test_song_shuai_sun_cancer(self):
        """宋帅太阳应为巨蟹座"""
        chart = compute_xingpan(1989, 6, 28, 5, 30, '林州')
        assert chart['planets']['太阳']['zodiac'] == '巨蟹'

    def test_all_planets_present(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        expected = ['太阳','月亮','水星','金星','火星','木星','土星','天王星','海王星','冥王星']
        for name in expected:
            assert name in chart['planets']

    def test_ascendant_exists(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        assert chart['ascendant']['zodiac'] in ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']

    def test_midheaven_exists(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        assert chart['midheaven']['zodiac'] in ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']

    def test_elements_sum_to_5(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        s = sum(chart['element_distribution'].values())
        assert s == 5  # 日月水金火 = 5 颗个人行星

    def test_true_solar_time_false(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        assert chart['true_solar_time_used'] == False

    def test_disclaimer_present(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        assert '仅供参考' in chart['disclaimer']

    def test_markdown_contains_sections(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        md = to_markdown(chart)
        assert '星盘' in md
        assert '太阳' in md
        assert '仅供参考' in md

    def test_no_garbled(self):
        chart = compute_xingpan(1989, 6, 28, 5, 30)
        md = to_markdown(chart)
        for bad in ['�', '鍏', '鐢']:
            assert bad not in md


class TestCLI:
    def run(self, *args):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        return subprocess.run(
            [sys.executable, '-X', 'utf8', os.path.join(BASE, 'xingpan_cli.py')] + list(args),
            capture_output=True, text=True, errors='replace', cwd=BASE, env=env,
        )

    def test_cli_json_parses(self):
        r = self.run('1989', '6', '28', '5:30', '--json')
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert 'planets' in data

    def test_cli_help_exits_ok(self):
        r = self.run('--help')
        assert r.returncode == 0
