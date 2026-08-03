#!/usr/bin/env python3
"""
占星命盘计算 — 基于出生日期/时间/地点输出完整星盘
用法: python xingpan.py 1989 6 28 5 30 林州
"""

import sys, math
import ephem
from datetime import datetime, timedelta

ZODIAC = ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']
ELEMENTS = {'白羊':'火','金牛':'土','双子':'风','巨蟹':'水','狮子':'火','处女':'土','天秤':'风','天蝎':'水','射手':'火','摩羯':'土','水瓶':'风','双鱼':'水'}
MODES = {'白羊':'开创','金牛':'固定','双子':'变动','巨蟹':'开创','狮子':'固定','处女':'变动','天秤':'开创','天蝎':'固定','射手':'变动','摩羯':'开创','水瓶':'固定','双鱼':'变动'}
PLANETS_CN = {'太阳':'核心自我','月亮':'情绪需求','水星':'思维沟通','金星':'爱情审美','火星':'行动竞争','木星':'幸运成长','土星':'责任课题','天王星':'创新独立','海王星':'梦想灵性','冥王星':'蜕变执念'}

SUN_MEANING = {
    '白羊':'精力充沛、行动力强、喜欢挑战。直接不拐弯。',
    '金牛':'稳重务实、重视安全感。对美和金钱敏感。',
    '双子':'好奇心强、思维敏捷、善于沟通。多面手。',
    '巨蟹':'情感丰富、重视家庭、直觉敏锐。会照顾人。',
    '狮子':'自信大方、有领导力、喜欢被关注。慷慨热情。',
    '处女':'细致认真、追求完美、逻辑清晰。做事有条理。',
    '天秤':'优雅得体、重视公平、善于协调。审美在线。',
    '天蝎':'洞察力强、情感深沉、意志坚定。爱憎分明。',
    '射手':'乐观开朗、热爱自由、喜欢探索。心胸开阔。',
    '摩羯':'踏实稳重、责任心强、目标明确。实干家。',
    '水瓶':'独立思考、有创新精神、重视朋友。不随大流。',
    '双鱼':'富有同情心、想象力丰富、直觉敏锐。艺术家。',
}

MOON_MEANING = {
    '白羊':'情绪来得快去得快。需要独立空间。',
    '金牛':'情绪稳定，需要安全感。通过身体接触感受爱。',
    '双子':'情绪多变，通过说话消化感受。',
    '巨蟹':'月亮入庙，情感极为丰富。家庭是情绪根基。',
    '狮子':'情感张扬，需要被认可。内心渴望被看见。',
    '处女':'情感内敛，用行动表达关心。对自己要求高。',
    '天秤':'追求关系和谐。需要陪伴。讨厌冲突。',
    '天蝎':'月亮落陷，情感深刻强烈。不轻易信任。',
    '射手':'情感乐观豁达。需要自由。用幽默化解。',
    '摩羯':'情感克制，不轻易表露。责任心重。',
    '水瓶':'情感独立，理性多于感性。需要朋友。',
    '双鱼':'情感细腻敏感，共情天赋。需独处充电。',
}

RISING_MEANING = {
    '白羊':'给人第一印象：直接、有活力。行动派。',
    '金牛':'第一印象：稳重、从容。看起来靠谱。',
    '双子':'第一印象：聪明、话多、灵活。永远年轻。',
    '巨蟹':'第一印象：温柔、亲和。自带家的感觉。',
    '狮子':'第一印象：自信、有气场。走哪都是焦点。',
    '处女':'第一印象：干净、低调、有礼貌。显小。',
    '天秤':'第一印象：优雅、好相处。自带社交光环。',
    '天蝎':'第一印象：深沉、神秘。不说话也有存在感。',
    '射手':'第一印象：开朗、大大咧咧。好接近。',
    '摩羯':'第一印象：严肃、可靠。比实际年龄成熟。',
    '水瓶':'第一印象：独特、有个性。不按常理出牌。',
    '双鱼':'第一印象：柔和、梦幻。需要被保护。',
}

CITY_COORDS = {
    '北京':(39.9,116.4),'上海':(31.2,121.5),'广州':(23.1,113.3),'深圳':(22.5,114.1),
    '成都':(30.6,104.1),'重庆':(29.5,106.5),'拉萨':(29.7,91.1),
    '林州':(36.1,113.8),'安阳':(36.1,114.4),'郑州':(34.8,113.6),'西安':(34.3,108.9),
    '武汉':(30.6,114.3),'南京':(32.1,118.8),'杭州':(30.3,120.2),'昆明':(25.0,102.7),
    '哈尔滨':(45.8,126.5),'乌鲁木齐':(43.8,87.6),'天津':(39.1,117.2),
    '长沙':(28.2,112.9),'济南':(36.7,117.0),'合肥':(31.8,117.3),'福州':(26.1,119.3),
    '南昌':(28.7,115.9),'南宁':(22.8,108.3),'贵阳':(26.6,106.7),'兰州':(36.1,103.8),
    '西宁':(36.6,101.8),'银川':(38.5,106.3),'呼和浩特':(40.8,111.7),'沈阳':(41.8,123.4),
    '长春':(43.8,125.3),'海口':(20.0,110.3),'香港':(22.3,114.2),'澳门':(22.2,113.5),
    '台北':(25.0,121.5),'河南':(34.8,113.6),'四川':(30.6,104.1),'西藏':(29.7,91.1),
}


