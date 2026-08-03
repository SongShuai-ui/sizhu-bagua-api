# 四柱八卦测算引擎 v2.1

八字、梅花易数、六爻、占星星盘 —— 四合一命理工具箱。

## 快速开始

```
pip install -r requirements.txt
python bazi_cli.py 1989 6 28 5:30 男 林州
python meihua_cli.py 5 2 0 问事业
python liuyao_cli.py 3 6 8 4 2 9 问财运
python xingpan_cli.py 1989 6 28 5:30 林州
```

所有工具支持 --json 和 --output。

## 工具矩阵

| 工具 | CLI | 引擎 | 测试 |
|------|-----|------|------|
| 八字 | bazi_cli.py | src/engine.py | 116 |
| 梅花 | meihua_cli.py | src/meihua.py | 17 |
| 六爻 | liuyao_cli.py | src/liuyao.py | 15 |
| 星盘 | xingpan_cli.py | src/xingpan.py | 13 |

## 不能做什么

- 不做寿命判断、疾病诊断
- 不做投资买卖、彩票赌博建议
- 不做恐吓式转运化解话术
- 当前未启用真太阳时校正
- 不替代心理咨询、法律、医疗建议

命理结果仅作文化娱乐和个人反思参考。

## 测试

```
pytest tests/ -v    # 158 passed
```

## 免责声明

所有报告自动包含免责声明。本引擎仅供命理学文化研究参考。
