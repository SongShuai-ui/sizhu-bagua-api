#!/usr/bin/env python3
"""
梅花易数起卦 + 解卦脚本
支持：年月日时起卦 / 数字起卦 / 随机起卦
"""

import sys
from datetime import datetime

# ===== 八卦 =====
# 乾兑离震巽坎艮坤
GUA = {
    1: ('乾', '天', '==', '金'),
    2: ('兑', '泽', '--', '金'),
    3: ('离', '火', '=-', '火'),
    4: ('震', '雷', '==', '木'),
    5: ('巽', '风', '--', '木'),
    6: ('坎', '水', '-=', '水'),
    7: ('艮', '山', '--', '土'),
    8: ('坤', '地', '==', '土'),
}

# 六十四卦表（上卦, 下卦 → 卦名）
# 上卦为外卦，下卦为内卦
GUA64_INDEX = {
    (1,1):1,(1,2):43,(1,3):14,(1,4):34,(1,5):9,(1,6):5,(1,7):26,(1,8):11,
    (2,1):10,(2,2):58,(2,3):38,(2,4):54,(2,5):61,(2,6):60,(2,7):41,(2,8):19,
    (3,1):13,(3,2):49,(3,3):30,(3,4):55,(3,5):37,(3,6):63,(3,7):22,(3,8):36,
    (4,1):25,(4,2):17,(4,3):21,(4,4):51,(4,5):42,(4,6):3,(4,7):27,(4,8):24,
    (5,1):44,(5,2):28,(5,3):50,(5,4):32,(5,5):57,(5,6):48,(5,7):18,(5,8):46,
    (6,1):6,(6,2):47,(6,3):64,(6,4):40,(6,5):59,(6,6):29,(6,7):4,(6,8):7,
    (7,1):33,(7,2):31,(7,3):56,(7,4):62,(7,5):53,(7,6):39,(7,7):52,(7,8):15,
    (8,1):12,(8,2):45,(8,3):35,(8,4):16,(8,5):20,(8,6):8,(8,7):23,(8,8):2,
}

# 六十四卦名称
GUA64_NAMES = {
    1:'乾为天',2:'坤为地',3:'水雷屯',4:'山水蒙',5:'水天需',6:'天水讼',7:'地水师',
    8:'水地比',9:'风天小畜',10:'天泽履',11:'地天泰',12:'天地否',13:'天火同人',
    14:'火天大有',15:'地山谦',16:'雷地豫',17:'泽雷随',18:'山风蛊',19:'地泽临',
    20:'风地观',21:'火雷噬嗑',22:'山火贲',23:'山地剥',24:'地雷复',25:'天雷无妄',
    26:'山天大畜',27:'山雷颐',28:'泽风大过',29:'坎为水',30:'离为火',31:'泽山咸',
    32:'雷风恒',33:'天山遁',34:'雷天大壮',35:'火地晋',36:'地火明夷',37:'风火家人',
    38:'火泽睽',39:'水山蹇',40:'雷水解',41:'山泽损',42:'风雷益',43:'泽天夬',
    44:'天风姤',45:'泽地萃',46:'地风升',47:'泽水困',48:'水风井',49:'泽火革',
    50:'火风鼎',51:'震为雷',52:'艮为山',53:'风山渐',54:'雷泽归妹',55:'雷火丰',
    56:'火山旅',57:'巽为风',58:'兑为泽',59:'风水涣',60:'水泽节',61:'风泽中孚',
    62:'雷山小过',63:'水火既济',64:'火水未济',
}

