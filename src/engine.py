"""八字测算引擎 — 核心编排模块。

输入 → 计算 → 结构化命盘 dict。
这是对外唯一入口，所有计算委托给子模块。
"""

from datetime import date
from .pillars import compute_pillars, get_bazi_object
from .ten_gods import compute_all_shishen
from .strength import compute_strength, get_wx_distribution
from .luck import compute_luck, get_current_dayun, compute_liunian_ganzhi
from .rules import (TIANGAN, DIZHI, SHENGXIAO, NAYIN, CANG_GAN,
                     GAN_WUXING, ZHI_WUXING)
from .safety import sanitize_report, has_blocked_content, DISCLAIMER


def compute_bazi(year: int, month: int, day: int,
                 hour: int, minute: int = 0,
                 gender: str = '男', birthplace: str = '') -> dict:
    """计算完整八字命盘。

    Args:
        year, month, day: 公历日期
        hour: 小时 (0-23)
        minute: 分钟
        gender: '男' | '女'
        birthplace: 出生地（可选）

    Returns:
        完整的命盘 dict，包含：
        - input, pillars, ten_gods, hidden_stems,
        - five_elements, strength, day_master,
        - luck, annual_fortune, nayin, disclaimer
    """
    # ── 四柱 ──
    solar, bazi = get_bazi_object(year, month, day, hour, minute)
    pillars = compute_pillars(year, month, day, hour, minute)

    year_gan = pillars.year.gan
    year_zhi = pillars.year.zhi
    month_gan = pillars.month.gan
    month_zhi = pillars.month.zhi
    day_gan = pillars.day.gan
    day_zhi = pillars.day.zhi
    hour_gan = pillars.hour.gan
    hour_zhi = pillars.hour.zhi

    # ── 藏干 ──
    hidden = {
        'year': CANG_GAN[year_zhi],
        'month': CANG_GAN[month_zhi],
        'day': CANG_GAN[day_zhi],
        'hour': CANG_GAN[hour_zhi],
    }

    # ── 十神 ──
    pillar_gans = {
        'year': year_gan, 'month': month_gan,
        'day': day_gan, 'hour': hour_gan,
    }
    shishen = compute_all_shishen(day_gan, pillar_gans)

    # ── 支柱dict（给strength用）──
    pillars_for_strength = {
        'year': (year_gan, year_zhi),
        'month': (month_gan, month_zhi),
        'day': (day_gan, day_zhi),
        'hour': (hour_gan, hour_zhi),
    }

    # ── 五行 ──
    wx_dist = get_wx_distribution(pillars_for_strength, hidden)

    # ── 身强身弱 ──
    strength = compute_strength(pillars_for_strength, hidden)

    # ── 日主 ──
    day_master_wx = GAN_WUXING[day_gan]

    # ── 纳音 ──
    nayin = {
        'year': NAYIN.get((year_gan, year_zhi), '-'),
        'month': NAYIN.get((month_gan, month_zhi), '-'),
        'day': NAYIN.get((day_gan, day_zhi), '-'),
        'hour': NAYIN.get((hour_gan, hour_zhi), '-'),
    }

    # ── 大运 ──
    luck = compute_luck(bazi, gender)

    # ── 当前大运 ──
    today = date.today()
    current_year = today.year
    birth_year = year
    age = current_year - birth_year
    if today.month < month or (today.month == month and today.day < day):
        age -= 1  # 还没过生日

    current_dayun = get_current_dayun(age, luck.cycles)

    # ── 当前流年 ──
    liunian_ganzhi = compute_liunian_ganzhi(current_year)

    # ── 流年十神 ──
    liunian_gan = liunian_ganzhi[0]
    from .ten_gods import compute_shishen
    liunian_shishen = compute_shishen(day_gan, liunian_gan)

    # ── 生肖 ──
    shengxiao = SHENGXIAO[DIZHI.index(year_zhi)]

    # ── 组装输出 ──
    return {
        'input': {
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute,
            'gender': gender, 'birthplace': birthplace,
        },
        'solar_datetime': f'{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00',
        'adjusted_datetime': f'{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00+08:00',
        'true_solar_time_used': False,
        'pillars': pillars.as_dict(),
        'ten_gods': shishen,
        'hidden_stems': hidden,
        'five_elements': wx_dist,
        'day_master': {
            'gan': day_gan,
            'zhi': day_zhi,
            'element': day_master_wx,
            'shengxiao': shengxiao,
        },
        'nayin': nayin,
        'strength_analysis': {
            'verdict': strength.verdict,
            'same_party_score': strength.same_party,
            'opposing_party_score': strength.opposing_party,
            'useful_elements': strength.useful,
            'harmful_elements': strength.harmful,
            'reasoning': strength.reasoning,
        },
        'luck': {
            'direction': luck.direction,
            'qiyun_age': {
                'years': luck.qiyun_years,
                'months': luck.qiyun_months,
            },
            'pre_qiyun': [
                {'ganzhi': c.ganzhi, 'start_age': c.start_age, 'end_age': c.end_age, 'note': '童限（起运前）'}
                for c in luck.pre_qiyun
            ],
            'cycles': [
                {'ganzhi': c.ganzhi, 'start_age': c.start_age, 'end_age': c.end_age}
                for c in luck.cycles
            ],
            'current': {
                'ganzhi': current_dayun.ganzhi,
                'start_age': current_dayun.start_age,
                'end_age': current_dayun.end_age,
            } if current_dayun else None,
        },
        'annual_fortune': {
            'year': current_year,
            'ganzhi': liunian_ganzhi,
            'ten_god': liunian_shishen,
        },
        'current_age': age,
        'disclaimer': DISCLAIMER,
    }
