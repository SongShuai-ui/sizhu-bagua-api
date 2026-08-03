#!/usr/bin/env python3
"""
通用八字排盘脚本 — 输入任意公历生辰，输出完整命盘
用法: python bazi_universal.py [年] [月] [日] [时] [性别]
示例: python bazi_universal.py 1995 8 12 14 女
       python bazi_universal.py 1989 6 28 5.5 男
      (不带参数则交互式输入)
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import date

# ===== 输入处理 =====
def get_input():
    if len(sys.argv) >= 5:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        hour = float(sys.argv[4])
        gender = sys.argv[5] if len(sys.argv) >= 6 else '男'
        return year, month, day, hour, gender
    else:
        print("=" * 40)
        print("  八字排盘 · 通用版")
        print("=" * 40)
        year = int(input("出生年份（公历）："))
        month = int(input("出生月份（公历）："))
        day = int(input("出生日期（公历）："))
        h = input("出生时间（24小时制，如 5.5=早上5:30）：")
        hour = float(h)
        gender = input("性别（男/女）：")
        return year, month, day, hour, gender

year, month, day, hour, gender = get_input()
solar = date(year, month, day)

# ===== 基础数据 =====
tiangan = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
dizhi = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
xiao = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']

# 时辰转换
def hour_to_shichen(h):
    idx = int(((h + 1) % 24) / 2)
    return dizhi[idx], idx

hb, hour_idx = hour_to_shichen(hour)

# ===== 年柱 =====
ys = (year - 4) % 10
yb = (year - 4) % 12
ng, nb = tiangan[ys], dizhi[yb]

# ===== 月柱（含节气近似） =====
# 节气日期近似表（每月第一个节气，±1天误差）
jieqi = {
    1: (5, '立春'), 2: (4, '惊蛰'), 3: (6, '清明'),
    4: (5, '立夏'), 5: (6, '芒种'), 6: (7, '小暑'),
    7: (7, '立秋'), 8: (8, '白露'), 9: (8, '寒露'),
    10: (7, '立冬'), 11: (7, '大雪'), 12: (7, '小寒')
}

# 确定月柱用的月份（以立春为正月起点）
if (month == 1 and day < jieqi[1][0]) or (month == 12 and day >= jieqi[12][0]):
    yue_adj = month + 12 if month == 1 else month  # 仍在上一年的丑月/寅月
    # 简化处理：用节气日切分
    if month == 1 and day < jieqi[1][0]:
        effective_month = 12  # 丑月
    elif month == 12 and day >= jieqi[12][0]:
        effective_month = 12  # 丑月仍是12
    else:
        effective_month = month
else:
    # 二月开始，以节气为界
    if day < jieqi.get(month, (4, ''))[0]:
        effective_month = month - 1
        if effective_month == 0:
            effective_month = 12
    else:
        effective_month = month

# 更准确的月份确定
def get_lunar_month(solar_month, solar_day):
    """根据节气近似确定八字月份"""
    # 寅=正月(立春2/4后), 卯=二月(惊蛰3/6后), 辰=三月(清明4/5后)
    # 巳=四月(立夏5/6后), 午=五月(芒种6/6后), 未=六月(小暑7/7后)
    # 申=七月(立秋8/7后), 酉=八月(白露9/8后), 戌=九月(寒露10/8后)
    # 亥=十月(立冬11/7后), 子=十一月(大雪12/7后), 丑=十二月(小寒1/5后)
    boundaries = [
        (2, 4, 1),   # 寅月 from 立春
        (3, 6, 2),   # 卯月 from 惊蛰
        (4, 5, 3),   # 辰月 from 清明
        (5, 6, 4),   # 巳月 from 立夏
        (6, 6, 5),   # 午月 from 芒种
        (7, 7, 6),   # 未月 from 小暑
        (8, 7, 7),   # 申月 from 立秋
        (9, 8, 8),   # 酉月 from 白露
        (10, 8, 9),  # 戌月 from 寒露
        (11, 7, 10), # 亥月 from 立冬
        (12, 7, 11), # 子月 from 大雪
        (1, 5, 12),  # 丑月 from 小寒
    ]

    for i, (bm, bd, yue_num) in enumerate(boundaries):
        if solar_month == bm and solar_day >= bd:
            return yue_num
        # Check if we're before this boundary but after the previous one
        prev_bm, prev_bd, prev_yue = boundaries[i-1]
        if (solar_month > prev_bm or (solar_month == prev_bm and solar_day >= prev_bd)) and \
           (solar_month < bm or (solar_month == bm and solar_day < bd)):
            return prev_yue

    # Default for dates before 立春
    return 12  # 丑月

lunar_month_num = get_lunar_month(month, day)

month_gan_seq = {
    '甲':['丙','丁','戊','己','庚','辛','壬','癸','甲','乙','丙','丁'],
    '乙':['戊','己','庚','辛','壬','癸','甲','乙','丙','丁','戊','己'],
    '丙':['庚','辛','壬','癸','甲','乙','丙','丁','戊','己','庚','辛'],
    '丁':['壬','癸','甲','乙','丙','丁','戊','己','庚','辛','壬','癸'],
    '戊':['甲','乙','丙','丁','戊','己','庚','辛','壬','癸','甲','乙'],
    '己':['丙','丁','戊','己','庚','辛','壬','癸','甲','乙','丙','丁'],
    '庚':['戊','己','庚','辛','壬','癸','甲','乙','丙','丁','戊','己'],
    '辛':['庚','辛','壬','癸','甲','乙','丙','丁','戊','己','庚','辛'],
    '壬':['壬','癸','甲','乙','丙','丁','戊','己','庚','辛','壬','癸'],
    '癸':['甲','乙','丙','丁','戊','己','庚','辛','壬','癸','甲','乙'],
}

# 月支顺序：寅=1, 卯=2, ..., 丑=12
month_zhi_list = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑']
mg = month_gan_seq[ng][lunar_month_num-1]
mb = month_zhi_list[lunar_month_num-1]  # 寅是正月

# ===== 日柱 =====
base = date(1900, 1, 1)
delta = (solar - base).days
cycle = (delta + 11) % 60
if cycle == 0:
    cycle = 60
ds = (cycle - 1) % 10
db = (cycle - 1) % 12
dg, dz_r = tiangan[ds], dizhi[db]

# ===== 时柱 =====
zishi_start = {'甲':'甲','乙':'丙','丙':'戊','丁':'庚','戊':'壬','己':'甲','庚':'丙','辛':'戊','壬':'庚','癸':'壬'}
start = zishi_start[dg]
hs = (tiangan.index(start) + hour_idx) % 10
hg = tiangan[hs]

# ===== 十神 =====
# 阳干(甲丙戊庚壬)和阴干(乙丁己辛癸)的十神映射不同
# 同一个 diff 值对阳干和阴干可能是不同的十神
_yang_shishen = {
    0:'比肩', 1:'劫财', 2:'食神', 3:'伤官', 4:'偏财',
    5:'正财', 6:'七杀', 7:'正官', 8:'偏印', 9:'正印'
}
_yin_shishen = {
    0:'比肩', 1:'伤官', 2:'食神', 3:'正财', 4:'偏财',
    5:'正官', 6:'七杀', 7:'正印', 8:'偏印', 9:'劫财'
}

def shishen(ri, other):
    """十神：ri=日干索引, other=目标天干索引"""
    diff = (other - ri) % 10
    is_yang_ri = ri % 2 == 0  # 甲(0)丙(2)戊(4)庚(6)壬(8) = 阳
    return _yang_shishen[diff] if is_yang_ri else _yin_shishen[diff]

ri = ds  # 日干索引

# ===== 地支藏干 =====
cang = {
    '子':['癸'], '丑':['己','癸','辛'], '寅':['甲','丙','戊'],
    '卯':['乙'], '辰':['戊','乙','癸'], '巳':['丙','庚','戊'],
    '午':['丁','己'], '未':['己','丁','乙'], '申':['庚','壬','戊'],
    '酉':['辛'], '戌':['戊','辛','丁'], '亥':['壬','甲']
}

# ===== 五行 =====
wx_map = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土',
    '庚':'金','辛':'金','壬':'水','癸':'水',
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}

# ===== 纳音 =====
nayin_map = {
    ('甲','子'):'海中金',('乙','丑'):'海中金',('丙','寅'):'炉中火',('丁','卯'):'炉中火',
    ('戊','辰'):'大林木',('己','巳'):'大林木',('庚','午'):'路旁土',('辛','未'):'路旁土',
    ('壬','申'):'剑锋金',('癸','酉'):'剑锋金',('甲','戌'):'山头火',('乙','亥'):'山头火',
    ('丙','子'):'涧下水',('丁','丑'):'涧下水',('戊','寅'):'城头土',('己','卯'):'城头土',
    ('庚','辰'):'白蜡金',('辛','巳'):'白蜡金',('壬','午'):'杨柳木',('癸','未'):'杨柳木',
    ('甲','申'):'泉中水',('乙','酉'):'泉中水',('丙','戌'):'屋上土',('丁','亥'):'屋上土',
    ('戊','子'):'霹雳火',('己','丑'):'霹雳火',('庚','寅'):'松柏木',('辛','卯'):'松柏木',
    ('壬','辰'):'长流水',('癸','巳'):'长流水',('甲','午'):'沙中金',('乙','未'):'沙中金',
    ('丙','申'):'山下火',('丁','酉'):'山下火',('戊','戌'):'平地木',('己','亥'):'平地木',
    ('庚','子'):'壁上土',('辛','丑'):'壁上土',('壬','寅'):'金箔金',('癸','卯'):'金箔金',
    ('甲','辰'):'覆灯火',('乙','巳'):'覆灯火',('丙','午'):'天河水',('丁','未'):'天河水',
    ('戊','申'):'大驿土',('己','酉'):'大驿土',('庚','戌'):'钗钏金',('辛','亥'):'钗钏金',
    ('壬','子'):'桑柘木',('癸','丑'):'桑柘木',
    ('甲','寅'):'大溪水',('乙','卯'):'大溪水',
    ('丙','辰'):'沙中土',('丁','巳'):'沙中土',
    ('戊','午'):'天上火',('己','未'):'天上火',
    ('庚','申'):'石榴木',('辛','酉'):'石榴木',
    ('壬','戌'):'大海水',('癸','亥'):'大海水',
}

# ===== 输出命盘 =====
print()
print('╔══════════════════════════════════════╗')
print('║         八  字  命  盘               ║')
print('╠══════════════════════════════════════╣')
print(f'║  公历：{year}年{month}月{day}日          ║')
print(f'║  时间：{hour}时（{hb}时）              ║')
print(f'║  性别：{gender}                         ║')
print(f'║  属相：{xiao[yb]}                         ║')
print('╠══════════════════════════════════════╣')
print(f'║                                      ║')
print(f'║    年        月        日        时   ║')
print(f'║   {ng}{nb}      {mg}{mb}      {dg}{dz_r}      {hg}{hb}     ║')
print(f'║                                      ║')
print('╚══════════════════════════════════════╝')
print()

# 十神
print('【十神关系】（日主：' + wx_map[dg] + '）')
pillars = [
    ('年柱', ng, nb, ys, yb),
    ('月柱', mg, mb, tiangan.index(mg), dizhi.index(mb)),
    ('日柱', dg, dz_r, ds, db),
    ('时柱', hg, hb, hs, hour_idx),
]
for name, g, z, gi, zi in pillars:
    ss_g = shishen(ri, gi)
    marker = ' ★日元' if name == '日柱' else ''
    print(f'  {name} {g}{z}：天干{g}({ss_g})，地支{z}{marker}')

print()

# 藏干
print('【地支藏干】')
for name, g, z, gi, zi in pillars:
    cg = cang[z]
    ss_list = [f'{x}({shishen(ri, tiangan.index(x))})' for x in cg]
    print(f'  {name} 支藏{z}：{", ".join(ss_list)}')

print()

# 五行
print('【五行分布】')
wx_ct = {'木':0,'火':0,'土':0,'金':0,'水':0}
for g,z in [(ng,nb),(mg,mb),(dg,dz_r),(hg,hb)]:
    wx_ct[wx_map[g]] += 1
    wx_ct[wx_map[z]] += 1
# 藏干加权
for g,z in [(ng,nb),(mg,mb),(dg,dz_r),(hg,hb)]:
    cg_list = cang[z]
    for c in cg_list:
        wx_ct[wx_map[c]] += 0.3  # 藏干权重0.3

ri_wx = wx_map[dg]
for k in ['木','火','土','金','水']:
    v = wx_ct[k]
    bar = '█' * int(v)
    m = ' ★日主' if k == ri_wx else ''
    print(f'  {k}：{bar} ({v:.1f}){m}')

print()

# 身强身弱
print('【身强身弱判断】')
tu = wx_ct['土']; huo = wx_ct['火']; jin = wx_ct['金']
mu = wx_ct['木']; shui = wx_ct['水']

# 月令得分
yueling_zhi = mb
yueling_wx = wx_map[yueling_zhi]
yueling_score = 2.0 if yueling_wx == ri_wx or (yueling_wx == '火' and ri_wx == '土') else 1.0
if yueling_wx == ri_wx:
    yueling_score = 2.5  # 月令同五行最强

tongdang = tu + huo  # 土日主：土为比劫，火为印
yidang = jin + shui + mu

print(f'  日主：{dg}（{ri_wx}）')
print(f'  月令：{mb}（{yueling_wx}）')
print(f'  同党(印+比劫)={tongdang:.1f}，异党(食伤+财+官杀)={yidang:.1f}')

if tongdang > yidang * 1.2:
    strength = '身强'
    xi = f'{"、".join([k for k in ["金","水","木"] if k != ri_wx])}'
    ji = f'{"、".join([k for k in ["火","土"] if k == ri_wx or k == "火"])}'
elif yidang > tongdang * 1.2:
    strength = '身弱'
    xi = f'{"、".join([k for k in ["火","土"] if k == ri_wx or k == "火"])}'
    ji = f'{"、".join([k for k in ["金","水","木"] if k != ri_wx])}'
else:
    strength = '中和'
    xi = '随大运流年变化'
    ji = '随大运流年变化'

print(f'  → {strength}')
print(f'  → 喜用神：{xi}')
print(f'  → 忌神：{ji}')

print()

# 纳音
print('【纳音】')
for name, g, z, gi, zi in pillars:
    n = nayin_map.get((g,z), '—')
    print(f'  {name} {g}{z}：{n}')

print()

# 大运
print('【大运排盘】')
# 阳年男/阴年女 = 顺排；阴年男/阳年女 = 逆排
yang_years = ['甲','丙','戊','庚','壬']
is_yang = ng in yang_years
is_male = gender == '男'

if (is_yang and is_male) or (not is_yang and not is_male):
    shunpai = True
    direction = '顺排'
else:
    shunpai = False
    direction = '逆排'

print(f'  年干{ng}({"阳" if is_yang else "阴"}) + {gender} → {direction}')

# 月柱天干索引
mg_idx = tiangan.index(mg)
mb_idx = month_zhi_list.index(mb)

dayun_ganzhi = []
for i in range(1, 9):
    if shunpai:
        gi = (mg_idx + i) % 10
        zi = (mb_idx + i) % 12
    else:
        gi = (mg_idx - i) % 10
        zi = (mb_idx - i) % 12
    dayun_ganzhi.append((tiangan[gi], month_zhi_list[zi]))

# 起运年龄（简化：约3-6岁）
qiyun = 3  # 粗略估计

print(f'  起运年龄：约{qiyun}岁')
print(f'  大运：')
for i, (g,z) in enumerate(dayun_ganzhi):
    start_age = qiyun + i * 10
    end_age = start_age + 9
    wx_g = wx_map[g]
    wx_z = wx_map[z]
    print(f'    {g}{z} ({wx_g}{wx_z})  {start_age}-{end_age}岁')

# 找到当前大运
current_age = 2026 - year
current_dayun = dayun_ganzhi[min(len(dayun_ganzhi)-1, max(0, (current_age - qiyun) // 10))]
print(f'  当前大运（{current_age}岁，2026年）：{current_dayun[0]}{current_dayun[1]}')

print()

# 2026流年
print('【2026年流年 丙午】')
print(f'  丙午：天干丙火，地支午火')
print(f'  丙为正印/偏印（对{dg}{ri_wx}日主而言）')
liunian_gan_ss = shishen(ri, tiangan.index('丙'))
liunian_zhi_ss = wx_map['午']
print(f'  丙火 → {liunian_gan_ss}')
print(f'  午火 → 火旺之年')
if '火' in ji or '土' in ji:
    print(f'  ⚠ 忌神之年，需谨慎行事，避免冲动决策')
if '火' in xi or '土' in xi:
    print(f'  ✓ 喜用之年，利于学习、事业、人脉拓展')

print()
print('='*50)
print('以上为排盘结果。可复制此输出用于 AI 解盘分析。')