# 六十四卦简义
GUA64_MEANING = {
    1:'纯阳之卦，刚健不息。问事业大吉，问感情需柔克刚。',
    2:'纯阴之卦，厚德载物。宜守不宜攻，以柔顺应事。',
    3:'万事初生，困难重重。需要耐心，不可急于求成。',
    4:'蒙昧初开，需要指引。求人不如求师，问路不如问心。',
    5:'等待时机，不可强求。时机未到，妄动则凶。',
    6:'口舌是非，争论不休。退一步海阔天空。',
    7:'统兵之象，需要组织。借助团队力量方能成事。',
    8:'亲附和合，吉。人际和谐，合作顺利。',
    9:'积蓄力量，小有成就。不可贪大，稳扎稳打。',
    10:'如履薄冰，谨慎行事。守规矩，不越界。',
    11:'天地交泰，万事亨通。最好的卦之一。',
    12:'天地不交，阻塞不通。忍耐等待，自有转机。',
    13:'志同道合，同心协力。适合合作、交友、婚恋。',
    14:'大有收获，丰收之象。财运事业皆吉。',
    15:'谦虚受益，骄傲受损。保持低调，自有好运。',
    16:'愉悦安乐，顺势而行。适合出行、变动。',
    17:'随缘而行，不可强求。顺其自然为上。',
    18:'积弊需除，改革整顿。旧的不去新的不来。',
    19:'好运将至，日渐光明。事业感情都在上升期。',
    20:'观察等待，不可贸进。多看了再说。',
    21:'受阻难行，需要突破。咬紧牙关挺过去。',
    22:'外表光鲜，内在需修。不宜只做表面功夫。',
    23:'根基动摇，小人当道。守住底线，不要硬抗。',
    24:'一阳来复，否极泰来。最困难的时候已经过去。',
    25:'真实不虚，不可投机。诚实是最好的策略。',
    26:'积蓄大能量，待时而动。准备越充分越好。',
    27:'养精蓄锐，自食其力。靠自己最可靠。',
    28:'负担过重，需要减负。不要硬撑。',
    29:'险难重重，需有信念。越是困难越要稳住。',
    30:'光明依附，需要依托。找对平台、跟对人。',
    31:'感应和合，感情融洽。婚姻恋爱大吉之卦。',
    32:'恒久不变，坚持到底。适合长线投资、稳定感情。',
    33:'退避三舍，以退为进。暂时撤退是策略。',
    34:'强盛壮大，不可逞强。盛极必衰，适可而止。',
    35:'旭日东升，前途光明。升职加薪，步步高升。',
    36:'光明受损，韬光养晦。不要出风头，低调做人。',
    37:'家庭和睦，各安其位。先把家里的事处理好。',
    38:'意见不合，各执一词。多沟通少争执。',
    39:'前路艰难，需要绕行。此路不通换一条。',
    40:'困难解除，万物复苏。终于可以松口气了。',
    41:'有损有益，损小得大。舍得舍得，有舍有得。',
    42:'受益进步，利有攸往。大胆往前，收获在望。',
    43:'决断果断，当断则断。犹豫只会坏事。',
    44:'不期而遇，意外之缘。桃花之卦，注意分寸。',
    45:'聚集荟萃，团结力量。抱团才能成事。',
    46:'步步高升，积少成多。不要急，慢慢来。',
    47:'被困受制，守时待变。不要挣扎，等待转机。',
    48:'滋养万物，源源不断。稳是最大的优势。',
    49:'改革变革，除旧布新。不要怕变化。',
    50:'革故鼎新，建功立业。适合创业、转型、换工作。',
    51:'雷霆震动，突发变故。冷静应对，不要慌乱。',
    52:'稳重如山，不宜妄动。守住本位就是胜利。',
    53:'循序渐进，不可冒进。慢就是快。',
    54:'名不正则言不顺。注意关系定位，避免越界。',
    55:'丰盛盈满，盛极必衰。顶峰时期要想到下落。',
    56:'客居在外，漂泊不定。适合外出、旅行、迁移。',
    57:'柔顺进入，潜移默化。以柔克刚，慢慢影响。',
    58:'喜悦交流，口才得力。适合谈判、销售、表白。',
    59:'涣散需要凝聚。散则不利，聚则有成。',
    60:'节制有度，过犹不及。控制好自己的节奏。',
    61:'诚信为本，言行一致。诚实赢得信任。',
    62:'小有过越，宜小不宜大。小事可为，大事停。',
    63:'圆满成功，但需防变。完美之后是下坡。',
    64:'未完成，还需努力。黎明前的黑暗，继续走。',
}

# 五行生克
WX = {'金':0,'水':1,'木':2,'火':3,'土':4}
# 生：我生者为 WX[(i+1)%5]，生我者为 WX[(i-1)%5]
# 克：我克者为 WX[(i+2)%5]，克我者为 WX[(i-2)%5]
def wx_sheng(wx): return list(WX.keys())[(WX[wx]+1)%5]  # 我生
def wx_ke(wx): return list(WX.keys())[(WX[wx]+2)%5]     # 我克
def wx_sheng_wo(wx): return list(WX.keys())[(WX[wx]-1)%5]  # 生我
def wx_ke_wo(wx): return list(WX.keys())[(WX[wx]-2)%5]     # 克我

# ===== 起卦方法 =====

