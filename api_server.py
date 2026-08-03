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


# ── 启动入口 ──
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
