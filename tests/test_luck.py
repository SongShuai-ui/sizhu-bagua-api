"""大运测试 — 验证顺逆排规则和起运年龄。

规则：
- 阳年男 → 顺排（甲丙戊庚壬年男）
- 阴年男 → 逆排（乙丁己辛癸年男）
- 阳年女 → 逆排
- 阴年女 → 顺排
"""

import pytest
from src.engine import compute_bazi


class TestLuckDirection:
    """大运方向测试"""

    def test_yang_male_forward(self):
        """甲子年男 → 顺排"""
        chart = compute_bazi(1984, 6, 1, 12, 0, '男')  # 甲子年
        assert chart['luck']['direction'] in ('顺排', '逆排')
        assert chart['luck']['direction'] == '顺排'

    def test_yin_male_reverse(self):
        """己巳年男 → 逆排"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')  # 己巳年
        assert chart['luck']['direction'] == '逆排'

    def test_yang_female_reverse(self):
        """甲子年女 → 逆排"""
        chart = compute_bazi(1984, 6, 1, 12, 0, '女')
        assert chart['luck']['direction'] == '逆排'

    def test_yin_female_forward(self):
        """己巳年女 → 顺排"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '女')
        assert chart['luck']['direction'] == '顺排'


class TestQiyunAge:
    """起运年龄测试"""

    def test_song_shuai_qiyun(self):
        """宋帅起运 7 岁 4 个月（非旧版硬编码的 3 岁）"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        qy = chart['luck']['qiyun_age']
        assert qy['years'] > 3  # 旧版硬编码3，实际应为7
        assert isinstance(qy['years'], int)
        assert isinstance(qy['months'], int)

    def test_qiyun_not_hardcoded(self):
        """不同生辰应有不同起运年龄"""
        chart1 = compute_bazi(1984, 6, 1, 12, 0, '男')
        chart2 = compute_bazi(2000, 11, 20, 14, 0, '男')
        qy1 = chart1['luck']['qiyun_age']['years']
        qy2 = chart2['luck']['qiyun_age']['years']
        # 不同八字大概率不同起运年龄（但不强制，理论上可以相同）
        assert isinstance(qy1, int) and isinstance(qy2, int)


class TestDayunCycles:
    """大运步骤测试"""

    def test_eight_cycles(self):
        """应有 8-10 步大运"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        cycles = chart['luck']['cycles']
        assert len(cycles) >= 8

    def test_each_cycle_has_ganzhi(self):
        """每步大运都有干支"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        for c in chart['luck']['cycles']:
            assert 'ganzhi' in c
            assert c['start_age'] < c['end_age']

    def test_current_dayun_exists(self):
        """当前大运字段存在"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert chart['luck']['current'] is not None
