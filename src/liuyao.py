# -*- coding: utf-8 -*-
"""六爻预测模块 — 起卦、装卦、解卦。

支持铜钱随机摇卦和数字起卦两种方式。
"""

import random
from datetime import datetime
from .safety import DISCLAIMER
from .meihua import GUA64_MEANING, GUA64_INDEX

# 六十四卦：(卦名, 世爻位置, 所属宫, 宫五行)
GONG64 = {
    '乾为天':(1,'乾','金'),'天风姤':(1,'乾','金'),'天山遁':(2,'乾','金'),'天地否':(3,'乾','金'),
    '风地观':(4,'乾','金'),'山地剥':(5,'乾','金'),'火地晋':(4,'乾','金'),'火天大有':(3,'乾','金'),
    '坎为水':(1,'坎','水'),'水泽节':(1,'坎','水'),'水雷屯':(2,'坎','水'),'水火既济':(3,'坎','水'),
    '泽火革':(4,'坎','水'),'雷火丰':(5,'坎','水'),'地火明夷':(4,'坎','水'),'地水师':(3,'坎','水'),
    '艮为山':(1,'艮','土'),'山火贲':(1,'艮','土'),'山天大畜':(2,'艮','土'),'山泽损':(3,'艮','土'),
    '火泽睽':(4,'艮','土'),'天泽履':(5,'艮','土'),'风泽中孚':(4,'艮','土'),'风山渐':(3,'艮','土'),
    '震为雷':(1,'震','木'),'雷地豫':(1,'震','木'),'雷水解':(2,'震','木'),'雷风恒':(3,'震','木'),
    '地风升':(4,'震','木'),'水风井':(5,'震','木'),'泽风大过':(4,'震','木'),'泽雷随':(3,'震','木'),
    '巽为风':(1,'巽','木'),'风天小畜':(1,'巽','木'),'风火家人':(2,'巽','木'),'风雷益':(3,'巽','木'),
    '天雷无妄':(4,'巽','木'),'火雷噬嗑':(5,'巽','木'),'山雷颐':(4,'巽','木'),'山风蛊':(3,'巽','木'),
    '离为火':(1,'离','火'),'火山旅':(1,'离','火'),'火风鼎':(2,'离','火'),'火水未济':(3,'离','火'),
    '山水蒙':(4,'离','火'),'风水涣':(5,'离','火'),'天水讼':(4,'离','火'),'天火同人':(3,'离','火'),
    '坤为地':(1,'坤','土'),'地雷复':(1,'坤','土'),'地泽临':(2,'坤','土'),'地天泰':(3,'坤','土'),
    '雷天大壮':(4,'坤','土'),'泽天夬':(5,'坤','土'),'水天需':(4,'坤','土'),'水地比':(3,'坤','土'),
    '兑为泽':(1,'兑','金'),'泽水困':(1,'兑','金'),'泽地萃':(2,'兑','金'),'泽山咸':(3,'兑','金'),
    '水山蹇':(4,'兑','金'),'地山谦':(5,'兑','金'),'雷山小过':(4,'兑','金'),'雷泽归妹':(3,'兑','金'),
}

# 八卦阴阳爻 → 卦名
_YY_PATTERNS = {
    (True,True,True):'乾',(False,False,False):'坤',(False,True,False):'坎',(True,False,True):'离',
    (False,False,True):'震',(True,True,False):'巽',(False,True,True):'艮',(True,False,False):'兑',
}

