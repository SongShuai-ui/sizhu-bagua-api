#!/usr/bin/env python3
"""Railway 生产环境入口 — 不使用 reload，端口从环境变量读取"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting on port {port}", flush=True)
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
