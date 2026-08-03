"""身强身弱分析模块。

按日主五行**动态计算**同党和异党，不再写死特定五行。
算法参考《滴天髓》得令/得地/得势原则。

规则来源：
- 日主五行 → 同党 = 生我者(印) + 同我者(比劫)
- 日主五行 → 异党 = 我生者(食伤) + 我克者(财) + 克我者(官杀)
- 月令得令加权
- 天干通根加分
"""

from typing import NamedTuple
from .rules import (TIANGAN, DIZHI, CANG_GAN, GAN_WUXING, ZHI_WUXING,
                     wx_sheng_wo, wx_sheng, wx_ke, wx_ke_wo)


class StrengthResult(NamedTuple):
    verdict: str           # '身强' | '身弱' | '中和'
    same_party: float      # 同党得分
    opposing_party: float  # 异党得分
    useful: list[str]      # 喜用神五行
    harmful: list[str]     # 忌神五行
    day_master_wx: str     # 日主五行
    reasoning: str         # 简短说明


def compute_strength(pillars: dict, hidden_stems: dict) -> StrengthResult:
    """计算身强身弱和喜忌。

    Args:
        pillars: {'year': (gan,zhi), 'month': (gan,zhi), 'day': (gan,zhi), 'hour': (gan,zhi)}
        hidden_stems: {'year': [gan,...], 'month': [...], 'day': [...], 'hour': [...]}

    Returns:
        StrengthResult
    """
    day_gan = pillars['day'][0]
    day_zhi = pillars['day'][1]
    month_zhi = pillars['month'][1]

    day_wx = GAN_WUXING[day_gan]
    month_wx = ZHI_WUXING[month_zhi]

    # ── 确定同党/异党五行 ──
    sheng_wo = wx_sheng_wo(day_wx)   # 印星（生我者）
    tong_wo = day_wx                 # 比劫（同我者）
    wo_sheng = wx_sheng(day_wx)      # 食伤（我生者）
    wo_ke = wx_ke(day_wx)            # 财星（我克者）
    ke_wo = wx_ke_wo(day_wx)         # 官杀（克我者）

    same_wx = {sheng_wo, tong_wo}    # 同党五行集合
    opposing_wx = {wo_sheng, wo_ke, ke_wo}  # 异党五行集合

    # ── 计分 ──
    score = {'same': 0.0, 'opposing': 0.0}

    # 天干（1.0 分/个）
    for position in ['year', 'month', 'day', 'hour']:
        gan = pillars[position][0]
        wx = GAN_WUXING[gan]
        if wx in same_wx:
            score['same'] += 1.0
        elif wx in opposing_wx:
            score['opposing'] += 1.0

    # 地支（1.5 分/个，通根更重）
    for position in ['year', 'month', 'day', 'hour']:
        zhi = pillars[position][1]
        wx = ZHI_WUXING[zhi]
        if wx in same_wx:
            score['same'] += 1.5
        elif wx in opposing_wx:
            score['opposing'] += 1.5

    # 藏干（0.3 分/个，加权轻）
    for position in ['year', 'month', 'day', 'hour']:
        for gan in hidden_stems.get(position, []):
            wx = GAN_WUXING[gan]
            if wx in same_wx:
                score['same'] += 0.3
            elif wx in opposing_wx:
                score['opposing'] += 0.3

    # 月令加权（得令 × 1.5）
    if month_wx in same_wx:
        # 月令为同党，额外加分
        score['same'] += 1.5

    # ── 判断 ──
    same = score['same']
    opposing = score['opposing']

    if same > opposing * 1.3:
        verdict = '身强'
        useful = list(opposing_wx)  # 喜克泄耗
        harmful = list(same_wx)     # 忌生扶
    elif opposing > same * 1.3:
        verdict = '身弱'
        useful = list(same_wx)      # 喜生扶
        harmful = list(opposing_wx) # 忌克泄耗
    else:
        verdict = '中和'
        useful = []
        harmful = []

    reasoning = (
        f'日主{day_gan}({day_wx})生于{month_zhi}月（{month_wx}），'
        f'同党{same:.1f} vs 异党{opposing:.1f}'
    )
    if month_wx in same_wx:
        reasoning += '，月令得令'
    else:
        reasoning += '，月令失令'

    return StrengthResult(
        verdict=verdict,
        same_party=round(same, 1),
        opposing_party=round(opposing, 1),
        useful=useful,
        harmful=harmful,
        day_master_wx=day_wx,
        reasoning=reasoning,
    )


def get_wx_distribution(pillars: dict, hidden_stems: dict) -> dict:
    """统计五行分布。

    Returns:
        {'木': 1.6, '火': 3.9, '土': 3.9, '金': 1.3, '水': 0.0}
    """
    wx_count = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}

    for position in ['year', 'month', 'day', 'hour']:
        gan, zhi = pillars[position]
        wx_count[GAN_WUXING[gan]] += 1.0
        wx_count[ZHI_WUXING[zhi]] += 1.0

    for position in ['year', 'month', 'day', 'hour']:
        for gan in hidden_stems.get(position, []):
            wx_count[GAN_WUXING[gan]] += 0.3

    return {k: round(v, 1) for k, v in wx_count.items()}