_GUA_NAMES = {
    ('乾','乾'):'乾为天',('乾','巽'):'天风姤',('乾','艮'):'天山遁',('乾','坤'):'天地否',
    ('乾','坎'):'天水讼',('乾','震'):'天雷无妄',('乾','离'):'天火同人',('乾','兑'):'天泽履',
    ('巽','乾'):'风天小畜',('巽','巽'):'巽为风',('巽','艮'):'风山渐',('巽','坤'):'风地观',
    ('巽','坎'):'风水涣',('巽','震'):'风雷益',('巽','离'):'风火家人',('巽','兑'):'风泽中孚',
    ('艮','乾'):'山天大畜',('艮','巽'):'山风蛊',('艮','艮'):'艮为山',('艮','坤'):'山地剥',
    ('艮','坎'):'山水蒙',('艮','震'):'山雷颐',('艮','离'):'山火贲',('艮','兑'):'山泽损',
    ('坤','乾'):'地天泰',('坤','巽'):'地风升',('坤','艮'):'地山谦',('坤','坤'):'坤为地',
    ('坤','坎'):'地水师',('坤','震'):'地雷复',('坤','离'):'地火明夷',('坤','兑'):'地泽临',
    ('坎','乾'):'水天需',('坎','巽'):'水风井',('坎','艮'):'水山蹇',('坎','坤'):'水地比',
    ('坎','坎'):'坎为水',('坎','震'):'水雷屯',('坎','离'):'水火既济',('坎','兑'):'水泽节',
    ('震','乾'):'雷天大壮',('震','巽'):'雷风恒',('震','艮'):'雷山小过',('震','坤'):'雷地豫',
    ('震','坎'):'雷水解',('震','震'):'震为雷',('震','离'):'雷火丰',('震','兑'):'雷泽归妹',
    ('离','乾'):'火天大有',('离','巽'):'火风鼎',('离','艮'):'火山旅',('离','坤'):'火地晋',
    ('离','坎'):'火水未济',('离','震'):'火雷噬嗑',('离','离'):'离为火',('离','兑'):'火泽睽',
    ('兑','乾'):'泽天夬',('兑','巽'):'泽风大过',('兑','艮'):'泽山咸',('兑','坤'):'泽地萃',
    ('兑','坎'):'泽水困',('兑','震'):'泽雷随',('兑','离'):'泽火革',('兑','兑'):'兑为泽',
}

YAO_LABELS = ['初爻','二爻','三爻','四爻','五爻','上爻']
YONG_SHEN = {
    '财运':'妻财','事业':'官鬼','感情':'妻财(男)/官鬼(女)','考试':'父母','子女':'子孙','合作':'兄弟',
}

# 六爻动爻断辞
_YAO_MEANING = {
    1: '初爻为事之始，根基所在。动则根基有变，事情的起步阶段会有波折。',
    2: '二爻为事之中，发展之时。动则中途有变，事情的推进过程会出现转折。',
    3: '三爻为内卦之极，事将外显。动则内有不安，内部因素影响大局。',
    4: '四爻为外卦之始，近于上者。动则外力介入，外界因素开始起作用。',
    5: '五爻为尊位，事之主宰。动则主导力量变化，关键人物或核心条件有变动。',
    6: '上爻为事之终，结局所在。动则结局未定，最终结果仍有变数。',
}

_MOVING_COUNT_MEANING = {
    0: '静卦：六爻安静，事情短期内变化不大，保持现状，宜守不宜攻。',
    1: '一爻动：事情有明确的变动方向，动爻所在的位置指示了变化的具体领域。',
    2: '两爻动：事情存在两股力量拉扯，需要做出选择。看哪个动爻离世爻更近，取近者为用。',
    3: '三爻动：变化较多，内卦与外卦之间的平衡被打破。事情发展较为复杂。',
    4: '四爻动：变动剧烈，宜看变卦来判断整体走向。',
    5: '五爻动：几乎全部在变，事情处于剧烈动荡期。以变卦为主，本卦为辅来断。',
    6: '六爻全动：大变大动，旧事将去，新局将至。以变卦为最终判断。',
}


def _num_to_yao(n):
    m = {1:7,5:7, 2:9,6:9, 3:8,7:8, 0:6,4:6,8:6,9:6}
    return m.get(n % 10, 6)


def _yao_str(n):
    return {6:'老阴 X', 7:'少阳 -', 8:'少阴 --', 9:'老阳 O'}[n]


def _yy_to_name(yy):
    return _YY_PATTERNS.get(tuple(yy), '?')


