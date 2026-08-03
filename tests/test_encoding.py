# -*- coding: utf-8 -*-
"""编码验证测试 — 确保所有关键文件中文可读，无乱码"""

import os
import sys
import json
import pytest
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# 乱码特征字符 - 这些字符绝不应出现在正常 UTF-8 中文文件中
# ============================================================
GARBLED_PATTERNS = [
    '�',   # Unicode replacement character
    '鏄', '槸', '鍏', '鐢', '鎴',   # GBK misinterpreted as Latin-1
    '鈥', '櫒', '鍜', '鈥檚',         # common garbled
]


def _read_utf8(relpath):
    """读取文件返回纯文本"""
    with open(os.path.join(BASE, relpath), 'r', encoding='utf-8') as f:
        return f.read()


def _check_no_garbled(text, label):
    """断言文本不含乱码"""
    for pattern in GARBLED_PATTERNS:
        assert pattern not in text, f'{label} contains garbled pattern: {repr(pattern)}'


class TestFileEncoding:
    """关键文档文件编码验证"""

    def test_readme_no_garbled(self):
        text = _read_utf8('README.md')
        _check_no_garbled(text, 'README.md')
        assert len(text) > 100, 'README.md should not be empty'
        assert 'bazi_cli' in text or 'bazi' in text.lower()

    def test_changelog_no_garbled(self):
        text = _read_utf8('CHANGELOG.md')
        _check_no_garbled(text, 'CHANGELOG.md')
        assert len(text) > 100, 'CHANGELOG.md should not be empty'

    def test_rules_yaml_no_garbled(self):
        text = _read_utf8('data/bazi_rules.yaml')
        _check_no_garbled(text, 'bazi_rules.yaml')
        assert '滴天髓' in text

    def test_sample_report_no_garbled(self):
        text = _read_utf8('示例报告.md')
        _check_no_garbled(text, '示例报告.md')
        assert '八字' in text

    def test_sample_json_no_garbled(self):
        text = _read_utf8('示例输出.json')
        _check_no_garbled(text, '示例输出.json')
        # JSON 中应有中文可读
        assert '己巳' in text or '庚午' in text or '"gan"' in text

    def test_all_src_py_no_garbled(self):
        """src/ 下所有 .py 文件无乱码"""
        src_dir = os.path.join(BASE, 'src')
        for f in os.listdir(src_dir):
            if not f.endswith('.py'):
                continue
            text = _read_utf8(f'src/{f}')
            _check_no_garbled(text, f'src/{f}')

    def test_all_tests_py_no_garbled(self):
        """tests/ 下所有 .py 文件无乱码（排除自身和含测试模式的文件）"""
        import os as _os
        skip = {'test_encoding.py', 'test_meihua.py', 'test_liuyao.py', 'test_xingpan.py'}
        for f in _os.listdir(_os.path.join(BASE, 'tests')):
            if not f.endswith('.py') or f in skip:
                continue
            text = _read_utf8(f'tests/{f}')
            _check_no_garbled(text, f'tests/{f}')

    def test_json_ensure_ascii_false(self):
        """JSON 输出使用 ensure_ascii=False，中文直接可读，无 \\uXXXX 转义"""
        sys.path.insert(0, BASE)
        from src.engine import compute_bazi
        from src.report import to_json
        chart = compute_bazi(1989, 6, 28, 5, 30, '男')
        js = to_json(chart)
        # 中文应该直接出现，不是 \uXXXX 转义
        assert '己' in js, 'JSON should contain readable Chinese character 己'
        assert '庚' in js, 'JSON should contain readable Chinese character 庚'
        assert '身强' in js, f'JSON should contain 身强, got escapes'
        # 验证无 Unicode escape 序列
        assert '\\u' not in js, 'JSON should NOT contain \\uXXXX escape sequences'


class TestCLISnapshot:
    """CLI 输出快照测试"""

    def run_cli(self, *args):
        """运行 CLI 并返回 stdout/stderr/returncode"""
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', os.path.join(BASE, 'bazi_cli.py')] + list(args),
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            cwd=BASE, env=env,
        )
        return result.stdout, result.stderr, result.returncode

    def test_markdown_output_contains_required_sections(self):
        """Markdown 输出必须包含关键段落"""
        stdout, stderr, rc = self.run_cli('1989', '6', '28', '5:30', '男', '林州')
        assert rc == 0, f'CLI failed: {stderr}'
        assert '八字命理简批报告' in stdout
        assert '公历' in stdout
        assert '八字' in stdout
        assert '大运方向' in stdout
        assert '仅供参考' in stdout, f'Missing disclaimer in: {stdout[:200]}'

    def test_markdown_no_garbled(self):
        """CLI Markdown 输出不含乱码"""
        stdout, stderr, rc = self.run_cli('1989', '6', '28', '5:30', '男')
        assert rc == 0
        _check_no_garbled(stdout, 'CLI markdown output')

    def test_json_output_no_garbled(self):
        """CLI JSON 输出不含乱码"""
        stdout, stderr, rc = self.run_cli('1989', '6', '28', '5:30', '男', '--json')
        assert rc == 0
        _check_no_garbled(stdout, 'CLI json output')
        # 验证 JSON 可解析
        data = json.loads(stdout)
        assert 'pillars' in data

    def test_json_output_readable_chinese(self):
        """CLI JSON 输出中文直接可读，无 \\uXXXX 转义"""
        stdout, stderr, rc = self.run_cli('1989', '6', '28', '5:30', '男', '--json')
        assert rc == 0
        # 中文应直接可见，整个输出不应有 Unicode escape
        assert '\\u' not in stdout, 'JSON should NOT contain \\uXXXX escape sequences'
        data = json.loads(stdout)
        assert data['pillars']['year']['gan'] == '己'

    def test_cli_error_friendly(self):
        """CLI 错误输出友好，无 traceback"""
        stdout, stderr, rc = self.run_cli('1989', '13', '32', '25:99', '男')
        assert rc != 0  # 应报错
        combined = stdout + stderr
        assert 'Traceback' not in combined, f'No traceback allowed: {combined[:200]}'
        assert '错误' in combined or '无效' in combined or 'Error' in combined or combined.strip() != ''

    def test_cli_help(self):
        """--help 输出帮助信息"""
        stdout, stderr, rc = self.run_cli('--help')
        assert rc == 0
        assert '用法' in stdout or 'usage' in stdout.lower() or 'python bazi_cli' in stdout
