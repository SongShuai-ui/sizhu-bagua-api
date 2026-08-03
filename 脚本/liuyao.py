#!/usr/bin/env python3
"""
六爻预测起卦 + 装卦脚本
铜钱摇卦法，自动装六亲六兽世应
"""

import sys, random
from datetime import datetime

# ===== 基础数据 =====
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
WX_MAP = {  # 地支五行
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水',
}

# 八卦（乾坎艮震巽离坤兑）
# 每卦：(卦名, 五行, 初爻到上爻的地支)
BAGUA_DATA = {
    '乾': ('金', ['子','寅','辰','午','申','戌']),
    '坎': ('水', ['寅','辰','午','申','戌','子']),
    '艮': ('土', ['辰','午','申','戌','子','寅']),
    '震': ('木', ['子','寅','辰','午','申','戌']),
    '巽': ('木', ['丑','亥','酉','未','巳','卯']),
    '离': ('火', ['卯','丑','亥','酉','未','巳']),
    '坤': ('土', ['未','巳','卯','丑','亥','酉']),
    '兑': ('金', ['巳','卯','丑','亥','酉','未']),
}

# 八宫六十四卦 - (卦名, 世爻位置1-6, 所属宫)
GONG64 = {
    # 乾宫八卦
    '乾为天': (1, '乾'), '天风姤': (1, '乾'), '天山遁': (2, '乾'), '天地否': (3, '乾'),
    '风地观': (4, '乾'), '山地剥': (5, '乾'), '火地晋': (4, '乾'), '火天大有': (3, '乾'),
    # 坎宫八卦
    '坎为水': (1, '坎'), '水泽节': (1, '坎'), '水雷屯': (2, '坎'), '水火既济': (3, '坎'),
    '泽火革': (4, '坎'), '雷火丰': (5, '坎'), '地火明夷': (4, '坎'), '地水师': (3, '坎'),
    # 艮宫八卦
    '艮为山': (1, '艮'), '山火贲': (1, '艮'), '山天大畜': (2, '艮'), '山泽损': (3, '艮'),
    '火泽睽': (4, '艮'), '天泽履': (5, '艮'), '风泽中孚': (4, '艮'), '风山渐': (3, '艮'),
    # 震宫八卦
    '震为雷': (1, '震'), '雷地豫': (1, '震'), '雷水解': (2, '震'), '雷风恒': (3, '震'),
    '地风升': (4, '震'), '水风井': (5, '震'), '泽风大过': (4, '震'), '泽雷随': (3, '震'),
    # 巽宫八卦
    '巽为风': (1, '巽'), '风天小畜': (1, '巽'), '风火家人': (2, '巽'), '风雷益': (3, '巽'),
    '天雷无妄': (4, '巽'), '火雷噬嗑': (5, '巽'), '山雷颐': (4, '巽'), '山风蛊': (3, '巽'),
    # 离宫八卦
    '离为火': (1, '离'), '火山旅': (1, '离'), '火风鼎': (2, '离'), '火水未济': (3, '离'),
    '山水蒙': (4, '离'), '风水涣': (5, '离'), '天水讼': (4, '离'), '天火同人': (3, '离'),
    # 坤宫八卦
    '坤为地': (1, '坤'), '地雷复': (1, '坤'), '地泽临': (2, '坤'), '地天泰': (3, '坤'),
    '雷天大壮': (4, '坤'), '泽天夬': (5, '坤'), '水天需': (4, '坤'), '水地比': (3, '坤'),
    # 兑宫八卦
    '兑为泽': (1, '兑'), '泽水困': (1, '兑'), '泽地萃': (2, '兑'), '泽山咸': (3, '兑'),
    '水山蹇': (4, '兑'), '地山谦': (5, '兑'), '雷山小过': (4, '兑'), '雷泽归妹': (3, '兑'),
}

# ===== 起卦 =====