def num_to_gua(n):
    """数字转八卦（1乾2兑3离4震5巽6坎7艮8坤）"""
    n = n % 8
    if n == 0: n = 8
    return n

def num_to_yao(n):
    """数字转动爻（1-6）"""
    n = n % 6
    if n == 0: n = 6
    return n


def qigua_by_date(year=None, month=None, day=None, hour=None):
    """年月日时起卦法"""
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    day = day or now.day
    hour = hour or now.hour

    # 上卦：(年+月+日) % 8
    shang = num_to_gua(year + month + day)
    # 下卦：(年+月+日+时) % 8
    xia = num_to_gua(year + month + day + hour)
    # 动爻：(年+月+日+时) % 6
    dong = num_to_yao(year + month + day + hour)

    return shang, xia, dong


def qigua_by_numbers(a, b, c):
    """三个数字起卦法"""
    shang = num_to_gua(a)
    xia = num_to_gua(b)
    dong = num_to_yao(c)
    return shang, xia, dong


def qigua_by_two(a, b):
    """两个数字起卦法（动爻取两数之和）"""
    shang = num_to_gua(a)
    xia = num_to_gua(b)
    dong = num_to_yao(a + b)
    return shang, xia, dong


# ===== 卦象推演 =====

def get_bengua(shang, xia):
    """本卦"""
    idx = GUA64_INDEX[(shang, xia)]
    return idx

def get_hugua(bengua_idx):
    """互卦：本卦2-4爻为下卦，3-5爻为上卦"""
    # 将卦序号转为六爻（二进制），取2-4和3-5爻
    # 简化：用查表法
    # 六十四卦序号 → 互卦序号（标准映射）
    hugua_map = {
        1:1,2:2,3:24,4:27,5:38,6:37,7:24,8:23,9:38,10:37,11:54,12:53,13:1,14:43,15:24,16:39,
        17:53,18:54,19:24,20:23,21:39,22:24,23:2,24:2,25:53,26:54,27:2,28:1,29:27,30:28,
        31:44,32:28,33:44,34:28,35:39,36:40,37:63,38:64,39:63,40:64,41:24,42:27,43:1,44:1,
        45:53,46:54,47:37,48:38,49:28,50:44,51:39,52:40,53:64,54:63,55:28,56:44,57:38,58:37,
        59:27,60:24,61:27,62:28,63:64,64:63,
    }
    return hugua_map.get(bengua_idx, bengua_idx)

def get_biangua(bengua_idx, dong_yao):
    """变卦：动爻位置取反"""
    # 将变卦前后的六十四卦映射直接计算
    # binary representation: 本卦 → flip one bit → 变卦
    bin_gua = bengua_idx - 1  # 0-63
    bit_pos = 5 - (dong_yao - 1)  # 动爻对应二进制位(5=初爻, 0=上爻)
    bin_bian = bin_gua ^ (1 << bit_pos)
    return bin_bian + 1

def get_tiyong(bengua_idx, dong_yao):
    """体用分析：动爻在下卦→下卦为用,上卦为体；动爻在上卦→上卦为用,下卦为体"""
    shang_gua_idx = (bengua_idx - 1) // 8 + 1  # 上卦
    xia_gua_idx = (bengua_idx - 1) % 8 + 1     # 下卦
    if dong_yao <= 3:
        # 动爻在下卦
        ti_gua = shang_gua_idx
        yong_gua = xia_gua_idx
    else:
        ti_gua = xia_gua_idx
        yong_gua = shang_gua_idx
    return ti_gua, yong_gua


def analyze_tiyong(ti, yong):
    """体用生克分析"""
    ti_wx = GUA[ti][3]
    yong_wx = GUA[yong][3]

    if ti_wx == yong_wx:
        return '比和', '体用五行相同，吉。事情顺利，心想事成。'
    if wx_sheng_wo(ti_wx) == yong_wx:
        return '用生体（大吉）', f'用卦({yong_wx})生体卦({ti_wx})。凡事顺遂，有贵人相助，财运感情皆利。'
    if wx_sheng(ti_wx) == yong_wx:
        return '体生用（耗泄）', f'体卦({ti_wx})生用卦({yong_wx})。需要付出很多，事情能成但很累。感情上你爱对方更多。'
    if wx_ke_wo(ti_wx) == yong_wx:
        return '用克体（凶）', f'用卦({yong_wx})克体卦({ti_wx})。事情不顺，阻力大，需谨慎行事。'
    if wx_ke(ti_wx) == yong_wx:
        return '体克用（小吉）', f'体卦({ti_wx})克用卦({yong_wx})。事可成但费心力，需要坚持才能成功。'


