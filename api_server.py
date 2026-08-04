#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四柱八卦 API Server — FastAPI 封装

八字 / 梅花易数 / 六爻 / 占星星盘 四合一命理计算 API

启动:
    python api_server.py
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

文档:
    http://localhost:8000/docs      Swagger UI
    http://localhost:8000/redoc     ReDoc
    http://localhost:8000/          中文文档页
"""

import sys
import os
from datetime import datetime

# 确保 src 在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.engine import compute_bazi
from src.meihua import compute_meihua
from src.liuyao import compute_liuyao
from src.xingpan import compute_xingpan
from src.report import to_markdown as bazi_to_md
from src.safety import DISCLAIMER
from src.ai_interpret import interpret_bazi, interpret_meihua, interpret_liuyao, interpret_xingpan

# ── Helpers ──
def _normalize_gender(g: str) -> str:
    g = g.strip().lower()
    if g in ("male", "m"):
        return "男"
    if g in ("female", "f"):
        return "女"
    return g if g in ("男", "女") else "男"


# ── App ──
app = FastAPI(
    title="四柱八卦命理 API",
    description="八字排盘 / 梅花易数 / 六爻预测 / 占星星盘 — 四合一命理计算引擎",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──
class BaziRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="公历年份", example=1989)
    month: int = Field(..., ge=1, le=12, description="公历月份", example=6)
    day: int = Field(..., ge=1, le=31, description="公历日期", example=28)
    hour: int = Field(..., ge=0, le=23, description="小时 (0-23)", example=5)
    minute: int = Field(default=0, ge=0, le=59, description="分钟", example=30)
    gender: str = Field(default="男", description="性别: 男/女 或 male/female")
    birthplace: str = Field(default="", description="出生地 (可选)", example="林州")


class MeihuaRequest(BaseModel):
    a: int = Field(..., description="第一个数字", example=5)
    b: int = Field(..., description="第二个数字", example=2)
    c: int = Field(..., description="第三个数字", example=0)
    question: str = Field(default="", description="所问之事", example="问事业")


class LiuyaoRequest(BaseModel):
    numbers: list[int] | None = Field(
        default=None, min_length=6, max_length=6,
        description="6个0-9的数字 (不传则随机铜钱起卦)",
        example=[3, 6, 8, 4, 2, 9],
    )
    question: str = Field(default="", description="所问之事", example="问财运")


class XingpanRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="公历年份", example=1989)
    month: int = Field(..., ge=1, le=12, description="公历月份", example=6)
    day: int = Field(..., ge=1, le=31, description="公历日期", example=28)
    hour: int = Field(..., ge=0, le=23, description="小时", example=5)
    minute: int = Field(default=0, ge=0, le=59, description="分钟", example=30)
    birthplace: str = Field(default="", description="出生地", example="林州")


class HealthResponse(BaseModel):
    status: str
    version: str
    engines: list[str]
    timestamp: str


# ── API ──
@app.get("/api/v1/health", response_model=HealthResponse, tags=["系统"])
def health():
    """服务健康检查"""
    return {
        "status": "ok",
        "version": "2.1.0",
        "engines": ["bazi", "meihua", "liuyao", "xingpan"],
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/bazi", tags=["八字"])
def bazi(request: BaziRequest):
    """八字排盘 — 四柱、十神、藏干、纳音、大运、流年、身强身弱"""
    gender = _normalize_gender(request.gender)
    try:
        chart = compute_bazi(
            request.year, request.month, request.day,
            request.hour, request.minute,
            gender, request.birthplace,
        )
        return {"code": 0, "data": chart}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "error": str(e)},
        )


@app.post("/api/v1/bazi/report", tags=["八字"])
def bazi_report(request: BaziRequest):
    """八字排盘 → Markdown 报告"""
    gender = _normalize_gender(request.gender)
    try:
        chart = compute_bazi(
            request.year, request.month, request.day,
            request.hour, request.minute,
            gender, request.birthplace,
        )
        md = bazi_to_md(chart)
        return {"code": 0, "data": {"markdown": md}}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "error": str(e)},
        )


@app.post("/api/v1/meihua", tags=["梅花易数"])
def meihua(request: MeihuaRequest):
    """梅花易数 — 数字起卦，输出本卦/互卦/变卦/体用生克"""
    try:
        chart = compute_meihua(request.a, request.b, request.c, request.question)
        return {"code": 0, "data": chart}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "error": str(e)},
        )


@app.post("/api/v1/liuyao", tags=["六爻"])
def liuyao(request: LiuyaoRequest = None):
    """六爻预测 — 支持数字起卦或随机铜钱起卦，含装卦、世应、动爻"""
    try:
        numbers = request.numbers if request else None
        question = request.question if request else ""
        chart = compute_liuyao(numbers=numbers, question=question)
        return {"code": 0, "data": chart}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "error": str(e)},
        )


@app.post("/api/v1/xingpan", tags=["星盘"])
def xingpan(request: XingpanRequest):
    """占星星盘 — 计算行星位置、上升/天顶、元素分布"""
    try:
        chart = compute_xingpan(
            request.year, request.month, request.day,
            request.hour, request.minute, request.birthplace,
        )
        return {"code": 0, "data": chart}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "error": str(e)},
        )


# ── AI 解读 ──
@app.post("/api/v1/bazi/ai", tags=["AI解读"])
def bazi_ai(request: BaziRequest):
    """八字 AI 白话解读"""
    gender = _normalize_gender(request.gender)
    chart = compute_bazi(request.year, request.month, request.day, request.hour, request.minute, gender, request.birthplace)
    try:
        text = interpret_bazi(chart)
        return {"code": 0, "data": {"chart": chart, "ai_reading": text}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 1, "error": f"AI 解读失败: {e}"})


@app.post("/api/v1/meihua/ai", tags=["AI解读"])
def meihua_ai(request: MeihuaRequest):
    """梅花易数 AI 白话解读"""
    chart = compute_meihua(request.a, request.b, request.c, request.question)
    try:
        text = interpret_meihua(chart)
        return {"code": 0, "data": {"chart": chart, "ai_reading": text}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 1, "error": f"AI 解读失败: {e}"})


@app.post("/api/v1/liuyao/ai", tags=["AI解读"])
def liuyao_ai(request: LiuyaoRequest = None):
    """六爻 AI 白话解读"""
    numbers = request.numbers if request else None
    question = request.question if request else ""
    chart = compute_liuyao(numbers=numbers, question=question)
    try:
        text = interpret_liuyao(chart)
        return {"code": 0, "data": {"chart": chart, "ai_reading": text}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 1, "error": f"AI 解读失败: {e}"})


@app.post("/api/v1/xingpan/ai", tags=["AI解读"])
def xingpan_ai(request: XingpanRequest):
    """星盘 AI 白话解读"""
    chart = compute_xingpan(request.year, request.month, request.day, request.hour, request.minute, request.birthplace)
    try:
        text = interpret_xingpan(chart)
        return {"code": 0, "data": {"chart": chart, "ai_reading": text}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 1, "error": f"AI 解读失败: {e}"})


# ── 用户端应用 ──
@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
def app_page():
    return test_page()


@app.get("/test", response_class=HTMLResponse, include_in_schema=False)
def test_page():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Test</title>
<style>
body { font-family: sans-serif; padding: 2rem; max-width: 500px; margin: 0 auto; }
input, select { padding: 0.5rem; margin: 0.3rem; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 0.6rem 1.5rem; background: #d97706; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; }
.result { margin-top: 1rem; padding: 1rem; background: #f5f5f5; border-radius: 8px; white-space: pre-wrap; }
.error { color: red; margin-top: 0.5rem; }
</style></head>
<body>
<h1>八字排盘测试</h1>
<p>年 <input id="y" value="1989" size="6"> 月 <input id="m" value="6" size="4"> 日 <input id="d" value="28" size="4">
   时 <input id="h" value="5" size="4"> 分 <input id="mi" value="30" size="4">
   性别 <select id="g"><option>男</option><option>女</option></select></p>
<button onclick="test()">排盘</button>
<div class="error" id="err"></div>
<div class="result" id="res"></div>
<script>
async function test() {
  document.getElementById('err').textContent = '';
  document.getElementById('res').textContent = '请求中...';
  try {
    const body = {
      year: +document.getElementById('y').value,
      month: +document.getElementById('m').value,
      day: +document.getElementById('d').value,
      hour: +document.getElementById('h').value,
      minute: +document.getElementById('mi').value || 0,
      gender: document.getElementById('g').value
    };
    const r = await fetch('/api/v1/bazi', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body)
    });
    const d = await r.json();
    if (d.code !== 0) throw new Error(d.error || JSON.stringify(d.detail));
    const p = d.data.pillars;
    document.getElementById('res').textContent = '八字: ' +
      p.year.gan + p.year.zhi + ' ' + p.month.gan + p.month.zhi + ' ' +
      p.day.gan + p.day.zhi + ' ' + p.hour.gan + p.hour.zhi + '\\n' +
      '日主: ' + d.data.day_master.gan + d.data.day_master.element + '\\n' +
      '身强身弱: ' + d.data.strength_analysis.verdict;
  } catch(e) {
    document.getElementById('err').textContent = 'Error: ' + e.message;
    document.getElementById('res').textContent = '';
  }
}
</script>
</body></html>""")


