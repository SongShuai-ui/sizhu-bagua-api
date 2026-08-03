# CHANGELOG

## v2.1.0 - 2026-08-02 全工具产品化

### 新增
- src/meihua.py - 梅花易数引擎
- src/liuyao.py - 六爻引擎
- src/xingpan.py - 占星星盘引擎
- meihua_cli.py / liuyao_cli.py / xingpan_cli.py
- tests: test_meihua(17) + test_liuyao(15) + test_xingpan(13)
- generate_report.py 重构: JSON输入、安全过滤

### 统一接口
四个工具全部支持 --json --output --help，统一免责声明。

### 测试
158 passed

---

## v2.0.0 - 2026-08-02 产品化重构

- 新建 src/ 测算引擎，8个模块
- lunar-python 替代固定节气表
- 修正12个bug: 立春切换、身强身弱动态计算、起运年龄精确计算
- 116测试用例

---

## v1.0.0 - 2026-07 快速原型

- bazi_universal.py / meihua.py / liuyao.py / xingpan.py
- PDF/DOCX 报告生成
