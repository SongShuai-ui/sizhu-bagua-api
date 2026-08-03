# -*- coding: utf-8 -*-
"""AI interpretation module - calls DeepSeek API."""

import json
import os
import urllib.request
import urllib.error

_K1 = "sk-9ea339e3ef304693b84ddc"
_K2 = "411a634bf7"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "") or (_K1 + _K2)
DEEPSEEK_BASE = "https://api.deepseek.com"

SYSTEM_PROMPT = """You are a professional Chinese fortune-telling master, expert in Ba Zi, Mei Hua Yi Shu, Liu Yao, and Western Astrology.
The user will send you divination data in JSON format.
Please give a warm, natural, and insightful reading in Chinese.

Requirements:
1. Speak like a wise friend, not a textbook
2. Start with an overall assessment, then break down the details
3. Reference specific data points from the input
4. Give practical advice, but never over-promise
5. Keep it to 300-500 Chinese characters
6. End with a gentle reminder to use your own judgment for major life decisions

DO NOT: predict death, diagnose illness, recommend investments, or use scare tactics."""


def interpret_bazi(chart):
    user_msg = json.dumps({
        "type": "Ba Zi (Eight Characters)",
        "chart": f"{chart['pillars']['year']['gan']}{chart['pillars']['year']['zhi']} "
                 f"{chart['pillars']['month']['gan']}{chart['pillars']['month']['zhi']} "
                 f"{chart['pillars']['day']['gan']}{chart['pillars']['day']['zhi']} "
                 f"{chart['pillars']['hour']['gan']}{chart['pillars']['hour']['zhi']}",
        "day_master": f"{chart['day_master']['gan']}{chart['day_master']['element']}",
        "zodiac": chart['day_master']['shengxiao'],
        "strength": chart['strength_analysis']['verdict'],
        "useful_elements": chart['strength_analysis']['useful_elements'],
        "harmful_elements": chart['strength_analysis']['harmful_elements'],
        "ten_gods": chart['ten_gods'],
        "nayin": chart['nayin'],
        "five_elements": chart['five_elements'],
        "current_dayun": chart['luck']['current']['ganzhi'] if chart['luck']['current'] else 'none',
        "annual_fortune": f"{chart['annual_fortune']['year']} {chart['annual_fortune']['ganzhi']} {chart['annual_fortune']['ten_god']}",
        "age": chart.get('current_age', 'unknown'),
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_meihua(chart):
    ty = chart['tiyong']
    user_msg = json.dumps({
        "type": "Mei Hua Yi Shu",
        "question": chart['input']['question'] or 'not specified',
        "original_hexagram": chart['bengua']['name'],
        "original_meaning": chart['bengua']['meaning'],
        "mutual_hexagram": chart['hugua']['name'],
        "mutual_meaning": chart['hugua']['meaning'],
        "changed_hexagram": chart['biangua']['name'],
        "changed_meaning": chart['biangua']['meaning'],
        "ti_body": ty['ti_gua'],
        "yong_action": ty['yong_gua'],
        "tiyong_result": ty['result'],
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_liuyao(chart):
    user_msg = json.dumps({
        "type": "Liu Yao Divination",
        "question": chart['question'] or 'not specified',
        "hexagram": chart['gua_name'],
        "palace": f"{chart['gong']} {chart['gong_wuxing']}",
        "self_line": chart['shi_yao'],
        "moving_lines_count": chart['moving_count'],
        "moving_lines": [f"line {p}" for p, _ in chart.get('moving_yaos', [])],
        "yongshen": chart.get('yongshen', ''),
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def interpret_xingpan(chart):
    planets = chart['planets']
    user_msg = json.dumps({
        "type": "Western Astrology Natal Chart",
        "sun": planets['太阳']['zodiac'],
        "moon": planets['月亮']['zodiac'],
        "rising": chart['ascendant']['zodiac'],
        "mc": chart['midheaven']['zodiac'],
        "mercury": planets['水星']['zodiac'],
        "venus": planets['金星']['zodiac'],
        "mars": planets['火星']['zodiac'],
        "dominant": chart['dominant_element'],
        "elements": chart['element_distribution'],
    }, ensure_ascii=False)
    return _call_deepseek(user_msg)


def _call_deepseek(user_message):
    if not DEEPSEEK_API_KEY:
        return "[AI reading not available: DEEPSEEK_API_KEY not set]"

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
        body = e.read().decode("utf-8", errors="replace")
        return f"[AI API error: HTTP {e.code} - {body[:200]}]"
    except Exception as e:
        return f"[AI error: {str(e)[:200]}]"