def get_coords(place):
    for city, coords in CITY_COORDS.items():
        if city in place:
            return coords
    return (39.9, 116.4)


def calc_chart(year, month, day, hour, minute, place):
    lat, lon = get_coords(place)
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
        lon = math.degrees(ecl.lon) % 360
        idx = int(lon // 30)
        deg = lon % 30
        planets[name] = {'zodiac':ZODIAC[idx], 'degree':round(deg,1), 'index':idx, 'lon':round(lon,1)}

    # Rising sign (ASC) calculation
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

    return planets, rising, midheaven, asc_idx, mc_idx


def display_chart(planets, rising, midheaven, birth_info, place):
    print()
    print('+========================================+')
    print('|          占 星 命 盘                    |')
    print('+========================================+')
    print(f'|  出生：{birth_info}')
    print(f'|  地点：{place}')
    print('+========================================+')
    print(f'|  上升 ASC：{rising} ({ELEMENTS[rising]}象)')
    print(f'|  天顶  MC：{midheaven} ({ELEMENTS[midheaven]}象)')
    print('+========================================+')

    order = ['太阳','月亮','水星','金星','火星','木星','土星','天王星','海王星','冥王星']
    for name in order:
        p = planets[name]
        print(f'|  {name:5s} → {p["zodiac"]:3s} {p["degree"]:5.1f}度  |')

    print('+========================================+')
    print()

    sun = planets['太阳']
    moon = planets['月亮']

    print(f'[太阳星座] {sun["zodiac"]}座（{ELEMENTS[sun["zodiac"]]}象·{MODES[sun["zodiac"]]}）')
    print(f'  {SUN_MEANING[sun["zodiac"]]}')
    print()

    print(f'[月亮星座] {moon["zodiac"]}座')
    print(f'  {MOON_MEANING.get(moon["zodiac"], "")}')
    print()

    print(f'[上升星座] {rising}座')
    print(f'  {RISING_MEANING.get(rising, "")}')
    print()

    # 日月关系
    sun_el = ELEMENTS[sun['zodiac']]
    moon_el = ELEMENTS[moon['zodiac']]
    if sun['index'] == moon['index']:
        print('[日月关系] 日月同座——内外一致，性格统一。')
    elif sun_el == moon_el:
        print(f'[日月关系] 日月同{sun_el}象——外在和内在比较协调。')
    else:
        print(f'[日月关系] 日{sun_el}月{moon_el}——内外有拉扯，是成长的张力。')
    print()

    # 元素统计
    el_count = {'火':0,'土':0,'风':0,'水':0}
    for name in ['太阳','月亮','水星','金星','火星']:
        el_count[ELEMENTS[planets[name]['zodiac']]] += 1
    dominant = max(el_count, key=el_count.get)
    print(f'[元素主导] 个人行星中{dominant}元素最强，性格偏向：')
    if dominant == '火': print('  行动力强、热情直接。')
    elif dominant == '土': print('  务实稳重、耐久可靠。')
    elif dominant == '风': print('  头脑灵活、善于沟通。')
    elif dominant == '水': print('  情感丰富、直觉敏锐。')
    print()

    print('提示：将此星盘与八字命盘合并，可得「中西合璧」综合分析。')
    print('='*50)

    return {
        'sun': sun['zodiac'], 'moon': moon['zodiac'], 'rising': rising,
        'dominant': dominant,
    }


if __name__ == '__main__':
    if len(sys.argv) >= 5:
        year, month, day = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        if ':' in str(sys.argv[4]):
            h, m = sys.argv[4].split(':')
            hour, minute = int(h), int(m)
        else:
            hour, minute = int(sys.argv[4]), 0
        place = sys.argv[5] if len(sys.argv) > 5 else '北京'
        birth_info = f'{year}年{month}月{day}日 {hour}:{minute:02d}'
    else:
        print('用法: python xingpan.py 年 月 日 时:分 城市')
        print('示例: python xingpan.py 1989 6 28 5:30 林州')
        sys.exit(1)

    planets, rising, midheaven, asc_idx, mc_idx = calc_chart(year, month, day, hour, minute, place)
    display_chart(planets, rising, midheaven, birth_info, place)