# ── 根路径 → 中文文档页 ──
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return HTMLResponse(content=DOC_HTML)


DOC_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>四柱八卦命理 API v2.1</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; line-height: 1.7; }
  h1 { font-size: 1.8rem; margin-bottom: 0.3rem; }
  h2 { font-size: 1.3rem; margin: 2rem 0 0.8rem; padding-bottom: 0.3rem; border-bottom: 2px solid #e0e0e0; }
  h3 { font-size: 1rem; margin: 1.2rem 0 0.4rem; }
  .sub { color: #666; margin-bottom: 1.5rem; }
  table { width: 100%; border-collapse: collapse; margin: 0.8rem 0; }
  th, td { padding: 0.55rem 0.8rem; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f5f5f5; font-weight: 600; font-size: 0.9rem; }
  code { background: #f0f0f0; padding: 0.15em 0.4em; border-radius: 3px; font-size: 0.9em; }
  pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem 1.2rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; line-height: 1.6; margin: 0.6rem 0; }
  .method { display: inline-block; padding: 0.15em 0.5em; border-radius: 4px; font-size: 0.8rem; font-weight: 700; margin-right: 0.3rem; }
  .post { background: #e8f5e9; color: #2e7d32; }
  .get { background: #e3f2fd; color: #1565c0; }
  .endpoint { font-family: monospace; font-size: 0.95rem; }
  a { color: #1565c0; }
  .links { display: flex; gap: 1rem; flex-wrap: wrap; margin: 0.8rem 0; }
  .links a { background: #f5f5f5; padding: 0.3rem 0.8rem; border-radius: 4px; text-decoration: none; }
  .note { background: #fff3e0; border-left: 3px solid #ff9800; padding: 0.6rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; font-size: 0.9rem; }
  .warn { background: #ffebee; border-left: 3px solid #e53935; padding: 0.6rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; font-size: 0.9rem; }
  @media (prefers-color-scheme: dark) {
    body { background: #1a1a2e; color: #e0e0e0; }
    th { background: #2a2a3e; }
    td, th { border-color: #333; }
    code { background: #333; color: #e0e0e0; }
    .note { background: #2a2010; }
    .warn { background: #2a1010; }
    .links a { background: #2a2a3e; }
    .sub { color: #aaa; }
    .post { background: #1a3a1a; color: #81c784; }
    .get { background: #1a2a3a; color: #64b5f6; }
  }
</style>
</head>
<body>

<h1>🀄️ 四柱八卦命理 API</h1>
<p class="sub">八字 · 梅花易数 · 六爻 · 占星星盘 — 四合一命理计算引擎 v2.1</p>

<div class="links">
  <a href="/docs">Swagger 文档</a>
  <a href="/redoc">ReDoc 文档</a>
  <a href="/api/v1/health">健康检查</a>
</div>

<div class="note">
  <strong>💡 快速开始</strong><br>
  所有接口统一返回 <code>{"code": 0, "data": {...}}</code>，出错时 <code>code</code> 为非 0。
  底层使用 <a href="https://pypi.org/project/lunar-python/" target="_blank">lunar-python</a>
  天文历法库，支持 1900-2100 年排盘。
</div>

<h2>API 端点</h2>

<table>
  <tr><th>方法</th><th>路径</th><th>说明</th></tr>
  <tr>
    <td><span class="method post">POST</span></td>
    <td class="endpoint">/api/v1/bazi</td>
    <td>八字排盘 — 四柱、十神、藏干、纳音、大运流年、身强身弱</td>
  </tr>
  <tr>
    <td><span class="method post">POST</span></td>
    <td class="endpoint">/api/v1/bazi/report</td>
    <td>八字排盘 → Markdown 人类可读报告</td>
  </tr>
  <tr>
    <td><span class="method post">POST</span></td>
    <td class="endpoint">/api/v1/meihua</td>
    <td>梅花易数 — 三数起卦，本卦/互卦/变卦/体用生克</td>
  </tr>
  <tr>
    <td><span class="method post">POST</span></td>
    <td class="endpoint">/api/v1/liuyao</td>
    <td>六爻预测 — 数字起卦或随机铜钱起卦，装卦世应动爻</td>
  </tr>
  <tr>
    <td><span class="method post">POST</span></td>
    <td class="endpoint">/api/v1/xingpan</td>
    <td>占星星盘 — 行星位置、上升/天顶、元素分布</td>
  </tr>
  <tr>
    <td><span class="method get">GET</span></td>
    <td class="endpoint">/api/v1/health</td>
    <td>服务健康检查</td>
  </tr>
</table>

<h2>示例</h2>

<h3>八字排盘</h3>
<pre>curl -X POST http://localhost:8000/api/v1/bazi \\
  -H "Content-Type: application/json" \\
  -d '{"year":1989,"month":6,"day":28,"hour":5,"minute":30,"gender":"男","birthplace":"林州"}'</pre>

<h3>梅花易数</h3>
<pre>curl -X POST http://localhost:8000/api/v1/meihua \\
  -H "Content-Type: application/json" \\
  -d '{"a":5,"b":2,"c":0,"question":"问事业"}'</pre>

<h3>六爻（随机铜钱）</h3>
<pre>curl -X POST http://localhost:8000/api/v1/liuyao \\
  -H "Content-Type: application/json" \\
  -d '{"question":"问财运"}'</pre>

<h3>六爻（数字起卦）</h3>
<pre>curl -X POST http://localhost:8000/api/v1/liuyao \\
  -H "Content-Type: application/json" \\
  -d '{"numbers":[3,6,8,4,2,9],"question":"问合作"}'</pre>

<h3>占星星盘</h3>
<pre>curl -X POST http://localhost:8000/api/v1/xingpan \\
  -H "Content-Type: application/json" \\
  -d '{"year":1989,"month":6,"day":28,"hour":5,"minute":30,"birthplace":"林州"}'</pre>

<div class="warn">
  <strong>⚠️ 免责声明</strong><br>
  所有接口返回结果均包含免责声明。本 API 仅供命理学文化研究与技术参考，
  不构成任何形式的寿命判断、疾病诊断、投资建议或法律建议。
</div>

</body>
</html>"""


APP_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="问爻">
<meta name="theme-color" content="#1c1917">
<title>问爻 — 命理推演</title>
<style>
  :root {
    --bg:#fcfcfc; --card:#fff; --text:#1c1917; --sub:#8a837e; --border:#eaddd7;
    --accent:#f59e0b; --accent2:#d97706; --accent-light:#fef3c7;
    --danger:#dc2626; --shadow:0 1px 3px rgba(0,0,0,0.06),0 1px 2px rgba(0,0,0,0.04);
    --radius:10px;
  }
  @media(prefers-color-scheme:dark){
    :root { --bg:#1c1917; --card:#292524; --text:#fafaf9; --sub:#a8a29e; --border:#44403c; --accent-light:#3a2a10; --shadow:0 1px 3px rgba(0,0,0,0.3); }
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body {
    font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
    background:var(--bg); color:var(--text); min-height:100vh;
    -webkit-tap-highlight-color:transparent; overflow-x:hidden;
  }
  .header {
    background:var(--card); border-bottom:1px solid var(--border);
    padding:1rem 1.5rem; position:sticky; top:0; z-index:10; backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);
  }
  .header-inner { max-width:640px; margin:0 auto; display:flex; align-items:center; justify-content:center; }
  .logo { font-family:"STKaiti","KaiTi","楷体",serif; font-size:1.6rem; color:var(--accent2); letter-spacing:0.6em; }
  .container { max-width:640px; margin:0 auto; padding:1rem 1rem 2rem; }
  .tabs { display:flex; gap:0.3rem; margin-bottom:0.8rem; background:var(--card); border-radius:var(--radius); padding:0.3rem; box-shadow:var(--shadow); }
  .tab { flex:1; padding:0.65rem 0.3rem; border:none; background:none; cursor:pointer; border-radius:8px; font-size:0.85rem; color:var(--sub); transition:all 0.2s; font-family:inherit; white-space:nowrap; }
  .tab.active { background:var(--accent); color:#fff; font-weight:600; box-shadow:0 2px 8px rgba(245,158,11,0.3); }
  .card { background:var(--card); border-radius:var(--radius); padding:1.25rem; margin-bottom:0.8rem; box-shadow:var(--shadow); }
  .card h2 { font-size:1rem; margin-bottom:0.8rem; color:var(--text); font-weight:600; }
  .form-row { display:flex; gap:0.5rem; margin-bottom:0.5rem; flex-wrap:wrap; }
  .form-group { display:flex; flex-direction:column; gap:0.2rem; }
  .form-group label { font-size:0.75rem; color:var(--sub); font-weight:500; }
  .form-group input, .form-group select {
    padding:0.55rem 0.7rem; border:1px solid var(--border); border-radius:8px;
    font-size:0.9rem; background:var(--card); color:var(--text); font-family:inherit;
    outline:none; transition:border 0.2s; min-width:0;
  }
  .form-group input:focus, .form-group select:focus { border-color:var(--accent); box-shadow:0 0 0 3px rgba(245,158,11,0.1); }
  .btn {
    padding:0.55rem 1.4rem; background:var(--accent); color:#fff; border:none;
    border-radius:8px; font-size:0.9rem; cursor:pointer; font-weight:600;
    font-family:inherit; transition:all 0.2s; white-space:nowrap;
  }
  .btn:hover { background:var(--accent2); transform:translateY(-1px); }
  .btn:active { transform:translateY(0); }
  .btn-ai { background:var(--card); color:var(--accent2); border:1.5px solid var(--accent); }
  .btn-ai:hover { background:var(--accent-light); }
  .result { display:none; }
  .result.show { display:block; animation:fadeIn 0.3s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:translateY(0);} }
  .result-block { margin-bottom:1rem; }
  .result-block h3 { font-size:0.85rem; color:var(--sub); margin-bottom:0.35rem; padding-bottom:0.25rem; border-bottom:1px solid var(--border); text-transform:uppercase; letter-spacing:0.05em; font-weight:500; }
  .bazi-big { font-family:"STSong","SimSun","宋体",serif; font-size:1.6rem; font-weight:700; text-align:center; letter-spacing:0.25em; margin:0.5rem 0; color:var(--accent2); }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:0.5rem; }
  .tag { display:inline-block; padding:0.15rem 0.5rem; background:var(--bg); border-radius:6px; font-size:0.8rem; margin:0.1rem; }
  .loading-overlay { position:fixed; inset:0; background:var(--bg); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:9999; pointer-events:none; }
  .loading-symbol { width:44px; height:44px; border:2px solid var(--border); border-top-color:var(--accent); border-radius:50%; animation:spin 1s linear infinite; margin-bottom:20px; }
  @keyframes spin { to{transform:rotate(360deg);} }
  .loading-text { color:var(--text); font-size:1.1rem; font-weight:500; letter-spacing:0.1em; font-family:"STSong","SimSun","宋体",serif; }
  .loading-sub { margin-top:6px; color:var(--sub); font-size:0.8rem; }
  .ai-box { margin-top:0.8rem; padding:1rem; background:var(--bg); border-radius:8px; border-left:3px solid var(--accent); animation:fadeIn 0.5s ease; }
  .ai-box h3 { font-size:0.9rem; color:var(--accent2); margin-bottom:0.5rem; display:flex; align-items:center; gap:0.3rem; }
  .ai-box p { line-height:1.8; font-size:0.9rem; white-space:pre-wrap; }
  .notice { background:var(--accent-light); border-left:3px solid var(--accent); padding:0.5rem 0.8rem; border-radius:0 6px 6px 0; font-size:0.78rem; margin-bottom:0.8rem; color:var(--accent2); }
  .error { background:#fef2f2; border-left:3px solid var(--danger); padding:0.5rem 0.8rem; border-radius:0 6px 6px 0; color:var(--danger); font-size:0.8rem; margin-bottom:0.8rem; display:none; }
  @media(prefers-color-scheme:dark){ .error { background:#2a1010; } }
  .small { font-size:0.78rem; color:var(--sub); }
  .yao-line { display:flex; align-items:center; gap:0.5rem; padding:0.2rem 0; font-family:"STSong","SimSun","宋体",serif; font-size:0.9rem; }
</style>
</head>
<body>

<div id="loading-screen" class="loading-overlay">
  <div class="loading-symbol"></div>
  <div class="loading-text">天机推演中</div>
  <div class="loading-sub">问爻 · 命理推演</div>
</div>
<script>
(function() {
  var el = document.getElementById('loading-screen');
  if (!el) return;
  function hide() {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(function() { el.remove(); }, 400);
  }
  document.addEventListener('DOMContentLoaded', function() { setTimeout(hide, 100); });
  window.addEventListener('load', hide);
  setTimeout(hide, 3000);
})();
</script>

<div class="header">
  <div class="header-inner">
    <div class="logo">☯ 问  爻</div>
  </div>
</div>

<div class="container">
  <div class="tabs">
    <button class="tab active" data-tab="bazi">八字</button>
    <button class="tab" data-tab="meihua">梅花</button>
    <button class="tab" data-tab="liuyao">六爻</button>
    <button class="tab" data-tab="xingpan">星盘</button>
  </div>

  <div id="tab-desc" style="text-align:center;padding:0.6rem 0.5rem;color:var(--sub);font-size:0.82rem;line-height:1.6;"></div>
  <div class="notice">本工具仅供传统文化研究参考，不构成任何决策建议。</div>
  <div class="error" id="error"></div>

  <!-- 八字 -->
  <div class="card tab-content" id="tab-bazi">
    <h2>请输入出生信息</h2>
    <div class="form-row">
      <div class="form-group"><label>年</label><input type="number" id="bz_year" value="" value="1989" placeholder="1989" min="1900" max="2100"></div>
      <div class="form-group"><label>月</label><input type="number" id="bz_month" value="" value="6" placeholder="6" min="1" max="12"></div>
      <div class="form-group"><label>日</label><input type="number" id="bz_day" value="" value="28" placeholder="28" min="1" max="31"></div>
      <div class="form-group"><label>时 (0-23)</label><input type="number" id="bz_hour" value="" value="5" placeholder="5" min="0" max="23"></div>
      <div class="form-group"><label>分</label><input type="number" id="bz_min" value="" value="30" placeholder="30" min="0" max="59"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>性别</label><select id="bz_gender"><option>男</option><option>女</option></select></div>
      <div class="form-group"><label>出生地（可选）</label><input type="text" id="bz_place" placeholder="如：北京" style="width:180px;"></div>
    </div>
    <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.3rem;">
      <button class="btn" onclick="doBazi()">排盘</button>
      <button class="btn" onclick="doBaziAI()" style="background:var(--accent2);">推演</button>
    </div>
    <div class="result" id="bz-result"></div>
  </div>

  <!-- 梅花 -->
  <div class="card tab-content" id="tab-meihua" style="display:none;">
    <h2>梅花易数 — 三数起卦</h2>
    <div class="form-row">
      <div class="form-group"><label>数字 1</label><input type="number" id="mh_a" value="5" placeholder="5"></div>
      <div class="form-group"><label>数字 2</label><input type="number" id="mh_b" value="2" placeholder="2"></div>
      <div class="form-group"><label>数字 3</label><input type="number" id="mh_c" value="0" placeholder="0"></div>
      <div class="form-group"><label>所问之事（可选）</label><input type="text" id="mh_q" placeholder="如：问事业" style="width:200px;"></div>
    </div>
    <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.3rem;">
      <button class="btn" onclick="doMeihua()">起卦</button>
      <button class="btn" onclick="doMeihuaAI()" style="background:var(--accent2);">推演</button>
    </div>
    <div class="result" id="mh-result"></div>
  </div>

  <!-- 六爻 -->
  <div class="card tab-content" id="tab-liuyao" style="display:none;">
    <h2>六爻预测</h2>
    <p class="small" style="margin-bottom:0.8rem;">输入6个数字起卦，或留空随机铜钱起卦</p>
    <div class="form-row">
      <div class="form-group"><label>数字1</label><input type="number" id="ly_n1" value="3" placeholder="3" min="0" max="9"></div>
      <div class="form-group"><label>数字2</label><input type="number" id="ly_n2" value="6" placeholder="6" min="0" max="9"></div>
      <div class="form-group"><label>数字3</label><input type="number" id="ly_n3" value="8" placeholder="8" min="0" max="9"></div>
      <div class="form-group"><label>数字4</label><input type="number" id="ly_n4" value="4" placeholder="4" min="0" max="9"></div>
      <div class="form-group"><label>数字5</label><input type="number" id="ly_n5" value="2" placeholder="2" min="0" max="9"></div>
      <div class="form-group"><label>数字6</label><input type="number" id="ly_n6" value="9" placeholder="9" min="0" max="9"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>所问之事（可选）</label><input type="text" id="ly_q" placeholder="如：问财运" style="width:200px;"></div>
    </div>
    <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.3rem;">
      <button class="btn" onclick="doLiuyao()">起卦</button>
      <button class="btn" onclick="doLiuyaoAI()" style="background:var(--accent2);">推演</button>
    </div>
    <div class="result" id="ly-result"></div>
  </div>

  <!-- 星盘 -->
  <div class="card tab-content" id="tab-xingpan" style="display:none;">
    <h2>请输入出生信息</h2>
    <div class="form-row">
      <div class="form-group"><label>年</label><input type="number" id="xp_year" value="" value="1989" placeholder="1989" min="1900" max="2100"></div>
      <div class="form-group"><label>月</label><input type="number" id="xp_month" value="" value="6" placeholder="6" min="1" max="12"></div>
      <div class="form-group"><label>日</label><input type="number" id="xp_day" value="" value="28" placeholder="28" min="1" max="31"></div>
      <div class="form-group"><label>时 (0-23)</label><input type="number" id="xp_hour" value="" value="5" placeholder="5" min="0" max="23"></div>
      <div class="form-group"><label>分</label><input type="number" id="xp_min" value="" value="30" placeholder="30" min="0" max="59"></div>
      <div class="form-group"><label>出生地（可选）</label><input type="text" id="xp_place" placeholder="如：北京" style="width:180px;"></div>
    </div>
    <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.3rem;">
      <button class="btn" onclick="doXingpan()">排盘</button>
      <button class="btn" onclick="doXingpanAI()" style="background:var(--accent2);">推演</button>
    </div>
    <div class="result" id="xp-result"></div>
  </div>
</div>

<script>
const API = '';
const tabs = document.querySelectorAll('.tab');
const tabDescs = {
  bazi: '八字由年、月、日、时四柱组成。填入公历出生时间，系统自动排盘并分析十神、藏干、纳音、大运流年与身强身弱。五行分布和喜用神助你了解自身气场偏向。',
  meihua: '梅花易数以三个数字起卦，数字可来自日期、页码等任意场景。系统推演本卦（现状）、互卦（过程）、变卦（结果），以体用生克断吉凶。默念问题，随意取三数。',
  liuyao: '六爻以六个数字（0-9）起卦，每数对应一爻。填好后系统自动装卦，判断世应、动爻并解卦。数字留空则随机铜钱起卦。问题越具体，解卦越准。',
  xingpan: '占星星盘基于西方占星学。太阳星座代表核心性格，月亮反映内在情感，上升是给人的第一印象。填写出生地可获更精准的上升/天顶度数。'
};
function switchTab(name) {
  tabs.forEach(x => x.classList.remove('active'));
  document.querySelector('[data-tab="'+name+'"]').classList.add('active');
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  document.getElementById('tab-'+name).style.display = '';
  document.getElementById('tab-desc').textContent = tabDescs[name] || '';
}
tabs.forEach(t => t.addEventListener('click', () => switchTab(t.dataset.tab)));
switchTab('bazi');

function showErr(msg) { console.error('App error:', msg); const e = document.getElementById('error'); e.textContent = msg; e.style.display = msg ? 'block' : 'none'; }
function loading(s) { document.getElementById('loading').classList.toggle('show', s); }

async function callAPI(path, body) {
  showErr(''); loading(true);
  try {
    console.log('callAPI:', path, body);
    const r = await fetch(API + path, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    console.log('Response status:', r.status);
    const text = await r.text();
    console.log('Response body:', text.substring(0, 500));
    let d;
    try { d = JSON.parse(text); } catch(e) { throw new Error('Invalid JSON: ' + text.substring(0, 200)); }
    if (d.code !== 0) throw new Error(d.error || (d.detail && d.detail[0] && d.detail[0].msg) || '请求失败');
    return d.data;
  } catch(e) { console.error('API error:', e.message); showErr(e.message); return null; }
  finally { loading(false); }
}

async function doBazi() {
  const data = await callAPI('/api/v1/bazi', {
    year:+document.getElementById('bz_year').value, month:+document.getElementById('bz_month').value,
    day:+document.getElementById('bz_day').value, hour:+document.getElementById('bz_hour').value,
    minute:+document.getElementById('bz_min').value||0,
    gender:document.getElementById('bz_gender').value, birthplace:document.getElementById('bz_place').value
  });
  if (!data) return;
  const p = data.pillars, dm = data.day_master, sa = data.strength_analysis, lk = data.luck;
  document.getElementById('bz-result').innerHTML = `
    <div class="result show">
      <div class="bazi-big">${p.year.gan}${p.year.zhi} ${p.month.gan}${p.month.zhi} ${p.day.gan}${p.day.zhi} ${p.hour.gan}${p.hour.zhi}</div>
      <div class="result-block">
        <h3>基本信息</h3>
        <div class="grid">
          <div><span class="small">日主</span><br><strong>${dm.gan}${dm.element}</strong></div>
          <div><span class="small">生肖</span><br><strong>${dm.shengxiao}</strong></div>
          <div><span class="small">身强身弱</span><br><strong>${sa.verdict}</strong></div>
          <div><span class="small">喜用神</span><br><strong>${sa.useful_elements.join(' ')}</strong></div>
        </div>
      </div>
      <div class="result-block">
        <h3>十神</h3>
        <span class="tag">年干：${data.ten_gods.year_gan}</span>
        <span class="tag">月干：${data.ten_gods.month_gan}</span>
        <span class="tag">时干：${data.ten_gods.hour_gan}</span>
      </div>
      <div class="result-block">
        <h3>纳音</h3>
        <span class="tag">${data.nayin.year}</span> → <span class="tag">${data.nayin.month}</span> → <span class="tag">${data.nayin.day}</span> → <span class="tag">${data.nayin.hour}</span>
      </div>
      <div class="result-block">
        <h3>五行分布</h3>
        <span class="tag">木 ${data.five_elements['木']}</span>
        <span class="tag">火 ${data.five_elements['火']}</span>
        <span class="tag">土 ${data.five_elements['土']}</span>
        <span class="tag">金 ${data.five_elements['金']}</span>
        <span class="tag">水 ${data.five_elements['水']}</span>
      </div>
      ${lk.current ? `<div class="result-block"><h3>当前运势</h3><div class="grid"><div><span class="small">大运</span><br><strong>${lk.current.ganzhi} (${lk.current.start_age}-${lk.current.end_age}岁)</strong></div><div><span class="small">${data.annual_fortune.year} 流年</span><br><strong>${data.annual_fortune.ganzhi} · ${data.annual_fortune.ten_god}</strong></div></div></div>` : ''}
      <div class="result-block"><h3>地支藏干</h3><span class="small">年：${data.hidden_stems.year.join(' ')} | 月：${data.hidden_stems.month.join(' ')} | 日：${data.hidden_stems.day.join(' ')} | 时：${data.hidden_stems.hour.join(' ')}</span></div>
      <p class="small" style="margin-top:1rem;text-align:center;">${data.disclaimer}</p>
    </div>`;
}

async function doMeihua() {
  const data = await callAPI('/api/v1/meihua', {
    a:+document.getElementById('mh_a').value, b:+document.getElementById('mh_b').value,
    c:+document.getElementById('mh_c').value, question:document.getElementById('mh_q').value
  });
  if (!data) return;
  const ty = data.tiyong;
  document.getElementById('mh-result').innerHTML = `
    <div class="result show">
      <div class="bazi-big">${data.bengua.name}</div>
      <div class="result-block"><h3>卦象推演</h3>
        <div class="grid">
          <div><span class="small">本卦</span><br><strong>${data.bengua.name}</strong><br><span class="small">${data.bengua.meaning}</span></div>
          <div><span class="small">互卦</span><br><strong>${data.hugua.name}</strong><br><span class="small">${data.hugua.meaning}</span></div>
          <div><span class="small">变卦</span><br><strong>${data.biangua.name}</strong><br><span class="small">${data.biangua.meaning}</span></div>
        </div>
      </div>
      <div class="result-block"><h3>体用生克</h3>
        <p><strong>体卦：</strong>${ty.ti_gua}（${data.shang_gua.wuxing}）| <strong>用卦：</strong>${ty.yong_gua}（${data.xia_gua.wuxing}）</p>
        <p style="font-size:1.1rem;margin-top:0.4rem;"><strong>${ty.result}</strong> — ${ty.description}</p>
      </div>
      <p class="small" style="margin-top:1rem;text-align:center;">${data.disclaimer}</p>
    </div>`;
}

async function doLiuyao() {
  const ns = ['ly_n1','ly_n2','ly_n3','ly_n4','ly_n5','ly_n6'].map(id => +document.getElementById(id).value);
  const data = await callAPI('/api/v1/liuyao', { numbers:ns, question:document.getElementById('ly_q').value });
  if (!data) return;
  const a = data.analysis || {};
  document.getElementById('ly-result').innerHTML = `
    <div class="result show">
      <div class="bazi-big">${data.gua_name}</div>
      <div class="result-block"><h3>排盘</h3>
        ${data.yaos.map(y => `<div style="padding:0.3rem 0;">${y.display} <strong>${y.label}</strong> ${y.shi_ying !== '-' ? '← '+y.shi_ying : ''} ${y.is_moving ? '⚡动' : ''}</div>`).join('')}
        <p class="small" style="margin-top:0.4rem;">${data.gong}宫 · ${data.gong_wuxing} | 动爻 ${data.moving_count} 个</p>
      </div>
      ${a.gua_meaning ? `<div class="result-block"><h3>解卦</h3><p><strong>卦义：</strong>${a.gua_meaning}</p><p style="margin-top:0.4rem;"><strong>变动：</strong>${a.moving_count_analysis}</p>${(a.yao_analysis||[]).map(y => `<p class="small">- ${y}</p>`).join('')}<p style="margin-top:0.6rem;color:var(--accent2);"><strong>建议：</strong>${a.overall_advice}</p></div>` : ''}
      <p class="small" style="margin-top:1rem;text-align:center;">${data.disclaimer}</p>
    </div>`;
}

async function doXingpan() {
  const data = await callAPI('/api/v1/xingpan', {
    year:+document.getElementById('xp_year').value, month:+document.getElementById('xp_month').value,
    day:+document.getElementById('xp_day').value, hour:+document.getElementById('xp_hour').value,
    minute:+document.getElementById('xp_min').value||0, birthplace:document.getElementById('xp_place').value
  });
  if (!data) return;
  const pp = data.planets;
  const planetOrder = ['太阳','月亮','水星','金星','火星','木星','土星','天王星','海王星','冥王星'];
  document.getElementById('xp-result').innerHTML = `
    <div class="result show">
      <div class="bazi-big">☀️ ${pp['太阳'].zodiac}座 🌙 ${pp['月亮'].zodiac}座</div>
      <div class="result-block"><h3>上升 & 天顶</h3>
        <div class="grid">
          <div><span class="small">上升 ASC</span><br><strong>${data.ascendant.zodiac}座</strong></div>
          <div><span class="small">天顶 MC</span><br><strong>${data.midheaven.zodiac}座</strong></div>
          <div><span class="small">主导元素</span><br><strong>${data.dominant_element}</strong></div>
          <div><span class="small">日月关系</span><br><strong>${data.sun_moon_relation}</strong></div>
        </div>
      </div>
      <div class="result-block"><h3>行星位置</h3>
        ${planetOrder.map(n => `<span class="tag">${n}：${pp[n].zodiac} ${pp[n].degree}°</span>`).join('')}
      </div>
      <div class="result-block"><h3>元素分布（个人行星）</h3>
        <span class="tag">🔥 火 ${data.element_distribution['火']}</span>
        <span class="tag">🌍 土 ${data.element_distribution['土']}</span>
        <span class="tag">💨 风 ${data.element_distribution['风']}</span>
        <span class="tag">💧 水 ${data.element_distribution['水']}</span>
      </div>
      <p class="small" style="margin-top:1rem;text-align:center;">${data.disclaimer}</p>
    </div>`;
}

async function doBaziAI() {
  const body = {
    year:+document.getElementById('bz_year').value, month:+document.getElementById('bz_month').value,
    day:+document.getElementById('bz_day').value, hour:+document.getElementById('bz_hour').value,
    minute:+document.getElementById('bz_min').value||0,
    gender:document.getElementById('bz_gender').value, birthplace:document.getElementById('bz_place').value
  };
  const data = await callAPI('/api/v1/bazi/ai', body);
  if (!data) return;
  showReading('bz-result', data.ai_reading, doBazi);
}

async function doMeihuaAI() {
  const body = { a:+document.getElementById('mh_a').value, b:+document.getElementById('mh_b').value, c:+document.getElementById('mh_c').value, question:document.getElementById('mh_q').value };
  const data = await callAPI('/api/v1/meihua/ai', body);
  if (!data) return;
  showReading('mh-result', data.ai_reading, doMeihua);
}

async function doLiuyaoAI() {
  const ns = ['ly_n1','ly_n2','ly_n3','ly_n4','ly_n5','ly_n6'].map(id => +document.getElementById(id).value);
  const body = { numbers:ns, question:document.getElementById('ly_q').value };
  const data = await callAPI('/api/v1/liuyao/ai', body);
  if (!data) return;
  showReading('ly-result', data.ai_reading, doLiuyao);
}

async function doXingpanAI() {
  const body = {
    year:+document.getElementById('xp_year').value, month:+document.getElementById('xp_month').value,
    day:+document.getElementById('xp_day').value, hour:+document.getElementById('xp_hour').value,
    minute:+document.getElementById('xp_min').value||0, birthplace:document.getElementById('xp_place').value
  };
  const data = await callAPI('/api/v1/xingpan/ai', body);
  if (!data) return;
  showReading('xp-result', data.ai_reading, doXingpan);
}

function showReading(containerId, aiText, fallbackFn) {
  const container = document.getElementById(containerId);
  // 先显示基础排盘
  fallbackFn();
  // 追加 AI 解读
  setTimeout(() => {
    const existing = container.querySelector('.ai-reading');
    if (existing) existing.remove();
    const div = document.createElement('div');
    div.className = 'ai-reading result-block show';
    div.style.cssText = 'margin-top:1rem;padding:1rem;background:var(--bg);border-radius:8px;border-left:3px solid var(--accent2);';
    div.innerHTML = `<h3>🤖 AI 白话解读</h3><p style="line-height:1.8;white-space:pre-wrap;">${aiText}</p><p class="small" style="margin-top:0.5rem;color:var(--sub);">以上解读由 AI 生成，仅供参考</p>`;
    container.appendChild(div);
    div.scrollIntoView({behavior:'smooth'});
  }, 300);
}
</script>
</body>
</html>"""


# ── 启动入口 ──
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
