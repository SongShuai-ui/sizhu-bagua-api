# -*- coding: utf-8 -*-
"""黄金样例对照测试 — 20个权威排盘样例。

所有预期值均从 lunar-python 实际计算输出获取。
"""

import pytest
from src.engine import compute_bazi


def ps(chart, k):
    return f'{chart["pillars"][k]["gan"]}{chart["pillars"][k]["zhi"]}'


GOLDEN_CASES = [
    ('宋帅', 1989,6,28,5,30,'男', ('己巳','庚午','己未','丁卯'),'逆排', (6,9)),
    ('立春前-年柱上年', 2020,2,3,12,0,'男', ('己亥','丁丑','丙子','甲午'),'逆排', (8,11)),
    ('立春后-年柱新年', 2020,2,5,12,0,'男', ('庚子','戊寅','戊寅','戊午'),'顺排', (8,11)),
    ('惊蛰前-寅月', 2020,3,4,12,0,'女', ('庚子','戊寅','丙午','甲午'),'逆排', (8,11)),
    ('惊蛰后-卯月', 2020,3,6,12,0,'女', ('庚子','己卯','戊申','戊午'),'逆排', (-1,2)),
    ('早子时', 1990,1,1,0,30,'男', ('己巳','丙子','丙寅','戊子'),'逆排', (7,10)),
    ('午时', 1990,1,1,12,0,'男', ('己巳','丙子','丙寅','甲午'),'逆排', (7,10)),
    ('晚子时', 1990,1,1,23,30,'男', ('己巳','丙子','丙寅','庚子'),'逆排', (7,10)),
    ('阳年男顺排', 1984,6,1,12,0,'男', ('甲子','己巳','丙寅','甲午'),'顺排', (0,3)),
    ('阴年男逆排', 1985,6,1,12,0,'男', ('乙丑','辛巳','辛未','甲午'),'逆排', (7,10)),
    ('阳年女逆排', 1984,6,1,12,0,'女', ('甲子','己巳','丙寅','甲午'),'逆排', (7,10)),
    ('阴年女顺排', 1985,6,1,12,0,'女', ('乙丑','辛巳','辛未','甲午'),'顺排', (0,3)),
    ('甲木日主', 1984,2,4,8,0,'男', ('癸亥','乙丑','戊辰','丙辰'),'逆排', (8,11)),
    ('丙火日主', 1990,7,15,10,0,'女', ('庚午','癸未','辛巳','癸巳'),'逆排', (1,4)),
    ('庚金日主', 2000,9,10,14,0,'男', ('庚辰','乙酉','辛未','乙未'),'顺排', (8,11)),
    ('壬水日主', 2000,11,20,8,0,'女', ('庚辰','丁亥','壬午','甲辰'),'逆排', (3,6)),
    ('闰年2月29', 2000,2,29,10,0,'男', ('庚辰','戊寅','丁巳','乙巳'),'顺排', (0,3)),
    ('世纪之交', 2000,1,1,0,0,'男', ('己卯','丙子','戊午','壬子'),'逆排', (7,10)),
    ('2024元旦甲子日', 2024,1,1,12,0,'男', ('癸卯','甲子','甲子','庚午'),'逆排', (7,10)),
    ('2025春节', 2025,1,29,8,0,'女', ('甲辰','丁丑','戊戌','丙辰'),'逆排', (6,9)),

]


class TestGoldenCases:
    @pytest.mark.parametrize(
        'desc,year,month,day,hour,minute,gender,exp_pillars,exp_dir,qiyun_range',
        GOLDEN_CASES,
        ids=[c[0] for c in GOLDEN_CASES],
    )
    def test_four_pillars_match(self, desc, year, month, day, hour, minute,
                                 gender, exp_pillars, exp_dir, qiyun_range):
        chart = compute_bazi(year, month, day, hour, minute, gender)
        actual = (ps(chart,'year'), ps(chart,'month'),
                  ps(chart,'day'), ps(chart,'hour'))
        assert actual == exp_pillars,             f'{desc}: expected {exp_pillars}, got {actual}'

    @pytest.mark.parametrize(
        'desc,year,month,day,hour,minute,gender,exp_pillars,exp_dir,qiyun_range',
        GOLDEN_CASES,
        ids=[c[0] for c in GOLDEN_CASES],
    )
    def test_luck_direction_match(self, desc, year, month, day, hour, minute,
                                   gender, exp_pillars, exp_dir, qiyun_range):
        chart = compute_bazi(year, month, day, hour, minute, gender)
        assert chart['luck']['direction'] == exp_dir,             f'{desc}: expected {exp_dir}, got {chart["luck"]["direction"]}'

    @pytest.mark.parametrize(
        'desc,year,month,day,hour,minute,gender,exp_pillars,exp_dir,qiyun_range',
        GOLDEN_CASES,
        ids=[c[0] for c in GOLDEN_CASES],
    )
    def test_qiyun_in_range(self, desc, year, month, day, hour, minute,
                             gender, exp_pillars, exp_dir, qiyun_range):
        chart = compute_bazi(year, month, day, hour, minute, gender)
        qy = chart['luck']['qiyun_age']['years']
        lo, hi = qiyun_range
        assert lo <= qy <= hi,             f'{desc}: qiyun={qy} not in [{lo},{hi}]'


class TestReportSafety:
    HARMFUL = [
        '活不过', '短命', '夭折', '少年终', '早凋零',
        '癌症', '肿瘤', '心脏病', '绝症', '不治之症',
        '花钱消灾', '做法事', '转运符', '破财消灾',
    ]

    def test_no_harmful_content_in_report(self):
        from src.report import to_markdown
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        md = to_markdown(chart)
        body = md.split('---')[-2] if '---' in md else md
        for word in self.HARMFUL:
            assert word not in body, f'Harmful word found: {word}'

    def test_disclaimer_present(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert '仅供参考' in chart['disclaimer']
        assert '传统命理学' in chart['disclaimer']

    def test_no_fear_marketing(self):
        from src.report import to_markdown
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        md = to_markdown(chart)
        for f in ['必有大灾', '血光之灾', '破财免灾', '化解煞气']:
            assert f not in md, f'Fear phrase: {f}'

    def test_cycles_no_empty_ganzhi(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        for c in chart['luck']['cycles']:
            assert c['ganzhi'] != '', f'Empty ganzhi: {c}'

    def test_pre_qiyun_marked(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        pre = chart['luck']['pre_qiyun']
        if pre:
            assert 'note' in pre[0]
            assert '童限' in pre[0]['note']


class TestOutputStructure:
    REQUIRED = [
        'input', 'pillars', 'ten_gods', 'hidden_stems',
        'five_elements', 'day_master', 'nayin',
        'strength_analysis', 'luck', 'annual_fortune',
        'true_solar_time_used', 'disclaimer',
    ]

    def test_all_required_fields(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        for f in self.REQUIRED:
            assert f in chart, f'Missing: {f}'

    def test_true_solar_time_false(self):
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        assert chart['true_solar_time_used'] is False
