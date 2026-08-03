# -*- coding: utf-8 -*-
"""占星星盘计算模块 — 基于 ephem 天文库"""

import math
from datetime import datetime, timedelta
import ephem
from .safety import DISCLAIMER

ZODIAC = ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']
ELEMENTS = {'白羊':'火','金牛':'土','双子':'风','巨蟹':'水','狮子':'火','处女':'土','天秤':'风','天蝎':'水','射手':'火','摩羯':'土','水瓶':'风','双鱼':'水'}
MODES = {'白羊':'开创','金牛':'固定','双子':'变动','巨蟹':'开创','狮子':'固定','处女':'变动','天秤':'开创','天蝎':'固定','射手':'变动','摩羯':'开创','水瓶':'固定','双鱼':'变动'}

SUN_MEANING = {
    '白羊':'精力充沛、行动力强、喜欢挑战。','金牛':'稳重务实、重视安全感。','双子':'好奇心强、思维敏捷、善于沟通。',
    '巨蟹':'情感丰富、重视家庭、直觉敏锐。','狮子':'自信大方、有领导力、喜欢被关注。','处女':'细致认真、追求完美、逻辑清晰。',
    '天秤':'优雅得体、重视公平、善于协调。','天蝎':'洞察力强、情感深沉、意志坚定。','射手':'乐观开朗、热爱自由、喜欢探索。',
    '摩羯':'踏实稳重、责任心强、目标明确。','水瓶':'独立思考、有创新精神、重视朋友。','双鱼':'富有同情心、想象力丰富、直觉敏锐。',
}

MOON_MEANING = {
    '白羊':'情绪来得快去得快。','金牛':'情绪稳定，需要安全感。','双子':'情绪多变，通过说话消化感受。',
    '巨蟹':'月亮入庙，情感极为丰富。','狮子':'情感张扬，需要被认可。','处女':'情感内敛，用行动表达关心。',
    '天秤':'追求关系和谐。','天蝎':'月亮落陷，情感深刻强烈。','射手':'情感乐观豁达。',
    '摩羯':'情感克制，不轻易表露。','水瓶':'情感独立，理性多于感性。','双鱼':'情感细腻敏感，共情天赋。',
}

RISING_MEANING = {
    '白羊':'给人第一印象：直接、有活力。','金牛':'第一印象：稳重、从容。','双子':'第一印象：聪明、话多、灵活。',
    '巨蟹':'第一印象：温柔、亲和。','狮子':'第一印象：自信、有气场。','处女':'第一印象：干净、低调、有礼貌。',
    '天秤':'第一印象：优雅、好相处。','天蝎':'第一印象：深沉、神秘。','射手':'第一印象：开朗、大大咧咧。',
    '摩羯':'第一印象：严肃、可靠。','水瓶':'第一印象：独特、有个性。','双鱼':'第一印象：柔和、梦幻。',
}

CITY_COORDS = {
    '北京':(39.9,116.4),'上海':(31.2,121.5),'广州':(23.1,113.3),'深圳':(22.5,114.1),
    '成都':(30.6,104.1),'拉萨':(29.7,91.1),'林州':(36.1,113.8),'郑州':(34.8,113.6),
    '西安':(34.3,108.9),'武汉':(30.6,114.3),'南京':(32.1,118.8),'杭州':(30.3,120.2),
    '昆明':(25.0,102.7),'哈尔滨':(45.8,126.5),'河南':(34.8,113.6),'四川':(30.6,104.1),
}


def _get_coords(place):
    for city, coords in CITY_COORDS.items():
        if city in place:
            return coords
    return (39.9, 116.4)