def yao_to_str(n):
    """将爻值转为显示字符"""
    return {6:'- X 老阴', 7:'- — 少阳', 8:'- - - 少阴', 9:'- O 老阳'}[n]

def yao_to_yin_yang(n):
    """爻值 → 阴阳 (True=阳, False=阴)"""
    return n in (7, 9)

def shake_yao():
    """铜钱摇一爻（三枚铜钱）"""
    coins = [random.choice([2, 3]) for _ in range(3)]  # 2=阴面,3=阳面
    total = sum(coins)
    # 6=老阴(变爻), 7=少阳, 8=少阴, 9=老阳(变爻)
    return total

def number_to_yao(n):
    """数字转爻：0-9的数字 → 四象爻值
       1,5 → 少阳(7)  3,7 → 少阴(8)
       2,6 → 老阳(9)  0,4,8,9 → 老阴(6)
    """
    n = n % 10
    if n in (1, 5):
        return 7   # 少阳 —
    elif n in (2, 6):
        return 9   # 老阳 O → 变爻
    elif n in (3, 7):
        return 8   # 少阴 - -
    else:  # 0, 4, 8, 9
        return 6   # 老阴 X → 变爻

def qigua_yao(method='shake'):
    """起卦：铜钱摇卦 或 数字起卦"""
    if method == 'shake':
        return [shake_yao() for _ in range(6)]
    return None

def qigua_by_numbers(nums):
    """6个数字起卦法（0-9），从初爻到上爻"""
    if len(nums) != 6:
        nums = (list(nums) + [0]*6)[:6]
    return [number_to_yao(n) for n in nums]

# ===== 装卦 =====

def get_gua_from_yaos(yaos):
    """根据六爻阴阳得上下卦名和世应宫"""
    # 上卦（外卦）：上三爻 4,5,6
    # 下卦（内卦）：下三爻 1,2,3（初爻=index 0）
    upper_yin_yang = [yao_to_yin_yang(yaos[i]) for i in range(3, 6)]  # 上卦
    lower_yin_yang = [yao_to_yin_yang(yaos[i]) for i in range(3)]     # 下卦

    # 八卦阴阳爻组合 → 卦名
    def yin_yang_to_gua(yy_list):
        """将三爻阴阳转为卦名"""
        # 乾坤坎离震巽艮兑
        patterns = {
            (True, True, True): '乾',
            (False, False, False): '坤',
            (False, True, False): '坎',
            (True, False, True): '离',
            (False, False, True): '震',
            (True, True, False): '巽',
            (False, True, True): '艮',
            (True, False, False): '兑',
        }
        return patterns.get(tuple(yy_list), '?')

    upper_gua = yin_yang_to_gua(upper_yin_yang)
    lower_gua = yin_yang_to_gua(lower_yin_yang)

    return upper_gua, lower_gua


