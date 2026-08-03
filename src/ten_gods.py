"""十神计算模块。

独立实现，不依赖 lunar-python 的十神输出。
使用已验证的双表映射（阳干/阴干各一套）。

规则来源：
- 阳干日主(甲丙戊庚壬)：diff→十神的映射为一套
- 阴干日主(乙丁己辛癸)：diff→十神的映射为另一套
- 两组在 diff=1,3,5,7,9 位置上互换
"""

from .rules import TIANGAN

# ── 十神映射表 ──
# 阳干日主 (日干索引为偶数: 甲0丙2戊4庚6壬8)
YANG_SHISHEN = {
    0: '比肩', 1: '劫财', 2: '食神', 3: '伤官', 4: '偏财',
    5: '正财', 6: '七杀', 7: '正官', 8: '偏印', 9: '正印',
}

# 阴干日主 (日干索引为奇数: 乙1丁3己5辛7癸9)
YIN_SHISHEN = {
    0: '比肩', 1: '伤官', 2: '食神', 3: '正财', 4: '偏财',
    5: '正官', 6: '七杀', 7: '正印', 8: '偏印', 9: '劫财',
}


def compute_shishen(day_gan: str, other_gan: str) -> str:
    """计算一个天干相对于日干的十神关系。

    Args:
        day_gan: 日干 (例如 '己')
        other_gan: 目标天干 (例如 '庚')

    Returns:
        十神名称，如 '伤官', '比肩', '正印' 等

    Examples:
        >>> compute_shishen('己', '庚')
        '伤官'
        >>> compute_shishen('己', '己')
        '比肩'
        >>> compute_shishen('甲', '辛')
        '正官'
    """
    ri = TIANGAN.index(day_gan)
    other = TIANGAN.index(other_gan)
    diff = (other - ri) % 10

    is_yang_ri = ri % 2 == 0  # 甲(0)丙(2)戊(4)庚(6)壬(8)
    mapping = YANG_SHISHEN if is_yang_ri else YIN_SHISHEN
    return mapping[diff]


def compute_all_shishen(day_gan: str, pillar_gans: dict) -> dict:
    """计算四柱天干各自的十神。

    Args:
        day_gan: 日干
        pillar_gans: {'year': '己', 'month': '庚', 'day': '己', 'hour': '丁'}

    Returns:
        {'year_gan': '比肩', 'month_gan': '伤官', 'day_gan': '日元', 'hour_gan': '偏印'}
    """
    result = {}
    for key, gan in pillar_gans.items():
        if key == 'day':
            result[f'{key}_gan'] = '日元'
        else:
            result[f'{key}_gan'] = compute_shishen(day_gan, gan)
    return result
