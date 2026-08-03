import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import date

birth = {'year':1989, 'month':5, 'day':25, 'hour':5.5, 'gender':'男', 'tz':'卯时'}

# Lunar to solar: 1989-06-28
solar = date(1989, 6, 28)

tiangan = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
dizhi = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
xiao = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
shi_list = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

# === Year Pillar ===
ys = (birth['year'] - 4) % 10  # 5 = 己
yb = (birth['year'] - 4) % 12  # 5 = 巳
ng, nb = tiangan[ys], dizhi[yb]

# === Month Pillar ===
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
month_zhi = {1:'寅',2:'卯',3:'辰',4:'巳',5:'午',6:'未',7:'申',8:'酉',9:'戌',10:'亥',11:'子',12:'丑'}
mg = month_gan_seq[ng][birth['month']-1]  # 庚
mb = month_zhi[birth['month']]  # 午

# === Day Pillar ===
base = date(1900, 1, 1)
delta = (solar - base).days
cycle = (delta + 11) % 60
if cycle == 0: cycle = 60
ds = (cycle - 1) % 10  # day stem index
db = (cycle - 1) % 12  # day branch index
dg, dz_r = tiangan[ds], dizhi[db]

# === Hour Pillar ===
zishi_start = {'甲':'甲','乙':'丙','丙':'戊','丁':'庚','戊':'壬','己':'甲','庚':'丙','辛':'戊','壬':'庚','癸':'壬'}
start = zishi_start[dg]
hour_idx = 3  # 卯时 (5-7am)
hs = (tiangan.index(start) + hour_idx) % 10
hg, hb = tiangan[hs], shi_list[hour_idx]

# === PRINT CHART ===
print()
print('╔══════════════════════════════════════╗')
print('║         八  字  命  盘               ║')
print('╠══════════════════════════════════════╣')
print(f'║  公历：1989年6月28日（周三）         ║')
print(f'║  农历：己巳年 五月廿五 卯时          ║')
print(f'║  出生：河南林州市河顺镇              ║')
print(f'║  属相：{xiao[yb]}                            ║')
print('╠══════════════════════════════════════╣')
print(f'║                                      ║')
print(f'║    年        月        日        时   ║')
print(f'║   {ng}{nb}      {mg}{mb}      {dg}{dz_r}      {hg}{hb}     ║')
print(f'║                                      ║')
print('╚══════════════════════════════════════╝')
print()

# === TEN GODS ===
def shishen(ri, other):
    diff = (other - ri) % 10
    same = (ri % 2) == (other % 2)
    if diff == 0: return ('比肩', same)
    if diff == 1: return ('劫财', not same)
    if diff == 2: return ('食神', same)
    if diff == 3: return ('伤官', not same)
    if diff == 4: return ('偏财', same)
    if diff == 5: return ('正财', same)
    if diff == 6: return ('七杀', same)
    if diff == 7: return ('正官', not same)
    if diff == 8: return ('正印', same)
    if diff == 9: return ('偏印', same)

ri = ds  # 日干己土 index

print('【十神】（日主：己土）')
print(f'  年柱 {ng}{nb}：天干{ng} → {shishen(ri, ys)[0]}，地支{nb}')
print(f'  月柱 {mg}{mb}：天干{mg} → {shishen(ri, tiangan.index(mg))[0]}，地支{mb}')
print(f'  日柱 {dg}{dz_r}：天干{dg} → ★ 日元（元男），地支{dz_r}')
print(f'  时柱 {hg}{hb}：天干{hg} → {shishen(ri, hs)[0]}，地支{hb}')
print()

# === HIDDEN STEMS ===
cang = {
    '子':['癸'], '丑':['己','癸','辛'], '寅':['甲','丙','戊'],
    '卯':['乙'], '辰':['戊','乙','癸'], '巳':['丙','庚','戊'],
    '午':['丁','己'], '未':['己','丁','乙'], '申':['庚','壬','戊'],
    '酉':['辛'], '戌':['戊','辛','丁'], '亥':['壬','甲']
}
print('【地支藏干】')
for lab, zhi in [('年',nb),('月',mb),('日',dz_r),('时',hb)]:
    cg = cang[zhi]
    ss = [f'{g}({shishen(ri, tiangan.index(g))[0]})' for g in cg]
    print(f'  {lab}支{zhi}藏：{", ".join(ss)}')
print()

# === FIVE ELEMENTS ===
wx_map = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土',
    '庚':'金','辛':'金','壬':'水','癸':'水',
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}
wx_ct = {'木':0,'火':0,'土':0,'金':0,'水':0}
for g,z in [(ng,nb),(mg,mb),(dg,dz_r),(hg,hb)]:
    wx_ct[wx_map[g]] += 1
    wx_ct[wx_map[z]] += 1

print('【五行分布】')
ri_wx = wx_map[dg]
for k in ['木','火','土','金','水']:
    v = wx_ct[k]
    bar = '█' * v
    m = ' ★日主' if k == ri_wx else ''
    print(f'  {k}：{bar} ({v}){m}')
print()

# === BODY STRENGTH ===
print('【身强身弱分析】')
print(f'  日主：己土（田园之土）')
print(f'  月令：午火（火旺之月，火生土，得令）')
print(f'  天干：戊(年劫财)+庚(月伤官)+己(日)+丁(时偏印)')
print(f'  地支：辰(土)+午(火)+酉(金)+卯(木)')
tu = wx_ct['土']; huo = wx_ct['火']; jin = wx_ct['金']
mu = wx_ct['木']; shui = wx_ct['水']
print(f'  同党(土+火)={tu+huo}，异党(金+水+木)={jin+shui+mu}')

if tu+huo > jin+shui+mu:
    strength = '身强'
    xi = '金、水、木'
    ji = '火、土'
else:
    strength = '身弱'
    xi = '火、土'
    ji = '金、水、木'

print(f'  → {strength}')
print(f'  → 喜用神：{xi}')
print(f'  → 忌神：{ji}')
print()

# === NA YIN ===
nayin = {
    ('戊','辰'):'大林木', ('己','巳'):'大林木',
    ('庚','午'):'路旁土', ('辛','未'):'路旁土',
    ('壬','申'):'剑锋金', ('癸','酉'):'剑锋金',
    ('甲','子'):'海中金', ('乙','丑'):'海中金',
}
print('【纳音】')
for g,z in [(ng,nb),(mg,mb),(dg,dz_r),(hg,hb)]:
    n = nayin.get((g,z), '—')
    print(f'  {g}{z}：{n}')
print()

# === LUCK PILLARS (preview) ===
print('【大运（逆排）】')
print(f'  己年(阴年)男命 → 逆排大运')
print(f'  起运约 3-4 岁（需节气精确计算）')
print(f'  己巳(年)→戊辰→丁卯→丙寅→乙丑→甲子→癸亥→壬戌→辛酉')
print(f'  当前(37岁, 2026)：约在 乙丑 大运 后期')
print(f'  下一步大运：甲子')
print()

# === 2026 STREAMING YEAR ===
print('【2026年流年 丙午】')
print(f'  丙午：天干丙火(正印)，地支午火(偏印)')
print(f'  火旺之年，印星极旺')
print(f'  对你：印星旺 → 利学习、文书、证书、房产')
if strength == '身强':
    print(f'  但身强者遇旺印 → 思多行少，容易想太多不动手')
    print(f'  需主动求变，用行动（金泄土）破局')