def compute_liuyao(numbers: list = None, question: str = '') -> dict:
    """六爻起卦装卦。

    Args:
        numbers: 6个0-9数字（可选，不提供则随机铜钱起卦）
        question: 所问之事

    Returns:
        结构化 dict
    """
    if numbers and len(numbers) >= 6:
        yaos = [_num_to_yao(n) for n in numbers[:6]]
        method = '数字起卦'
    else:
        yaos = [random.choice([6,7,8,9]) for _ in range(6)]
        method = '铜钱随机起卦'

    yy = [(y in (7,9)) for y in yaos]
    upper_yy = (yy[5], yy[4], yy[3])
    lower_yy = (yy[2], yy[1], yy[0])
    shang = _yy_to_name(upper_yy)
    xia = _yy_to_name(lower_yy)
    gua_name = _GUA_NAMES.get((shang, xia), shang + xia + '卦')

    info = GONG64.get(gua_name)
    shi_yao = info[0] if info else None
    gong = info[1] if info else '?'
    gong_wx = info[2] if info else '?'

    # 应爻 = 世爻 + 3（隔两位）
    ying_yao = ((shi_yao + 2) % 6) if shi_yao else None
    if ying_yao == 0:
        ying_yao = 6

    yaos_detail = []
    for i in range(5, -1, -1):
        y = yaos[i]
        pos = i + 1
        shi_mark = '世' if pos == shi_yao else ''
        ying_mark = '应' if pos == ying_yao else ''
        yaos_detail.append({
            'position': pos,
            'label': YAO_LABELS[i],
            'value': y,
            'display': _yao_str(y),
            'is_moving': y in (6, 9),
            'shi_ying': (shi_mark + ying_mark) or '-',
        })

    moving = [(y['position'], y['value']) for y in yaos_detail if y['is_moving']]

    # 用神提示
    yongshen = ''
    for k, v in YONG_SHEN.items():
        if k in question:
            yongshen = v
            break

    # 卦义解读
    idx = GUA64_INDEX.get((xia, shang), 0)
    gua_meaning = GUA64_MEANING.get(idx, '卦义待查')

    # 动爻解读
    moving_analysis = _MOVING_COUNT_MEANING.get(len(moving), '')
    yao_details_analysis = [_YAO_MEANING.get(pos, '') for pos, _ in moving]

    # 问题定向
    yongshen_analysis = ''
    if len(moving) == 0:
        yongshen_analysis = '静卦宜守，不适合主动出击。如有明确计划，可等一等再行动。'
    elif len(moving) == 1:
        yongshen_analysis = '变动聚焦在一处，方向明确。按动爻的提示去推进。'
    elif len(moving) >= 5:
        yongshen_analysis = '变动太大，现在做决定为时过早。建议观望，等形势明朗。'
    else:
        yongshen_analysis = '多方变动，需要分清主次，抓住离世爻最近的动爻优先处理。'

    analysis = {
        'gua_meaning': gua_meaning,
        'moving_count_analysis': moving_analysis,
        'yao_analysis': yao_details_analysis,
        'overall_advice': yongshen_analysis,
    }

    return {
        'method': method,
        'question': question,
        'yaos': yaos_detail,
        'gua_name': gua_name,
        'gong': gong,
        'gong_wuxing': gong_wx,
        'shi_yao': shi_yao,
        'ying_yao': ying_yao,
        'moving_yaos': moving,
        'moving_count': len(moving),
        'yongshen': yongshen,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat(),
        'disclaimer': DISCLAIMER,
    }


def to_markdown(chart: dict) -> str:
    """六爻结果 → Markdown"""
    lines = [
        '# 六爻预测',
        '',
        f'**起卦方式：** {chart["method"]}',
        f'**卦名：** {chart["gua_name"]}（{chart["gong"]}宫·{chart["gong_wuxing"]}）',
        '',
        '## 六爻排盘',
        '',
    ]
    for y in chart['yaos']:
        marker = ''
        if '世' in y['shi_ying']:
            marker = ' ← 世爻'
        elif '应' in y['shi_ying']:
            marker = ' ← 应爻'
        lines.append(f'- {y["label"]}：{y["display"]}{marker}')

    lines.append('')
    if chart['moving_yaos']:
        lines.append(f'**动爻：** {len(chart["moving_yaos"])} 个')
        for pos, val in chart['moving_yaos']:
            t = '老阳→阴' if val == 9 else '老阴→阳'
            lines.append(f'- 第{pos}爻（{t}）')
    else:
        lines.append('**静卦：** 六爻安静，短期内变化不大。')

    if chart['yongshen']:
        lines.append(f'\n**用神：** {chart["yongshen"]}')

    # 解读
    if 'analysis' in chart:
        a = chart['analysis']
        lines.extend([
            '',
            '## 解卦',
            '',
            f'**卦义：** {a["gua_meaning"]}',
            '',
            f'**变动分析：** {a["moving_count_analysis"]}',
        ])
        if a.get('yao_analysis'):
            for yao_a in a['yao_analysis']:
                lines.append(f'- {yao_a}')
        lines.extend([
            '',
            f'**综合建议：** {a["overall_advice"]}',
        ])

    lines.extend([
        '',
        '---',
        f'> {chart["disclaimer"]}',
    ])
    return '\n'.join(lines)