def generate_report(shang, xia, dong, question=''):
    """生成完整梅花易数报告"""
    bengua = get_bengua(shang, xia)
    hugua = get_hugua(bengua)
    biangua = get_biangua(bengua, dong)
    ti, yong = get_tiyong(bengua, dong)
    result, desc = analyze_tiyong(ti, yong)

    shang_gua = GUA[shang]
    xia_gua = GUA[xia]

    print()
    print('+==================================+')
    print('|       梅 花 易 数 占 卜           |')
    print('+==================================+')
    if question:
        print(f'|  所问：{question}')
    print(f'|  起卦时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('+==================================+')
    print(f'|                                  |')
    print(f'|  上卦：{shang_gua[2]} {shang_gua[0]}（{shang_gua[1]}）属{shang_gua[3]}')
    print(f'|  下卦：{xia_gua[2]} {xia_gua[0]}（{xia_gua[1]}）属{xia_gua[3]}')
    print(f'|  动爻：第{dong}爻动')
    print(f'|                                  |')
    print('+==================================+')
    print(f'|                                  |')
    print(f'|  本卦：{GUA64_NAMES[bengua]}')
    print(f'|  互卦：{GUA64_NAMES[hugua]}')
    print(f'|  变卦：{GUA64_NAMES[biangua]}')
    print(f'|                                  |')
    print('+==================================+')
    print(f'|  体用：{result}')
    print('+==================================+')
    print()
    print(f'【本卦解读】{GUA64_NAMES[bengua]}')
    print(f'  {GUA64_MEANING[bengua]}')
    print()
    print(f'【互卦解读】{GUA64_NAMES[hugua]}')
    print(f'  互卦揭示事情发展的中间过程：')
    print(f'  {GUA64_MEANING[hugua]}')
    print()
    print(f'【变卦解读】{GUA64_NAMES[biangua]}')
    print(f'  变卦揭示事情的最终结果：')
    print(f'  {GUA64_MEANING[biangua]}')
    print()
    print(f'【体用生克】{result}')
    print(f'  {desc}')
    print()
    print(f'【综合判断】')
    print(f'  体卦：{GUA[ti][0]}（{GUA[ti][1]}）属{GUA[ti][3]}')
    print(f'  用卦：{GUA[yong][0]}（{GUA[yong][1]}）属{GUA[yong][3]}')
    print(f'  本卦→互卦→变卦的走势：{GUA64_NAMES[bengua]} → {GUA64_NAMES[hugua]} → {GUA64_NAMES[biangua]}')
    print()
    if question:
        print(f'  === 针对「{question}」的建议 ===')
        if '用生体' in result or '比和' in result:
            print(f'  整体吉利，可以放心去做。变卦{GUA64_NAMES[biangua]}提示最终结果向好。')
        elif '体克用' in result:
            print(f'  事情可以做成，但需要花心思和精力。变卦{GUA64_NAMES[biangua]}的结果取决于你投入多少。')
        elif '体生用' in result:
            print(f'  这件事你可能付出比收获多。建议评估一下值不值得。如果是为了积累经验可以做。')
        else:
            print(f'  目前来看阻力较大，建议暂缓或换方向。变卦{GUA64_NAMES[biangua]}提示了另一种可能。')
    print()
    print('='*50)


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        # 三个数字起卦
        a, b, c = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        shang, xia, dong = qigua_by_numbers(a, b, c)
        q = sys.argv[4] if len(sys.argv) > 4 else ''
    elif len(sys.argv) == 2 and sys.argv[1] == 'now':
        shang, xia, dong = qigua_by_date()
        q = ''
    else:
        # 交互模式
        print('梅花易数起卦')
        print('1. 时间起卦（输入 now）')
        print('2. 数字起卦（输入3个数字，空格分隔）')
        mode = input('选择方式（输入 now 或 三个数字）: ').strip()
        if mode.lower() == 'now':
            shang, xia, dong = qigua_by_date()
            q = input('想问什么事？（回车跳过）: ').strip()
        else:
            parts = mode.split()
            if len(parts) >= 3:
                a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                a = int(input('第一个数字：'))
                b = int(input('第二个数字：'))
                c = int(input('第三个数字：'))
            shang, xia, dong = qigua_by_numbers(a, b, c)
            q = input('想问什么事？（回车跳过）: ').strip()

    generate_report(shang, xia, dong, q)
