"""结构化输出模块。

将 engine.compute_bazi() 返回的 dict 转换为各类格式：
- JSON（完整命盘数据）
- Markdown（人类可读报告）
- Text（纯文本摘要）
"""

import json


def to_json(chart: dict, indent: int = 2, ensure_ascii: bool = False) -> str:
    """输出完整 JSON，默认 ensure_ascii=False 使中文直接可读。"""
    return json.dumps(chart, indent=indent, ensure_ascii=ensure_ascii)


def to_markdown(chart: dict) -> str:
    """输出 Markdown 格式的人类可读报告。"""
    p = chart['pillars']
    tg = chart['ten_gods']
    hs = chart['hidden_stems']
    wx = chart['five_elements']
    sa = chart['strength_analysis']
    lk = chart['luck']
    af = chart['annual_fortune']
    inp = chart['input']
    dm = chart['day_master']
    nayin = chart['nayin']

    lines = [
        f"# 八字命理简批报告",
        f"",
        f"**公历：** {inp['year']}年{inp['month']}月{inp['day']}日 {inp['hour']}:{inp['minute']:02d}",
        f"**八字：** {p['year']['gan']}{p['year']['zhi']} {p['month']['gan']}{p['month']['zhi']} {p['day']['gan']}{p['day']['zhi']} {p['hour']['gan']}{p['hour']['zhi']}",
        f"**性别：** {inp['gender']}　**属相：** {dm['shengxiao']}",
        f"**日主：** {dm['gan']}{dm['element']}",
        f"",
        f"*注：本排盘使用北京时间（UTC+8），未启用真太阳时校正。*",
        f"",
        f"---",
        f"",
        f"## 一、命盘排盘",
        f"",
        f"```",
        f"     年      月      日      时",
        f"    {p['year']['gan']}{p['year']['zhi']}    {p['month']['gan']}{p['month']['zhi']}    {p['day']['gan']}{p['day']['zhi']}    {p['hour']['gan']}{p['hour']['zhi']}",
        f"    {tg['year_gan']:4s}    {tg['month_gan']:4s}    日元    {tg['hour_gan']:4s}",
        f"```",
        f"",
        f"**十神：** 年干{tg['year_gan']}　月干{tg['month_gan']}　时干{tg['hour_gan']}",
        f"",
        f"**地支藏干：**",
        f"- 年支{p['year']['zhi']}藏：{' '.join(hs['year'])}",
        f"- 月支{p['month']['zhi']}藏：{' '.join(hs['month'])}",
        f"- 日支{p['day']['zhi']}藏：{' '.join(hs['day'])}",
        f"- 时支{p['hour']['zhi']}藏：{' '.join(hs['hour'])}",
        f"",
        f"**纳音：** {nayin['year']} → {nayin['month']} → {nayin['day']} → {nayin['hour']}",
        f"",
        f"## 二、五行与强弱",
        f"",
        f"**五行分布：** 木{wx['木']}　火{wx['火']}　土{wx['土']}　金{wx['金']}　水{wx['水']}",
        f"",
        f"**格局：** {sa['verdict']}",
        f"**喜用神：** {' '.join(sa['useful_elements']) if sa['useful_elements'] else '随大运变化'}",
        f"**忌神：** {' '.join(sa['harmful_elements']) if sa['harmful_elements'] else '随大运变化'}",
        f"",
        f"**判断依据：** {sa['reasoning']}",
        f"",
        f"## 三、大运排盘",
        f"",
        f"**大运方向：** {lk['direction']}",
        f"**起运年龄：** {lk['qiyun_age']['years']}岁{lk['qiyun_age']['months']}个月",
        f"",
    ]

    # 起运前（童限）
    if lk.get('pre_qiyun'):
        for cyc in lk['pre_qiyun']:
            lines.append(f"- [童限] {cyc['start_age']}-{cyc['end_age']}岁（起运前）")

    # 正式大运列表
    for i, cyc in enumerate(lk['cycles']):
        marker = ' ← 当前' if lk['current'] and cyc['ganzhi'] == lk['current']['ganzhi'] else ''
        lines.append(f"- {cyc['ganzhi']}　{cyc['start_age']}-{cyc['end_age']}岁{marker}")

    lines.extend([
        f"",
        f"## 四、流年运势",
        f"",
        f"**{af['year']}年流年：{af['ganzhi']}**",
        f"**天干十神：** {af['ten_god']}",
        f"",
        f"---",
        f"",
        f"> {chart['disclaimer']}",
    ])

    return '\n'.join(lines)
