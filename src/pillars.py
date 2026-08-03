"""四柱计算模块。

封装 lunar-python 的 EightChar，提供统一接口。
底层已内置立春切换年和节气切换月，无需自建历法。
"""

from typing import NamedTuple
from lunar_python import Solar


class Pillar(NamedTuple):
    gan: str
    zhi: str

    @property
    def ganzhi(self) -> str:
        return f'{self.gan}{self.zhi}'


class FourPillars(NamedTuple):
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    def as_dict(self) -> dict:
        return {
            'year': {'gan': self.year.gan, 'zhi': self.year.zhi},
            'month': {'gan': self.month.gan, 'zhi': self.month.zhi},
            'day': {'gan': self.day.gan, 'zhi': self.day.zhi},
            'hour': {'gan': self.hour.gan, 'zhi': self.hour.zhi},
        }


def compute_pillars(year: int, month: int, day: int, hour: int, minute: int = 0) -> FourPillars:
    """根据公历日期时间计算八字四柱。

    Args:
        year: 公历年
        month: 公历月 (1-12)
        day: 公历日
        hour: 小时 (0-23)
        minute: 分钟

    Returns:
        FourPillars 包含年月日时四柱

    lunar-python 内部处理：
    - 立春切换年柱
    - 节气切换月柱
    - 日柱按黄经计算
    - 五鼠遁时柱
    """
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    bazi = lunar.getEightChar()

    return FourPillars(
        year=Pillar(gan=bazi.getYearGan(), zhi=bazi.getYearZhi()),
        month=Pillar(gan=bazi.getMonthGan(), zhi=bazi.getMonthZhi()),
        day=Pillar(gan=bazi.getDayGan(), zhi=bazi.getDayZhi()),
        hour=Pillar(gan=bazi.getTimeGan(), zhi=bazi.getTimeZhi()),
    )


def get_bazi_object(year: int, month: int, day: int, hour: int, minute: int = 0):
    """获取 lunar-python 的 EightChar 对象，供其他模块使用。"""
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    return solar, solar.getLunar().getEightChar()
