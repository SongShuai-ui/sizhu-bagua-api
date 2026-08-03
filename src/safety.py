"""风险过滤器。

在报告文本生成后、输出 PDF/DOCX 前进行内容审核。
不阻止生成，但标记风险行供人工复核。
"""

import re
from dataclasses import dataclass, field


@dataclass
class SafetyWarning:
    line: int
    text: str
    category: str
    severity: str  # 'block' | 'warn'


# ── 风险模式 ──
BANNED_PATTERNS = [
    # (正则, 类别, 严重度)
    (r'(死|亡|活不过|短命|夭折|寿元终|寿不长|少年终|早凋零|命不长|寿将完|寿元归|损寿|伤寿元)',
     '寿命判断', 'block'),
    (r'(癌症|肿瘤|心脏病|绝症|不治之症|必死)',
     '疾病诊断', 'block'),
    (r'(彩票|赌博|赌钱|买涨|买跌|抄底|逃顶|股票推荐|投资建议)',
     '投资赌博', 'block'),
    (r'(花钱消灾|做法事|化解煞气|转运符|改运法事|破解之法|破财消灾)',
     '恐吓营销', 'block'),
    (r'(包准|包对|100%|百分百准|绝不骗人|保证准确)',
     '过度承诺', 'warn'),
]
# 编译
COMPILED_PATTERNS = [(re.compile(p), cat, sev) for p, cat, sev in BANNED_PATTERNS]

# ── 免责声明 ──
DISCLAIMER = (
    '以上分析基于传统命理学，仅供参考。\n'
    '本报告不构成以下建议：寿命判断、疾病诊断、投资买卖、赌博彩票、法律事务。\n'
    '人生重大决策请结合现实情况独立判断。'
)

DISCLAIMER_SHORT = (
    '以上分析基于传统命理学，仅供参考。人生选择请结合现实独立判断。'
)


def sanitize_report(text: str) -> tuple[str, list[SafetyWarning]]:
    """扫描报告文本，标记风险行。

    Returns:
        (text, warnings): 文本不做修改，返回警告列表供调用方决策
    """
    warnings = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern, category, severity in COMPILED_PATTERNS:
            if pattern.search(line):
                warnings.append(SafetyWarning(
                    line=i + 1,
                    text=line.strip()[:80],
                    category=category,
                    severity=severity,
                ))
    return text, warnings


def has_blocked_content(warnings: list[SafetyWarning]) -> bool:
    """是否有被阻止的内容"""
    return any(w.severity == 'block' for w in warnings)


def format_warnings(warnings: list[SafetyWarning]) -> str:
    """格式化警告列表"""
    if not warnings:
        return '未检测到风险内容。'
    lines = ['检测到以下风险内容：']
    for w in warnings:
        lines.append(f'  行{w.line} [{w.severity.upper()}] {w.category}: {w.text}')
    return '\n'.join(lines)