def load_gua(yaos):
    """装卦：定卦名、世应、宫、六亲"""
    full_yin_yang = [yao_to_yin_yang(y) for y in yaos]

    # 找卦名
    upper = (full_yin_yang[5], full_yin_yang[4], full_yin_yang[3])  # 上卦从上到下
    lower = (full_yin_yang[2], full_yin_yang[1], full_yin_yang[0])  # 下卦从上到下

    def yy_to_name(yy):
        patterns = {
            (True, True, True): '乾', (False, False, False): '坤',
            (False, True, False): '坎', (True, False, True): '离',
            (False, False, True): '震', (True, True, False): '巽',
            (False, True, True): '艮', (True, False, False): '兑',
        }
        return patterns.get(yy, '?')

    shang_name = yy_to_name(upper)
    xia_name = yy_to_name(lower)

    # 卦名映射
    gua_name_map = {
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

    gua_name = gua_name_map.get((shang_name, xia_name), f'{shang_name}{xia_name}卦')

    info = GONG64.get(gua_name, (None, '?'))
    shi_yao, gong = info if info[0] else (None, '?')

    return gua_name, shi_yao, gong, shang_name, xia_name


# ===== 输出 =====

def display(yaos, gua_name, shi_yao, gong):
    """显示六爻纳甲装卦结果"""
    gong_wx = BAGUA_DATA.get(gong, ('?', []))[0]
    yao_labels = ['初爻','二爻','三爻','四爻','五爻','上爻']

    print()
    print('+===============================+')
    print('|      六  爻  预  测            |')
    print('+===============================+')
    print(f'|  卦名：{gua_name}（{gong}宫·{gong_wx}）')
    print(f'|  时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('+===============================+')

    # 从上到下显示（上爻→初爻）
    for i in range(5, -1, -1):
        yao_str = yao_to_str(yaos[i])
        label = yao_labels[i]
        shi_mark = ' ← 世爻' if shi_yao == i+1 else ''
        ying_mark = ''
        if shi_yao:
            ying = (shi_yao + 2) % 6
            if ying == 0: ying = 6
            if ying == i+1:
                ying_mark = ' ← 应爻'
        print(f'|  {label}: {yao_str}{shi_mark}{ying_mark}')

    print('+===============================+')
    print()

    # 用神提示
    print('【用神定位】')
    print(f'  问财运 → 以妻财为用神')
    print(f'  问事业 → 以官鬼为用神')
    print(f'  问感情 → 以妻财(男)/官鬼(女)为用神')
    print(f'  问考试 → 以父母为用神')
    print(f'  问子女 → 以子孙为用神')
    print(f'  问合作 → 以兄弟为用神')
    print()

    # 变爻提示
    bian_yaos = [(i+1, y) for i, y in enumerate(yaos) if y in (6, 9)]
    if bian_yaos:
        print('【动爻提示】')
        for pos, val in bian_yaos:
            t = '老阳→阴' if val == 9 else '老阴→阳'
            print(f'  第{pos}爻动（{t}）——这是关键变化点')
    else:
        print('【静卦】六爻安静，事情短期内不会有大变化。')
    print()


# ===== 主程序 =====

def run(q='', nums=None):
    if nums:
        yaos = qigua_by_numbers(nums)
    else:
        yaos = qigua_yao()

    gua_name, shi_yao, gong, shang, xia = load_gua(yaos)
    display(yaos, gua_name, shi_yao, gong)

    if q:
        print(f'  === 针对「{q}」的分析 ===')
        bian_count = sum(1 for y in yaos if y in (6,9))
        if bian_count == 0:
            print(f'  六爻皆静，事情稳定。{gua_name}主静守，不宜大动。')
        elif bian_count >= 3:
            print(f'  {bian_count}个动爻，变数较多。可以重新确认一下。')
        else:
            print(f'  {bian_count}个动爻，变化可控。注意动爻位置对应的时机。')
    print()
    print('提示：将以上卦象发给AI解卦，可得详细分析。')
    print('='*50)


if __name__ == '__main__':
    if len(sys.argv) >= 7:
        # 6个数字起卦
        nums = [int(x) for x in sys.argv[1:7]]
        q = sys.argv[7] if len(sys.argv) > 7 else ''
        run(q, nums)
    elif len(sys.argv) > 1 and sys.argv[1] == 'q':
        q = sys.argv[2] if len(sys.argv) > 2 else ''
        run(q)
    else:
        print('用法1: python liuyao.py q "想问的事"  (铜钱随机摇卦)')
        print('用法2: python liuyao.py 3 6 9 1 5 8 "想问的事"  (报6个数字起卦)')
        q = input('想问什么？: ').strip()
        mode = input('有6个数字吗？（直接回车=随机摇卦，输入6个数字空格分隔）: ').strip()
        if mode and len(mode.split()) == 6:
            nums = [int(x) for x in mode.split()]
            run(q, nums)
        else:
            run(q)