def compute_xingpan(year: int, month: int, day: int, hour: int, minute: int = 0, birthplace: str = '') -> dict:
    """计算占星星盘。

    Returns:
        结构化 dict，含行星位置、上升/天顶、日月关系、元素分布
    """
    lat, lon = _get_coords(birthplace)
    dt_cst = datetime(year, month, day, hour, minute)
    dt_utc = dt_cst - timedelta(hours=8)

    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = dt_utc
    obs.pressure = 0

    bodies = {
        '太阳':ephem.Sun(),'月亮':ephem.Moon(),'水星':ephem.Mercury(),
        '金星':ephem.Venus(),'火星':ephem.Mars(),'木星':ephem.Jupiter(),
        '土星':ephem.Saturn(),'天王星':ephem.Uranus(),'海王星':ephem.Neptune(),
        '冥王星':ephem.Pluto(),
    }

    planets = {}
    for name, body in bodies.items():
        body.compute(obs)
        ecl = ephem.Ecliptic(body)
        lon_deg = math.degrees(ecl.lon) % 360
        idx = int(lon_deg // 30)
        deg = round(lon_deg % 30, 1)
        planets[name] = {
            'zodiac': ZODIAC[idx],
            'degree': deg,
            'element': ELEMENTS[ZODIAC[idx]],
            'mode': MODES[ZODIAC[idx]],
        }

    # ASC / MC
    sidereal = obs.sidereal_time()
    st_deg = math.degrees(sidereal) % 360
    obl = math.radians(23.439291)
    lat_rad = math.radians(lat)

    asc_deg = math.degrees(math.atan2(
        -math.cos(math.radians(st_deg)),
        math.sin(math.radians(st_deg)) * math.cos(obl) + math.tan(lat_rad) * math.sin(obl)
    )) % 360
    mc_deg = math.degrees(math.atan2(
        math.sin(math.radians(st_deg)),
        math.cos(math.radians(st_deg)) * math.cos(obl)
    )) % 360

    asc_idx = int(asc_deg // 30)
    mc_idx = int(mc_deg // 30)
    rising = ZODIAC[asc_idx]
    midheaven = ZODIAC[mc_idx]

    # 日月关系
    sun_el = ELEMENTS[planets['太阳']['zodiac']]
    moon_el = ELEMENTS[planets['月亮']['zodiac']]
    sun_idx = ZODIAC.index(planets['太阳']['zodiac'])
    moon_idx = ZODIAC.index(planets['月亮']['zodiac'])
    if sun_idx == moon_idx:
        sun_moon = '日月同座，内外一致'
    elif sun_el == moon_el:
        sun_moon = f'日月同{sun_el}象，较为协调'
    else:
        sun_moon = f'日{sun_el}月{moon_el}，内外有拉扯'

    # 元素统计（个人行星：日月水金火）
    el_count = {'火':0,'土':0,'风':0,'水':0}
    for name in ['太阳','月亮','水星','金星','火星']:
        el_count[ELEMENTS[planets[name]['zodiac']]] += 1
    dominant = max(el_count, key=el_count.get)

    return {
        'input': {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'birthplace': birthplace},
        'true_solar_time_used': False,
        'ascendant': {'zodiac': rising, 'element': ELEMENTS[rising]},
        'midheaven': {'zodiac': midheaven, 'element': ELEMENTS[midheaven]},
        'planets': planets,
        'sun_moon_relation': sun_moon,
        'dominant_element': dominant,
        'element_distribution': el_count,
        'disclaimer': DISCLAIMER,
    }


def to_markdown(chart: dict) -> str:
    """星盘结果 → Markdown"""
    p = chart['planets']
    asc = chart['ascendant']
    lines = [
        '# 占星星盘',
        '',
        f'**出生：** {chart["input"]["year"]}年{chart["input"]["month"]}月{chart["input"]["day"]}日 {chart["input"]["hour"]}:{chart["input"]["minute"]:02d}',
        f'**地点：** {chart["input"]["birthplace"] or "未指定"}',
        f'**上升 ASC：** {asc["zodiac"]}座（{asc["element"]}象）',
        f'**天顶 MC：** {chart["midheaven"]["zodiac"]}座',
        '',
        '*注：使用北京时间（UTC+8），未启用真太阳时校正。*',
        '',
        '## 行星位置',
        '',
    ]
    for name in ['太阳','月亮','水星','金星','火星','木星','土星','天王星','海王星','冥王星']:
        pp = p[name]
        lines.append(f'- **{name}：** {pp["zodiac"]}座 {pp["degree"]}度（{pp["element"]}象·{pp["mode"]}）')

    lines.extend([
        '',
        '## 解读',
        '',
        f'**太阳星座：** {p["太阳"]["zodiac"]}座 — {SUN_MEANING[p["太阳"]["zodiac"]]}',
        f'**月亮星座：** {p["月亮"]["zodiac"]}座 — {MOON_MEANING.get(p["月亮"]["zodiac"], "")}',
        f'**上升星座：** {asc["zodiac"]}座 — {RISING_MEANING.get(asc["zodiac"], "")}',
        f'**日月关系：** {chart["sun_moon_relation"]}',
        f'**主导元素：** {chart["dominant_element"]}',
        '',
        '---',
        f'> {chart["disclaimer"]}',
    ])
    return '\n'.join(lines)
