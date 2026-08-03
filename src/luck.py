# -*- coding: utf-8 -*-
"""大运、起运年龄、流年计算模块。

底层使用 lunar-python 的 Yun 模块，该模块已正确实现：
- 阳年男/阴年女 → 顺排；阴年男/阳年女 → 逆排
- 起运年龄 = 出生日到节气的天数 / 3（精确到年月）
- 每步大运 10 年
- 流年按公历年计算

规则来源：
- 《渊海子平》论大运："阳男阴女顺行，阴男阳女逆行"
- 起运口诀："三天为一岁，一日为四月"

注意：
- lunar-python 的 getDaYun() 返回 10 步，第一步可能是起运前的"童限"
  （干支为空字符串）。需要过滤掉童限，只保留正式大运。
"""

from typing import NamedTuple
from datetime import date
from .rules import TIANGAN, DIZHI


class DayunStep(NamedTuple):
    ganzhi: str
    start_age: int
    end_age: int


class LuckResult(NamedTuple):
    direction: str                     # '顺排' | '逆排'
    qiyun_years: int                   # 起运岁数
    qiyun_months: int                  # 起运月数
    pre_qiyun: list[DayunStep]         # 童限（起运前）
    cycles: list[DayunStep]            # 正式大运（8步）
    current: DayunStep | None          # 当前大运
    current_year_ganzhi: str           # 当前流年干支


def compute_luck(bazi, gender: str = '男') -> LuckResult:
    """计算大运和起运。

    Args:
        bazi: lunar-python 的 EightChar 对象
        gender: '男' | '女'

    Returns:
        LuckResult 包含童限、正式大运、当前大运、流年
    """
    yun = bazi.getYun(gender=1 if gender == '男' else 0)

    direction = '顺排' if yun.isForward() else '逆排'
    qiyun_years = yun.getStartYear()
    qiyun_months = yun.getStartMonth()

    da_yun = yun.getDaYun()

    # 分离童限和正式大运
    pre_qiyun = []
    formal_cycles = []
    for dy in da_yun:
        gz = dy.getGanZhi()
        step = DayunStep(
            ganzhi=gz,
            start_age=dy.getStartAge(),
            end_age=dy.getEndAge(),
        )
        # 干支为空的步骤是起运前的童限期
        if not gz or gz.strip() == '':
            pre_qiyun.append(step)
        else:
            formal_cycles.append(step)

    # 当前流年干支
    today = date.today()
    current_year = today.year
    current_ganzhi = compute_liunian_ganzhi(current_year)

    return LuckResult(
        direction=direction,
        qiyun_years=qiyun_years,
        qiyun_months=qiyun_months,
        pre_qiyun=pre_qiyun,
        cycles=formal_cycles,
        current=None,  # engine 层根据年龄动态计算
        current_year_ganzhi=current_ganzhi,
    )


def compute_liunian_ganzhi(year: int) -> str:
    """计算流年干支。

    年柱公式: (year - 4) % 10 → 天干, (year - 4) % 12 → 地支
    """
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return f'{TIANGAN[gan_idx]}{DIZHI[zhi_idx]}'


def get_current_dayun(age: int, cycles: list[DayunStep]) -> DayunStep | None:
    """根据年龄确定当前所处的大运。"""
    for cyc in cycles:
        if cyc.start_age <= age <= cyc.end_age:
            return cyc
    return None
