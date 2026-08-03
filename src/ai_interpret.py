# -*- coding: utf-8 -*-
"""AI 解读模块 — 调用 DeepSeek API 将命盘数据翻译成白话解读"""

import json
import os
import urllib.request
import urllib.error

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE = "https://api.deepseek.com"

SYSTEM_PROMPT = """你是一位资深命理师，精通八字、梅花易数、六爻和占星。
用户会发来命盘数据，请你用通俗易懂的中文给出解读。

要求：
1. 语言亲切自然，像朋友聊天一样，不要教科书式
2. 先总述整体格局，再分点分析
3. 结合具体数据说话，不要空泛
4. 适当给出建议，但不过度承诺
5. 结尾附上一句简短提醒（如"人生重大决策请结合现实判断"）
6. 控制在 300-500 字以内

注意：不预测寿命、不诊断疾病、不建议投资买卖、不做恐吓。" ""


def interpret_bazi(chart: dict) -> str:
    """八字解读"""
    user_msg = json.dumps({
        "类型": "八字排盘",
        "八字": f"{chart['pillars']['year']['gan']}{chart['pillars']['year']['zhi']} "
                f"{chart['pillars']['month']['gan']}{chart['pillars']['month']['zhi']} "
                f"{chart['pillars']['day']['gan']}{chart['pillars']['day']['zhi']} "
                f"{chart['pillars']['hour']['gan']}{chart['pillars']['hour']['zhi']}",
        "日主": f"{chart['day_master']['gan']}{chart['day_master']['element']}",
        "生肖": chart['day_master']['shengxiao'],
        "身强身弱": chart['strength_analysis']['verdict'],
        "喜用神": chart['strength_analysis']['useful_elements'],
        "忌神": chart['strength_analysis']['harmful_elements'],
        "判断依据": chart['strength_analysis']['reasoning'],
        "十神": chart['ten_gods'],
        "纳音": chart['nayin'],
        "五行分布": chart['five_elements'],
        "当前大运": chart['luck']['current']['ganzhi'] if chart['luck']['current'] else '无',
        "流年": f"{chart['annual_fortune']['year']}年 {chart['annual_fortune']['ganzhi']} {chart['annual_fortune']['ten_god']}",
        "年龄": chart.get('current_age', '未知'),
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_meihua(chart: dict) -> str:
    """梅花易数解读"""
    ty = chart['tiyong']
    user_msg = json.dumps({
        "类型": "梅花易数",
        "所问之事": chart['input']['question'] or '未指定',
        "本卦": chart['bengua']['name'],
        "本卦含义": chart['bengua']['meaning'],
        "互卦": chart['hugua']['name'],
        "互卦含义": chart['hugua']['meaning'],
        "变卦": chart['biangua']['name'],
        "变卦含义": chart['biangua']['meaning'],
        "体卦": ty['ti_gua'],
        "用卦": ty['yong_gua'],
        "体用结果": ty['result'],
        "体用解读": ty['description'],
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_liuyao(chart: dict) -> str:
    """六爻解读"""
    user_msg = json.dumps({
        "类型": "六爻预测",
        "所问之事": chart['question'] or '未指定',
        "卦名": chart['gua_name'],
        "所属宫": f"{chart['gong']}宫 {chart['gong_wuxing']}",
        "世爻": f"第{chart['shi_yao']}爻",
        "动爻数量": chart['moving_count'],
        "动爻详情": [f"第{p}爻" for p, _ in chart.get('moving_yaos', [])],
        "用神": chart.get('yongshen', ''),
        "基础分析": chart.get('analysis', {}),
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_xingpan(chart: dict) -> str:
    """星盘解读"""
    planets = chart['planets']
    user_msg = json.dumps({
        "类型": "占星星盘",
        "太阳星座": planets['太阳']['zodiac'],
        "月亮星座": planets['月亮']['zodiac'],
        "上升星座": chart['ascendant']['zodiac'],
        "天顶": chart['midheaven']['zodiac'],
        "水星": planets['水星']['zodiac'],
        "金星": planets['金星']['zodiac'],
        "火星": planets['火星']['zodiac'],
        "日月关系": chart['sun_moon_relation'],
        "主导元素": chart['dominant_element'],
        "元素分布": chart['element_distribution'],
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def _call_deepseek(user_message: str) -> str:
    """调用 DeepSeek API（同步，使用 urllib）"""
    if not DEEPSEEK_API_KEY:
        return "[AI 解读未配置：请设置 DEEPSEEK_API_KEY 环境变量]"
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{DEEPSEEK_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[AI 解读失败: HTTP {e.code}]"
    except Exception as e:
        return f"[AI 解读异常: {str(e)[:100]}]"
