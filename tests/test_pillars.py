"""四柱测试 — 验证年、月、日、时柱计算。

覆盖：立春切换、节气换月、子时、闰年、不同日主
"""

import pytest
from src.engine import compute_bazi


def pillar_str(pillars, key):
    """返回完整干支字符串"""
    p = pillars[key]
    return f'{p["gan"]}{p["zhi"]}'


class TestYearPillar:
    """年柱测试 — 必须按立春切换"""

    def test_before_lichun(self):
        """立春前：年柱应为上一年"""
        chart = compute_bazi(1989, 2, 3, 12, 0, '男')
        assert pillar_str(chart['pillars'], 'year') in ('戊辰',)

    def test_after_lichun(self):
        """立春后：年柱应为当年"""
        chart = compute_bazi(1989, 2, 5, 12, 0, '男')
        assert pillar_str(chart['pillars'], 'year') in ('己巳',)

    def test_lichun_boundary_change(self):
        """立春前后年柱必须不同"""
        before = compute_bazi(1989, 2, 3, 12, 0, '男')
        after = compute_bazi(1989, 2, 5, 12, 0, '男')
        assert pillar_str(before['pillars'], 'year') != pillar_str(after['pillars'], 'year')


class TestMonthPillar:
    """月柱测试 — 必须按节气切换"""

    def test_before_jingzhe(self):
        """惊蛰前：应为正月（寅月）"""
        chart = compute_bazi(1989, 3, 5, 12, 0, '男')
        month = pillar_str(chart['pillars'], 'month')
        # 月支应为 寅
        assert '寅' in month

    def test_after_jingzhe(self):
        """惊蛰后：应为二月（卯月）"""
        chart = compute_bazi(1989, 3, 7, 12, 0, '男')
        month = pillar_str(chart['pillars'], 'month')
        assert '卯' in month

    def test_january_is_chou_month(self):
        """一月中旬应为丑月"""
        chart = compute_bazi(1989, 1, 15, 12, 0, '男')
        month = pillar_str(chart['pillars'], 'month')
        assert '丑' in month

    def test_december_is_zi_month(self):
        """十二月应为子月"""
        chart = compute_bazi(1989, 12, 15, 12, 0, '男')
        month = pillar_str(chart['pillars'], 'month')
        assert '子' in month


class TestHourPillar:
    """时柱测试"""

    def test_early_zi_hour(self):
        """早子时（0-1点）"""
        chart = compute_bazi(2020, 1, 1, 0, 30, '男')
        hour = pillar_str(chart['pillars'], 'hour')
        assert '子' in hour

    def test_late_zi_hour(self):
        """晚子时（23-24点）"""
        chart = compute_bazi(2020, 1, 1, 23, 30, '男')
        hour = pillar_str(chart['pillars'], 'hour')
        assert '子' in hour

    def test_noon_is_wu_hour(self):
        """午时"""
        chart = compute_bazi(1989, 6, 28, 12, 0, '男')
        hour = pillar_str(chart['pillars'], 'hour')
        assert '午' in hour


class TestDayPillar:
    """日柱测试"""

    def test_known_reference(self):
        """2024-01-01 已知为甲子日"""
        chart = compute_bazi(2024, 1, 1, 12, 0, '男')
        day = pillar_str(chart['pillars'], 'day')
        assert day == '甲子'

    def test_leap_year(self):
        """闰年不崩溃"""
        chart = compute_bazi(2000, 2, 29, 10, 0, '男')
        assert pillar_str(chart['pillars'], 'day') != ''


class TestSongShuai:
    """宋帅基准测试"""

    def test_four_pillars(self):
        """宋帅四柱验证"""
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert pillar_str(chart['pillars'], 'year') == '己巳'
        assert pillar_str(chart['pillars'], 'month') == '庚午'
        assert pillar_str(chart['pillars'], 'day') == '己未'
        assert pillar_str(chart['pillars'], 'hour') == '丁卯'

    def test_day_master(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert chart['day_master']['gan'] == '己'
        assert chart['day_master']['element'] == '土'

    def test_shengxiao(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert chart['day_master']['shengxiao'] == '蛇'
