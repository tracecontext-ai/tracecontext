#!/usr/bin/env python3
"""
TraceContext Developer Demo UI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run:  python demo_ui.py
Opens http://localhost:8080 automatically.

Shows developers exactly what TraceContext does:
  - Live ADR generation via GPT-4o-mini
  - Dead-end recording
  - MCP search_context() simulation
  - Claude Code integration preview
"""
import sys, subprocess, time, threading, webbrowser, os
sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import requests as _req
import uvicorn

ORCH = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
PORT = int(os.getenv("DEMO_PORT", "8080"))

app = FastAPI(title="TraceContext Demo UI")


def _orch_ok() -> bool:
    try:
        return _req.get(f"{ORCH}/", timeout=2).ok
    except Exception:
        return False


# ── Proxy routes ───────────────────────────────────────────────────────────────

@app.get("/api/status")
async def api_status():
    return {"orchestrator": "online" if _orch_ok() else "offline"}


@app.post("/api/events")
async def fwd_events(req: Request):
    try:
        r = _req.post(f"{ORCH}/events", json=await req.json(), timeout=90)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=503)


@app.get("/api/context")
async def fwd_context(query: str = ""):
    try:
        params = {"query": query} if query else {}
        r = _req.get(f"{ORCH}/context", params=params, timeout=15)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"context": [], "error": str(e)}, status_code=503)


@app.post("/api/reset")
async def fwd_reset():
    try:
        r = _req.post(f"{ORCH}/reset", timeout=5)
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=503)


# ── UI ─────────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>TraceContext — Persistent Intent History for Every Codebase</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    :root{
      --bg:#07090f;--surface:#0d1117;--surface2:#161b22;--surface3:#1c2432;
      --accent:#5865f2;--cyan:#0ea5e9;--green:#22c55e;--orange:#f97316;
      --purple:#a855f7;--text:#e2e8f0;--muted:#64748b;--muted2:#94a3b8;
      --border:rgba(255,255,255,0.07);--glow:rgba(88,101,242,0.3);
    }
    html{scroll-behavior:smooth}
    body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.6;overflow-x:hidden}
    code,pre,.mono{font-family:'JetBrains Mono','Fira Code',monospace}
    a{color:inherit;text-decoration:none}

    /* ── Nav ── */
    nav{
      position:fixed;top:0;left:0;right:0;z-index:100;height:60px;
      background:rgba(7,9,15,0.85);backdrop-filter:blur(16px);
      border-bottom:1px solid var(--border);
      padding:0 2rem;display:flex;align-items:center;justify-content:space-between;
    }
    .nav-logo{font-weight:800;font-size:1.05rem;letter-spacing:-0.02em;
      background:linear-gradient(135deg,var(--accent),var(--cyan));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .nav-links{display:flex;gap:1.5rem;align-items:center}
    .nav-links a{color:var(--muted2);font-size:0.875rem;transition:color .2s}
    .nav-links a:hover{color:var(--text)}
    .status-pill{
      display:flex;align-items:center;gap:6px;
      background:var(--surface2);border:1px solid var(--border);
      border-radius:100px;padding:.25rem .75rem;font-size:.75rem;color:var(--muted2);
    }
    .dot{width:7px;height:7px;border-radius:50%;background:var(--muted);transition:background .4s}
    .dot.online{background:var(--green);box-shadow:0 0 6px var(--green)}
    .dot.offline{background:var(--orange)}

    /* ── Hero ── */
    .hero{
      min-height:100vh;display:flex;flex-direction:column;
      align-items:center;justify-content:center;
      text-align:center;padding:7rem 2rem 5rem;
      position:relative;overflow:hidden;
    }
    .hero::before{
      content:'';position:absolute;inset:0;pointer-events:none;
      background:
        radial-gradient(ellipse 80% 60% at 50% -10%,rgba(88,101,242,.2),transparent 70%),
        radial-gradient(circle,rgba(255,255,255,.03) 1px,transparent 1px);
      background-size:100% 100%,28px 28px;
    }
    .hero-badge{
      display:inline-flex;align-items:center;gap:6px;
      background:rgba(88,101,242,.1);border:1px solid rgba(88,101,242,.3);
      border-radius:100px;padding:.35rem 1rem;
      font-size:.78rem;font-weight:600;color:var(--cyan);margin-bottom:2rem;letter-spacing:.02em;
    }
    .hero h1{
      font-size:clamp(2.4rem,6vw,4.8rem);font-weight:800;line-height:1.08;
      margin-bottom:1.5rem;max-width:820px;letter-spacing:-.03em;
    }
    .grad{background:linear-gradient(135deg,var(--accent) 0%,var(--cyan) 100%);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .hero p{
      font-size:clamp(.95rem,2vw,1.2rem);color:var(--muted2);
      max-width:620px;margin-bottom:3rem;line-height:1.85;
    }
    .cta-row{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-bottom:2.5rem}
    .btn-primary{
      background:var(--accent);color:#fff;padding:.9rem 2rem;
      border-radius:9px;border:none;cursor:pointer;
      font-size:.95rem;font-weight:700;font-family:inherit;
      display:inline-flex;align-items:center;gap:.5rem;
      transition:all .2s;box-shadow:0 0 30px var(--glow);
    }
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 0 45px var(--glow)}
    .btn-secondary{
      background:var(--surface2);color:var(--text);padding:.9rem 2rem;
      border-radius:9px;border:1px solid var(--border);cursor:pointer;
      font-size:.95rem;font-weight:600;font-family:inherit;
      display:inline-flex;align-items:center;gap:.5rem;transition:all .2s;
    }
    .btn-secondary:hover{border-color:rgba(255,255,255,.18);transform:translateY(-2px)}
    .install-pill{
      display:inline-flex;align-items:center;gap:1rem;
      background:var(--surface);border:1px solid var(--border);
      border-radius:10px;padding:.8rem 1.5rem;
    }
    .install-pill code{color:var(--cyan);font-size:.95rem}
    .copy-btn{background:none;border:none;cursor:pointer;color:var(--muted2);
      font-size:.85rem;transition:color .2s;padding:0;line-height:1}
    .copy-btn:hover{color:var(--text)}

    /* ── Stats bar ── */
    .stats-bar{display:grid;grid-template-columns:repeat(3,1fr);
      gap:1px;background:var(--border);
      border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
    .stat{background:var(--surface);padding:2.5rem 1rem;text-align:center}
    .stat-num{font-size:2.75rem;font-weight:800;letter-spacing:-.04em;
      background:linear-gradient(135deg,var(--accent),var(--cyan));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .stat-label{font-size:.82rem;color:var(--muted2);margin-top:.35rem;line-height:1.5}

    /* ── Generic section ── */
    .section{padding:5.5rem 2rem;max-width:1120px;margin:0 auto}
    .label{
      display:inline-block;background:rgba(88,101,242,.1);
      border:1px solid rgba(88,101,242,.3);border-radius:5px;
      padding:.25rem .75rem;font-size:.72rem;font-weight:700;
      color:var(--accent);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1rem;
    }
    h2{font-size:clamp(1.75rem,3.5vw,2.6rem);font-weight:700;margin-bottom:1rem;line-height:1.15;letter-spacing:-.02em}
    .sub{color:var(--muted2);font-size:1.05rem;max-width:580px;line-height:1.8}

    /* ── Problem cards ── */
    .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:1.5rem;margin-top:3rem}
    .card{
      background:var(--surface);border:1px solid var(--border);
      border-radius:14px;padding:2rem;transition:border-color .2s,transform .2s;
    }
    .card:hover{border-color:rgba(88,101,242,.4);transform:translateY(-4px)}
    .card-icon{font-size:2rem;margin-bottom:1rem}
    .card h3{font-size:1.05rem;font-weight:600;margin-bottom:.5rem}
    .card p{color:var(--muted2);font-size:.875rem;line-height:1.65}

    /* ── Flow diagram ── */
    .flow{display:flex;align-items:center;gap:0;overflow-x:auto;
      padding:2.5rem 1rem;margin:3rem -1rem 0}
    .flow-step{
      flex:1;min-width:140px;
      background:var(--surface);border:1px solid var(--border);
      border-radius:12px;padding:1.5rem .75rem;text-align:center;
    }
    .flow-step.hl{background:rgba(88,101,242,.08);border-color:rgba(88,101,242,.45)}
    .fi{font-size:1.75rem;margin-bottom:.6rem}
    .ft{font-size:.82rem;font-weight:600;margin-bottom:.2rem}
    .fs{font-size:.7rem;color:var(--muted2)}
    .arr{flex:0 0 36px;text-align:center;color:var(--muted);font-size:1.1rem;user-select:none}

    /* ── Demo section ── */
    .demo-wrap{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:5.5rem 2rem}
    .demo-inner{max-width:1120px;margin:0 auto}
    .demo-controls{display:flex;align-items:center;gap:.75rem;margin:2rem 0 1.5rem;flex-wrap:wrap}
    .sc-select{
      background:var(--surface2);border:1px solid var(--border);color:var(--text);
      padding:.6rem 1rem;border-radius:9px;font-family:inherit;font-size:.875rem;cursor:pointer;
    }
    .run-btn{
      background:var(--green);color:#000;font-weight:800;
      padding:.6rem 1.5rem;border-radius:9px;border:none;cursor:pointer;
      font-family:inherit;font-size:.875rem;display:flex;align-items:center;gap:.5rem;
      transition:all .2s;
    }
    .run-btn:hover{transform:translateY(-2px);box-shadow:0 0 20px rgba(34,197,94,.4)}
    .run-btn:disabled{opacity:.45;cursor:not-allowed;transform:none;box-shadow:none}
    .clear-btn{
      background:none;border:1px solid var(--border);color:var(--muted2);
      padding:.6rem 1rem;border-radius:9px;cursor:pointer;font-family:inherit;font-size:.875rem;
      transition:border-color .2s,color .2s;
    }
    .clear-btn:hover{border-color:rgba(255,255,255,.2);color:var(--text)}

    .demo-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
    @media(max-width:768px){.demo-grid{grid-template-columns:1fr}}

    /* Terminal */
    .terminal{background:#010409;border:1px solid var(--border);border-radius:14px;overflow:hidden}
    .term-bar{
      background:var(--surface2);padding:.7rem 1rem;
      display:flex;align-items:center;gap:.5rem;border-bottom:1px solid var(--border);
    }
    .td{width:12px;height:12px;border-radius:50%}
    .term-title{font-size:.72rem;color:var(--muted);margin-left:auto}
    .term-body{
      padding:1.25rem;min-height:420px;max-height:420px;
      overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:.78rem;line-height:1.8;
    }
    .term-body::-webkit-scrollbar{width:4px}
    .term-body::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
    .term-body p{margin:0}

    .lc{color:#22d3ee}   /* $ commands */
    .lo{color:#4ade80}   /* ok / received */
    .la{color:#a78bfa}   /* ADR */
    .ld{color:#fb923c}   /* dead-end */
    .ls{color:#38bdf8}   /* search */
    .lm{color:#374151}   /* muted separator */
    .lx{color:#4ade80;font-weight:700} /* done */
    .le{color:#f87171}   /* error */
    .li{color:#64748b}   /* info */

    /* Context panel */
    .ctx-panel{background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden}
    .ctx-bar{
      background:var(--surface2);padding:.7rem 1rem;font-size:.75rem;font-weight:600;
      color:var(--muted2);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.5rem;
    }
    .ctx-body{padding:1.25rem;min-height:420px;max-height:420px;overflow-y:auto}
    .ctx-body::-webkit-scrollbar{width:4px}
    .ctx-body::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
    .ctx-rec{
      background:var(--surface2);border:1px solid var(--border);
      border-radius:10px;padding:1rem;margin-bottom:.75rem;
      font-size:.78rem;line-height:1.65;animation:fadeUp .35s ease;
    }
    .ctx-rec.adr{border-left:3px solid var(--purple)}
    .ctx-rec.dead{border-left:3px solid var(--orange)}
    .ctx-badge{
      display:inline-block;font-size:.65rem;font-weight:700;padding:.1rem .5rem;
      border-radius:4px;margin-bottom:.4rem;font-family:'JetBrains Mono',monospace;
    }
    .b-adr{background:rgba(168,85,247,.18);color:#a78bfa}
    .b-dead{background:rgba(249,115,22,.18);color:#fb923c}
    .ctx-title{font-weight:600;color:var(--text);margin-bottom:.3rem}
    .ctx-desc{color:var(--muted2);font-size:.73rem}

    /* ── Claude preview ── */
    .claude-section{padding:5.5rem 2rem}
    .claude-inner{max-width:1120px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}
    @media(max-width:768px){.claude-inner{grid-template-columns:1fr}}
    .claude-win{background:#010409;border:1px solid var(--border);border-radius:14px;overflow:hidden}
    .cl-bar{
      background:var(--surface2);padding:.7rem 1rem;
      display:flex;align-items:center;gap:.75rem;border-bottom:1px solid var(--border);
    }
    .cl-av{
      width:26px;height:26px;border-radius:50%;
      background:linear-gradient(135deg,var(--accent),var(--cyan));
      display:flex;align-items:center;justify-content:center;
      font-size:.65rem;font-weight:800;color:#fff;
    }
    .cl-title{font-size:.8rem;font-weight:600}
    .cl-body{padding:1.25rem 1.5rem;font-size:.8rem;line-height:1.85}
    .msg{margin-bottom:1rem}
    .msg-u{color:var(--muted2)}
    .msg-u::before{content:"You  ";color:var(--cyan);font-weight:700;font-family:'JetBrains Mono',monospace}
    .msg-c::before{content:"Claude  ";color:var(--accent);font-weight:700;font-family:'JetBrains Mono',monospace}
    .mcp-call{
      background:rgba(88,101,242,.08);border:1px solid rgba(88,101,242,.2);
      border-radius:7px;padding:.45rem .85rem;margin:.4rem 0;
      font-family:'JetBrains Mono',monospace;font-size:.73rem;color:var(--cyan);
    }
    .kv-list{margin:.4rem 0;padding-left:1.1rem}
    .kv-list li{color:var(--muted2);margin-bottom:.2rem;font-size:.78rem}

    /* ── Quick start ── */
    .steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:1.5rem;margin-top:3rem}
    .step{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:2rem}
    .step-num{
      width:32px;height:32px;border-radius:50%;
      background:rgba(88,101,242,.12);border:1px solid rgba(88,101,242,.35);
      color:var(--accent);font-weight:700;font-size:.9rem;
      display:flex;align-items:center;justify-content:center;margin-bottom:1rem;
    }
    .step h3{font-size:1rem;font-weight:600;margin-bottom:.8rem}
    .code-blk{
      background:#010409;border:1px solid var(--border);border-radius:9px;
      padding:1rem 1.1rem;position:relative;
      font-family:'JetBrains Mono',monospace;font-size:.78rem;
      color:var(--cyan);line-height:1.85;
    }
    .ci{
      position:absolute;top:.7rem;right:.7rem;background:none;border:none;
      cursor:pointer;color:var(--muted);font-size:.78rem;transition:color .2s;
    }
    .ci:hover{color:var(--text)}

    /* ── MCP config ── */
    .mcp-section{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:5.5rem 2rem}
    .mcp-inner{max-width:1120px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:start}
    @media(max-width:768px){.mcp-inner{grid-template-columns:1fr}}
    .tool-list{margin-top:1.5rem;display:flex;flex-direction:column;gap:.75rem}
    .tool{
      background:var(--surface2);border:1px solid var(--border);border-radius:10px;
      padding:1rem 1.25rem;display:flex;align-items:flex-start;gap:.85rem;
    }
    .tool-icon{font-size:1.25rem;margin-top:.1rem}
    .tool-name{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--cyan);margin-bottom:.2rem}
    .tool-desc{font-size:.8rem;color:var(--muted2);line-height:1.55}

    /* ── Footer ── */
    footer{border-top:1px solid var(--border);padding:2.5rem 2rem;text-align:center;color:var(--muted)}
    footer a{color:var(--muted2);transition:color .2s}
    footer a:hover{color:var(--text)}
    footer p+p{margin-top:.4rem}

    /* ── Animations ── */
    @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    .spinner{
      display:inline-block;width:12px;height:12px;
      border:2px solid rgba(255,255,255,.2);border-top-color:currentColor;
      border-radius:50%;animation:spin .75s linear infinite;
    }
    .pulse{animation:pulse 1.6s ease-in-out infinite}

    /* ── About section ── */
    .about-section{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:5.5rem 2rem}
    .about-inner{max-width:1120px;margin:0 auto}
    .about-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:4rem;align-items:start;margin:2.5rem 0 4rem}
    @media(max-width:768px){.about-grid{grid-template-columns:1fr}}
    .about-p{color:var(--muted2);font-size:1rem;line-height:1.85;margin-bottom:1.25rem}
    .vision-card{
      background:linear-gradient(135deg,rgba(88,101,242,.12),rgba(14,165,233,.06));
      border:1px solid rgba(88,101,242,.25);border-radius:16px;padding:2rem;
    }
    .vision-quote{font-size:4rem;line-height:.8;color:var(--accent);opacity:.4;font-family:Georgia,serif;margin-bottom:.5rem}
    .vision-text{font-size:.95rem;line-height:1.85;color:var(--muted2);font-style:italic;margin-bottom:1.25rem}
    .vision-sig{font-size:.8rem;color:var(--muted);font-weight:600;letter-spacing:.05em;text-transform:uppercase}
    .why-section{margin-top:0}
    .why-title{font-size:1.35rem;font-weight:700;margin-bottom:.75rem}
    .why-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.25rem;margin-top:0}
    .why-card{
      background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:1.5rem;
      transition:border-color .2s,transform .2s;
    }
    .why-card:hover{border-color:rgba(88,101,242,.35);transform:translateY(-3px)}
    .why-icon{font-size:1.6rem;margin-bottom:.75rem}
    .why-card h4{font-size:.95rem;font-weight:600;margin-bottom:.5rem}
    .why-card p{font-size:.82rem;color:var(--muted2);line-height:1.65}
    .open-source-banner{
      display:flex;align-items:center;justify-content:space-between;gap:2rem;
      margin-top:3rem;padding:2rem;
      background:rgba(88,101,242,.06);border:1px solid rgba(88,101,242,.2);
      border-radius:14px;flex-wrap:wrap;
    }

    /* ── Installation ── */
    .prereq-box{
      background:var(--surface);border:1px solid var(--border);border-radius:12px;
      padding:1.25rem 1.5rem;margin:2.5rem 0;
    }
    .prereq-title{font-size:.72rem;font-weight:700;color:var(--accent);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.75rem}
    .prereq-list{display:flex;flex-wrap:wrap;gap:.6rem}
    .prereq-item{
      background:var(--surface2);border:1px solid var(--border);border-radius:100px;
      padding:.25rem .85rem;font-size:.8rem;color:var(--muted2);
      font-family:'JetBrains Mono',monospace;
    }
    .install-steps{display:flex;flex-direction:column;gap:0;margin-top:2rem}
    .install-step{
      display:grid;grid-template-columns:80px 1fr;gap:0;
      padding:2rem 0;border-bottom:1px solid var(--border);
    }
    .install-step:last-child{border-bottom:none}
    .is-num{
      font-size:.72rem;font-weight:700;color:var(--accent);
      letter-spacing:.08em;text-transform:uppercase;
      padding-top:.2rem;
    }
    .is-body h3{font-size:1.05rem;font-weight:700;margin-bottom:.6rem}
    .is-body p{font-size:.875rem;color:var(--muted2);line-height:1.7;margin-bottom:.85rem}
    .is-body p:last-of-type{margin-bottom:0}
    .ic{
      background:var(--surface2);border:1px solid var(--border);border-radius:5px;
      padding:.1rem .4rem;font-size:.75rem;color:var(--cyan);
    }
    .tool-tabs{margin-top:.5rem}
    .tool-tab-content{line-height:1.9}
    @media(max-width:600px){
      .install-step{grid-template-columns:1fr}
      .is-num{margin-bottom:.5rem}
    }

    @media(max-width:600px){
      .stats-bar{grid-template-columns:1fr}
      .flow{flex-direction:column}
      .arr{transform:rotate(90deg)}
      .nav-links a:not(:last-child){display:none}
    }
  </style>
</head>
<body>

<!-- ── Nav ──────────────────────────────────────────────────────────────────── -->
<nav>
  <div class="nav-logo">⬡ TraceContext <span style="font-weight:400;opacity:.55;font-size:.8em">· tracecontext-ai</span></div>
  <div class="nav-links">
    <a href="#about">About</a>
    <a href="#how">How it Works</a>
    <a href="#demo">Live Demo</a>
    <a href="#quickstart">Install</a>
    <a href="https://github.com/tracecontext-ai/tracecontext" target="_blank">GitHub ↗</a>
    <div class="status-pill">
      <span class="dot" id="orch-dot"></span>
      <span id="orch-label">checking…</span>
    </div>
  </div>
</nav>

<!-- ── Hero ─────────────────────────────────────────────────────────────────── -->
<header class="hero">
  <div class="hero-badge">✦ Open Source &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; v0.1.0 &nbsp;·&nbsp; <a href="https://github.com/tracecontext-ai/tracecontext" target="_blank" style="color:inherit;text-decoration:underline dotted">github.com/tracecontext-ai</a></div>
  <h1>Your codebase now has a memory.<br><span class="grad">TraceContext tracks your intent history — automatically.</span></h1>
  <p>
    Every architectural decision automatically captured. Every dead-end documented.
    Your AI tools know your architecture and reasoning before you even ask a question.
  </p>
  <div class="cta-row">
    <button class="btn-primary" onclick="scrollTo('#demo')">▶&nbsp; Run Live Demo</button>
    <a class="btn-secondary" href="https://github.com/tracecontext-ai/tracecontext" target="_blank">⭐&nbsp; Star on GitHub</a>
  </div>
  <div class="install-pill">
    <code>$ pip install tracecontext</code>
    <button class="copy-btn" title="Copy" onclick="copyText('pip install tracecontext',this)">📋</button>
  </div>
</header>

<!-- ── Stats bar ────────────────────────────────────────────────────────────── -->
<div class="stats-bar">
  <div class="stat">
    <div class="stat-num">3</div>
    <div class="stat-label">AI agents — distiller · dead-end · ranker</div>
  </div>
  <div class="stat">
    <div class="stat-num">1</div>
    <div class="stat-label">MCP server — Claude Code · Cursor · Windsurf · Antigravity</div>
  </div>
  <div class="stat">
    <div class="stat-num">0</div>
    <div class="stat-label">re-explanations needed per AI session</div>
  </div>
</div>

<!-- ── Problem ───────────────────────────────────────────────────────────────── -->
<div class="section">
  <div class="label">The Problem</div>
  <h2>Intent disappears. Context gets lost. Teams repeat mistakes.</h2>
  <p class="sub">
    Every AI session starts from zero. You re-explain the same architecture daily.
    Decisions made months ago get re-debated. Failed approaches get tried again.
    Your team's hard-won knowledge lives nowhere permanent.
  </p>
  <div class="cards">
    <div class="card">
      <div class="card-icon">🧠</div>
      <h3>AI Tools Have No Memory</h3>
      <p>Every session starts blank. "We use Stripe, not Braintree" — explained again and again, to every tool, every morning.</p>
    </div>
    <div class="card">
      <div class="card-icon">🔄</div>
      <h3>Decisions Get Re-debated</h3>
      <p>"Why integer cents and not float?" — answered three times this quarter by three different developers to three different AI tools.</p>
    </div>
    <div class="card">
      <div class="card-icon">💀</div>
      <h3>Dead-ends Get Revisited</h3>
      <p>A new joiner — or a new AI session — tries the JWT approach your team already abandoned. Weeks of work, thrown away again.</p>
    </div>
    <div class="card">
      <div class="card-icon">📤</div>
      <h3>Knowledge Walks Out the Door</h3>
      <p>When a senior developer leaves, every architectural decision they held in their head disappears with them. There is no system of record for intent.</p>
    </div>
  </div>
</div>

<!-- ── How it works ─────────────────────────────────────────────────────────── -->
<div class="section" id="how">
  <div class="label">How It Works</div>
  <h2>Code change → AI distiller → Intent store → Your AI tools</h2>
  <p class="sub">
    TraceContext runs silently alongside your development workflow.
    Zero friction — every code change is captured and distilled automatically.
  </p>
  <div class="flow">
    <div class="flow-step">
      <div class="fi">📝</div>
      <div class="ft">Code Change</div>
      <div class="fs">Commit, refactor, revert</div>
    </div>
    <div class="arr">→</div>
    <div class="flow-step">
      <div class="fi">🪝</div>
      <div class="ft">Auto Capture</div>
      <div class="fs">Hook fires instantly</div>
    </div>
    <div class="arr">→</div>
    <div class="flow-step hl">
      <div class="fi">⬡</div>
      <div class="ft">TraceContext</div>
      <div class="fs">GPT-4o-mini distills intent</div>
    </div>
    <div class="arr">→</div>
    <div class="flow-step">
      <div class="fi">📚</div>
      <div class="ft">Intent Store</div>
      <div class="fs">ADRs + dead-ends</div>
    </div>
    <div class="arr">→</div>
    <div class="flow-step">
      <div class="fi">🔌</div>
      <div class="ft">MCP Server</div>
      <div class="fs">search_context() tool</div>
    </div>
    <div class="arr">→</div>
    <div class="flow-step">
      <div class="fi">🤖</div>
      <div class="ft">Your AI Tools</div>
      <div class="fs">Context-aware answers</div>
    </div>
  </div>
</div>

<!-- ── Live Demo ─────────────────────────────────────────────────────────────── -->
<div class="demo-wrap" id="demo">
  <div class="demo-inner">
    <div class="label">Live Demo</div>
    <h2>Watch it work — real API calls, real AI output</h2>
    <p class="sub">
      Simulates code change events hitting your orchestrator. GPT-4o-mini generates real ADRs.
      MCP search shows exactly what your AI tool would receive.
    </p>

    <div class="demo-controls">
      <select class="sc-select" id="sc-select">
        <option value="payment">💳 Payment Service Migration</option>
        <option value="auth">🔐 Auth System Redesign</option>
      </select>
      <button class="run-btn" id="run-btn" onclick="runDemo()">▶ Run Demo</button>
      <button class="clear-btn" onclick="clearAll()">Clear</button>
    </div>

    <div class="demo-grid">
      <!-- Terminal -->
      <div>
        <div class="terminal">
          <div class="term-bar">
            <span class="td" style="background:#ff5f57"></span>
            <span class="td" style="background:#ffbd2e"></span>
            <span class="td" style="background:#28ca41"></span>
            <span class="term-title">TraceContext event stream</span>
          </div>
          <div class="term-body" id="terminal">
            <p class="li"># Select a scenario above and click Run Demo</p>
            <p class="li"># Git commits and dead-ends will stream here</p>
            <p class="li"># GPT-4o-mini generates ADRs in real time</p>
          </div>
        </div>
      </div>

      <!-- Context panel -->
      <div>
        <div class="ctx-panel">
          <div class="ctx-bar">
            📚 Generated Context Records
            <span id="rec-count" style="margin-left:auto;background:rgba(88,101,242,.18);padding:.1rem .55rem;border-radius:5px;font-size:.7rem;color:var(--accent)">0 records</span>
          </div>
          <div class="ctx-body" id="ctx-panel">
            <p style="color:var(--muted);font-size:.82rem;text-align:center;margin-top:4rem;line-height:1.8">
              Run the demo to see<br>AI-generated ADRs and dead-end<br>records appear here
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ── AI Tool Integration Preview ──────────────────────────────────────────── -->
<div class="claude-section">
  <div class="claude-inner">
    <div>
      <div class="label">MCP Integration</div>
      <h2>Your AI tools answer from your real intent history</h2>
      <p class="sub" style="margin-bottom:1.5rem">
        When you ask your AI assistant a question, it automatically calls
        <code style="color:var(--cyan);font-size:.9rem">search_context()</code> first —
        then answers using <em>your actual ADRs and intent history</em>, not generic advice.
      </p>
      <p class="sub">Works with <strong>Cursor</strong>, <strong>Windsurf</strong>,
        <strong>Zed</strong>, <strong>Antigravity</strong>, and every
        MCP-compatible AI coding tool.</p>
    </div>
    <div class="claude-win">
      <div class="cl-bar">
        <div class="cl-av">AI</div>
        <div class="cl-title">AI Assistant (MCP-connected)</div>
        <div style="margin-left:auto;font-size:.72rem;color:var(--green)">● TraceContext connected</div>
      </div>
      <div class="cl-body">
        <div class="msg msg-u">Add a new payment method to checkout</div>
        <div class="msg msg-c">
          Let me check your intent history before writing any code.
          <div class="mcp-call">🔌 search_context("payment") → 3 results from your ADR store</div>
          Based on your recorded decisions I can see:
          <ul class="kv-list">
            <li>✓ Use <strong>Stripe PaymentIntents</strong> — Braintree reverted (46-country limit, abandoned SDK)</li>
            <li>✓ Store amounts as <strong>Money objects with integer cents</strong> — float causes $0.01 rounding errors</li>
            <li>✓ Always set <strong>idempotency_key</strong> on every mutation</li>
          </ul>
          Here's an implementation that follows your established patterns and documented intent…
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ── MCP Config ────────────────────────────────────────────────────────────── -->
<div class="mcp-section">
  <div class="mcp-inner">
    <div>
      <div class="label">MCP Tools</div>
      <h2>Three tools, called automatically</h2>
      <p class="sub">TraceContext exposes three MCP tools. Your AI tool calls them transparently — no prompting needed from you.</p>
      <div class="tool-list">
        <div class="tool">
          <div class="tool-icon">🔍</div>
          <div>
            <div class="tool-name">search_context(query)</div>
            <div class="tool-desc">Keyword search across your entire intent history — ADRs and dead-ends. Called before every answer.</div>
          </div>
        </div>
        <div class="tool">
          <div class="tool-icon">📋</div>
          <div>
            <div class="tool-name">add_decision(title, decision, context)</div>
            <div class="tool-desc">Lets your AI tool record decisions it helps you make during a session — added to the permanent intent history.</div>
          </div>
        </div>
        <div class="tool">
          <div class="tool-icon">🚫</div>
          <div>
            <div class="tool-name">add_dead_end(approach, reason)</div>
            <div class="tool-desc">Record failed approaches in real-time so no developer or AI tool repeats them.</div>
          </div>
        </div>
      </div>
      <div style="margin-top:1.5rem;padding:1rem;background:var(--surface3);border-radius:10px;border:1px solid var(--border)">
        <p style="font-size:.78rem;color:var(--muted2);line-height:1.7">
          ✓ &nbsp;<strong style="color:var(--text)">Cursor</strong> &nbsp;·&nbsp;
          <strong style="color:var(--text)">Windsurf</strong> &nbsp;·&nbsp;
          <strong style="color:var(--text)">Zed</strong> &nbsp;·&nbsp;
          <strong style="color:var(--text)">Antigravity</strong> &nbsp;·&nbsp;
          any MCP-compatible AI tool
        </p>
      </div>
    </div>
    <div>
      <p style="font-size:.8rem;color:var(--muted2);margin-bottom:.75rem;font-family:'JetBrains Mono',monospace">MCP config (add to your AI tool's settings)</p>
      <div class="code-blk" style="font-size:.75rem">
{<br>
&nbsp;&nbsp;<span style="color:#a78bfa">"mcpServers"</span>: {<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"tracecontext"</span>: {<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"command"</span>: <span style="color:#86efac">"tracecontext"</span>,<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"args"</span>: [<span style="color:#86efac">"mcp"</span>],<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"env"</span>: {<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"ORCHESTRATOR_URL"</span>: <span style="color:#86efac">"http://localhost:8000"</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br>
&nbsp;&nbsp;&nbsp;&nbsp;}<br>
&nbsp;&nbsp;}<br>
}
        <button class="ci" onclick="copyMcp(event)" title="Copy config">📋</button>
      </div>
      <p style="font-size:.75rem;color:var(--muted);margin-top:.75rem;line-height:1.6">
        Paste this into your AI tool's MCP settings file.<br>
        Reload — TraceContext is connected.
      </p>
    </div>
  </div>
</div>

<!-- ── About ──────────────────────────────────────────────────────────────────── -->
<div class="about-section" id="about">
  <div class="about-inner">
    <div class="label">About</div>
    <h2>The intent history layer every software team needs.</h2>

    <div class="about-grid">
      <div>
        <p class="about-p">
          Every software project accumulates invisible knowledge — the architectural
          decisions made, the approaches abandoned, the reasons behind every choice.
          This knowledge lives in developers' heads, in Slack threads, in outdated
          wiki pages nobody reads.
        </p>
        <p class="about-p">
          When a developer leaves, that knowledge leaves with them. When you start
          a new AI session, it starts from zero — because there is no permanent
          place for <em>intent</em> to live.
        </p>
        <p class="about-p">
          <strong style="color:var(--text)">TraceContext is that place.</strong>
          It runs silently alongside your development workflow, capturing the intent
          behind every change. Decisions are recorded. Failed approaches are documented.
          When your AI tool starts a session, the full context is already there.
        </p>
      </div>
      <div class="vision-card">
        <div class="vision-quote">"</div>
        <p class="vision-text">
          In the age of AI-assisted development, the bottleneck is not code —
          it's context. TraceContext makes your team's intent history a
          first-class artifact, as persistent and queryable as the code itself.
        </p>
        <p class="vision-sig">— TraceContext Mission</p>
      </div>
    </div>

    <div class="why-section">
      <h3 class="why-title">Why TraceContext matters right now</h3>
      <p style="color:var(--muted2);font-size:.95rem;line-height:1.7;margin-bottom:2rem;max-width:680px">
        In 2025, AI coding assistants are standard tools in every developer's workflow.
        But they all share one fundamental flaw: they have no persistent memory.
        TraceContext fills this gap — permanently.
      </p>
      <div class="why-cards">
        <div class="why-card">
          <div class="why-icon">🤖</div>
          <h4>AI Tools Need Context</h4>
          <p>Your AI assistant is powerful but amnesiac. Every session starts blank. TraceContext gives it your complete architectural history — automatically, before you ask your first question.</p>
        </div>
        <div class="why-card">
          <div class="why-icon">🏛️</div>
          <h4>Institutional Knowledge at Risk</h4>
          <p>Senior developers carry years of decision context in their heads. When they leave, it's gone. TraceContext preserves this knowledge as a searchable, permanent record.</p>
        </div>
        <div class="why-card">
          <div class="why-icon">🔁</div>
          <h4>The Dead-end Problem</h4>
          <p>Teams walk the same failed paths repeatedly because failure context isn't captured anywhere. TraceContext breaks this cycle — document a dead-end once, never repeat it.</p>
        </div>
        <div class="why-card">
          <div class="why-icon">🚀</div>
          <h4>Onboarding in Minutes</h4>
          <p>New team members spend weeks learning what was decided and why. With TraceContext, the full decision history is queryable from day one — by humans and AI tools alike.</p>
        </div>
      </div>
    </div>

    <div class="open-source-banner">
      <div>
        <h3 style="font-size:1.2rem;font-weight:700;margin-bottom:.5rem">Open Source · MIT Licensed · Self-hosted</h3>
        <p style="color:var(--muted2);font-size:.9rem;line-height:1.7">
          Run it locally. Self-host it. Extend it. Your intent history belongs to you —
          not a cloud vendor, not a SaaS platform.
          TraceContext is infrastructure for your team's institutional memory.
        </p>
      </div>
      <a class="btn-secondary" href="https://github.com/tracecontext-ai/tracecontext" target="_blank" style="white-space:nowrap">⭐ View on GitHub</a>
    </div>
  </div>
</div>

<!-- ── Installation ──────────────────────────────────────────────────────────── -->
<div class="section" id="quickstart">
  <div class="label">Installation</div>
  <h2>Step-by-step setup guide</h2>
  <p class="sub">No database required. No cloud account needed. Runs entirely on your machine.</p>

  <div class="prereq-box">
    <div class="prereq-title">Prerequisites</div>
    <div class="prereq-list">
      <span class="prereq-item">Python 3.9+</span>
      <span class="prereq-item">pip</span>
      <span class="prereq-item">OpenAI API key (for GPT-4o-mini distillation)</span>
      <span class="prereq-item">Any MCP-compatible AI coding tool</span>
    </div>
  </div>

  <div class="install-steps">

    <div class="install-step">
      <div class="is-num">Step 1</div>
      <div class="is-body">
        <h3>Install TraceContext</h3>
        <p>Install the package from PyPI. This gives you the <code class="ic">tracecontext</code> CLI and the full library.</p>
        <div class="code-blk">
          $ pip install tracecontext
          <button class="ci" onclick="copyText('pip install tracecontext',this)">📋</button>
        </div>
      </div>
    </div>

    <div class="install-step">
      <div class="is-num">Step 2</div>
      <div class="is-body">
        <h3>Set your OpenAI API key</h3>
        <p>TraceContext uses GPT-4o-mini to distill code changes into architectural decisions. Create a <code class="ic">.env</code> file in your project root:</p>
        <div class="code-blk">
          # .env<br>
          OPENAI_API_KEY=sk-proj-your-key-here<br>
          ORCHESTRATOR_URL=http://localhost:8000
          <button class="ci" onclick="copyText('OPENAI_API_KEY=sk-proj-your-key-here',this)">📋</button>
        </div>
      </div>
    </div>

    <div class="install-step">
      <div class="is-num">Step 3</div>
      <div class="is-body">
        <h3>Initialize in your repository</h3>
        <p>Run <code class="ic">tracecontext init</code> inside your project. This installs a post-commit hook that automatically captures every commit.</p>
        <div class="code-blk">
          $ cd your-project/<br>
          $ tracecontext init<br>
          <span style="color:#4ade80">✓ Post-commit hook installed</span><br>
          <span style="color:#4ade80">✓ .env loaded</span>
          <button class="ci" onclick="copyText('tracecontext init',this)">📋</button>
        </div>
      </div>
    </div>

    <div class="install-step">
      <div class="is-num">Step 4</div>
      <div class="is-body">
        <h3>Start the orchestrator</h3>
        <p>The orchestrator is the core engine. It receives events, runs the AI distillation pipeline, and stores your intent history.</p>
        <div class="code-blk">
          $ tracecontext serve<br>
          <span style="color:#4ade80">✓ TraceContext Orchestrator Online</span><br>
          <span style="color:#64748b"># Running at http://localhost:8000</span>
          <button class="ci" onclick="copyText('tracecontext serve',this)">📋</button>
        </div>
        <p style="font-size:.8rem;color:var(--muted2);margin-top:.5rem">Tip: add this to your startup scripts or run it as a background service.</p>
      </div>
    </div>

    <div class="install-step">
      <div class="is-num">Step 5</div>
      <div class="is-body">
        <h3>Connect your AI tool</h3>
        <p>Add the TraceContext MCP server to your AI tool's config. The exact file location depends on which tool you use — examples for the most popular:</p>
        <div class="tool-tabs">
          <div class="tool-tab-content code-blk" style="font-size:.73rem">
            <span style="color:var(--muted2)"># Cursor: ~/.cursor/mcp.json</span><br>
            <span style="color:var(--muted2)"># Windsurf: ~/.windsurf/mcp_settings.json</span><br>
            <span style="color:var(--muted2)"># Any MCP tool: see tool docs for config location</span><br>
            <br>
{<br>
&nbsp;&nbsp;<span style="color:#a78bfa">"mcpServers"</span>: {<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"tracecontext"</span>: {<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"command"</span>: <span style="color:#86efac">"tracecontext"</span>,<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"args"</span>: [<span style="color:#86efac">"mcp"</span>],<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#a78bfa">"env"</span>: { <span style="color:#a78bfa">"ORCHESTRATOR_URL"</span>: <span style="color:#86efac">"http://localhost:8000"</span> }<br>
&nbsp;&nbsp;&nbsp;&nbsp;}<br>
&nbsp;&nbsp;}<br>
}
            <button class="ci" onclick="copyMcp(event)">📋</button>
          </div>
        </div>
        <p style="font-size:.8rem;color:var(--muted2);margin-top:.5rem">Reload your AI tool after saving the config.</p>
      </div>
    </div>

    <div class="install-step">
      <div class="is-num">Step 6</div>
      <div class="is-body">
        <h3>Verify &amp; start building</h3>
        <p>Check that everything is connected and working:</p>
        <div class="code-blk">
          $ tracecontext status<br>
          <span style="color:#4ade80">✓ Orchestrator: Online (http://localhost:8000)</span><br>
          <span style="color:#4ade80">✓ MCP Server: Ready</span><br>
          <span style="color:#4ade80">✓ OpenAI: Connected (gpt-4o-mini)</span>
          <button class="ci" onclick="copyText('tracecontext status',this)">📋</button>
        </div>
        <div style="margin-top:1rem;padding:1rem;background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.2);border-radius:9px">
          <p style="font-size:.85rem;color:#4ade80;font-weight:600;margin-bottom:.35rem">You're ready.</p>
          <p style="font-size:.82rem;color:var(--muted2);line-height:1.7">
            Make a commit. Your intent history captures it automatically.<br>
            Ask your AI tool about your architecture — it already knows.
          </p>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- ── Footer ────────────────────────────────────────────────────────────────── -->
<footer>
  <p>
    <strong style="color:var(--text)">TraceContext</strong> &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; © 2025 Sanika Deshmukh Tungare &nbsp;·&nbsp;
    <a href="https://github.com/tracecontext-ai/tracecontext">github.com/tracecontext-ai/tracecontext</a>
  </p>
  <p>Built with FastAPI · LangGraph · GPT-4o-mini · MCP 1.26</p>
</footer>

<!-- ── JavaScript ────────────────────────────────────────────────────────────── -->
<script>
// ── Status polling ────────────────────────────────────────────────────────────
async function checkStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    const online = d.orchestrator === 'online';
    document.getElementById('orch-dot').className = 'dot ' + (online ? 'online' : 'offline');
    document.getElementById('orch-label').textContent = online ? 'Orchestrator Online' : 'Orchestrator Offline';
  } catch {
    document.getElementById('orch-dot').className = 'dot offline';
    document.getElementById('orch-label').textContent = 'Offline';
  }
}
checkStatus();
setInterval(checkStatus, 5000);

// ── Demo scenarios ────────────────────────────────────────────────────────────
const SCENARIOS = {
  payment: {
    label: 'Payment Service Migration',
    commits: [
      {
        message: "feat: add PaymentService using Braintree gateway",
        diff: "+from braintree import BraintreeGateway, Configuration, Environment\\n+gateway = BraintreeGateway(Configuration(\\n+    merchant_id=os.getenv('BT_MERCHANT'),\\n+    public_key=os.getenv('BT_PUBLIC'),\\n+))\\n+def charge(amount, nonce):\\n+    return gateway.transaction.sale({'amount': str(amount), 'payment_method_nonce': nonce})"
      },
      {
        message: "feat: add Money value object - integer cents, never float arithmetic",
        diff: "+class Money:\\n+    def __init__(self, cents: int, currency: str = 'USD'):\\n+        if not isinstance(cents, int):\\n+            raise TypeError('cents must be int - float causes rounding errors')\\n+        self.cents = cents\\n+    def to_stripe_amount(self) -> int:\\n+        return self.cents"
      },
      {
        message: "refactor: replace Braintree with Stripe PaymentIntents - global coverage and lower fees",
        diff: "-from braintree import BraintreeGateway\\n+import stripe\\n+stripe.api_key = os.getenv('STRIPE_SECRET_KEY')\\n+def charge(amount: Money, payment_method_id: str) -> dict:\\n+    return stripe.PaymentIntent.create(\\n+        amount=amount.to_stripe_amount(),\\n+        idempotency_key=f'charge_{payment_method_id}_{amount.cents}'\\n+    )"
      }
    ],
    deadEnds: [
      {
        approach: "Braintree payment gateway",
        reason: "Supports only 46 countries. SDK maintenance abandoned by PayPal. Higher fees than Stripe. Poor webhook reliability.",
        alternative: "Stripe PaymentIntents API with mandatory idempotency keys on all mutations"
      },
      {
        approach: "float for monetary values",
        reason: "IEEE 754 floating-point causes silent rounding errors. 0.1 + 0.2 = 0.30000000000000004. Found lost $0.01 per transaction in load test edge cases.",
        alternative: "Money value object with integer cents. Store as int, display as formatted string."
      }
    ],
    searchQueries: ["Braintree", "Money cents", "Stripe"]
  },
  auth: {
    label: 'Auth System Redesign',
    commits: [
      {
        message: "feat: implement JWT authentication with HS256 signing",
        diff: "+import jwt\\n+SECRET = os.getenv('JWT_SECRET')\\n+def create_token(user_id: str) -> str:\\n+    return jwt.encode({'sub': user_id, 'exp': datetime.utcnow() + timedelta(hours=1)}, SECRET, algorithm='HS256')"
      },
      {
        message: "feat: add refresh token rotation - blacklist old tokens on rotation",
        diff: "+def rotate_refresh_token(old_token: str) -> tuple[str, str]:\\n+    payload = verify_token(old_token)\\n+    revoke_token(old_token)\\n+    return create_access_token(payload['sub']), create_refresh_token(payload['sub'])"
      },
      {
        message: "refactor: migrate to Auth0 for managed authentication - reduce maintenance burden",
        diff: "-import jwt\\n+from authlib.integrations.flask_client import OAuth\\n+oauth = OAuth(app)\\n+auth0 = oauth.register('auth0',\\n+    client_id=os.getenv('AUTH0_CLIENT_ID'),\\n+    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),\\n+)"
      }
    ],
    deadEnds: [
      {
        approach: "custom JWT with in-memory token blacklist",
        reason: "Blacklist does not persist across pod restarts. Tokens cannot be revoked in multi-pod Kubernetes deployment without Redis. Memory bloat on long-lived services.",
        alternative: "Auth0 managed authentication with built-in token revocation, MFA, and social login"
      },
      {
        approach: "PostgreSQL session table for server-side sessions",
        reason: "Session table becomes bottleneck at 10k+ concurrent users. Every request hits database for session lookup. p99 latency spiked to 800ms under load.",
        alternative: "Stateless JWT with 15-minute expiry plus Auth0 refresh token rotation"
      }
    ],
    searchQueries: ["JWT", "session", "Auth0"]
  }
};

// ── Terminal helpers ──────────────────────────────────────────────────────────
function log(text, cls = '') {
  const t = document.getElementById('terminal');
  const p = document.createElement('p');
  if (cls) p.className = cls;
  p.textContent = text;
  t.appendChild(p);
  t.scrollTop = t.scrollHeight;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Context panel helpers ─────────────────────────────────────────────────────
let recCount = 0;

function addRecord(text) {
  const panel = document.getElementById('ctx-panel');
  const ph = panel.querySelector('p');
  if (ph) ph.remove();

  const isAdr  = text.includes('[ADR]');
  const isDead = text.includes('[DEAD_END]');

  const div   = document.createElement('div');
  div.className = 'ctx-rec ' + (isAdr ? 'adr' : 'dead');

  const badge = document.createElement('div');
  badge.className = 'ctx-badge ' + (isAdr ? 'b-adr' : 'b-dead');
  badge.textContent = isAdr ? 'ADR' : 'DEAD-END';

  const titleDiv = document.createElement('div');
  titleDiv.className = 'ctx-title';

  const descDiv = document.createElement('div');
  descDiv.className = 'ctx-desc';

  // Parse key fields from the record text
  const clean = text.replace('[ADR] ', '').replace('[DEAD_END] ', '');
  const lines  = clean.split('\\n').map(l => l.trim()).filter(Boolean);
  let title = '', desc = [];
  for (const ln of lines) {
    if (/^Title:/i.test(ln))    { title = ln.replace(/^Title:\\s*/i, ''); }
    else if (/^Approach:/i.test(ln)) { title = ln.replace(/^Approach:\\s*/i, ''); }
    else if (/^Decision:/i.test(ln)) { desc.push(ln.replace(/^Decision:\\s*/i, '')); }
    else if (/^Reason:/i.test(ln))   { desc.push(ln.replace(/^Reason:\\s*/i, '')); }
  }
  if (!title) title = lines[0] || 'Record';

  titleDiv.textContent = title;
  descDiv.textContent  = desc.slice(0,2).join(' · ').substring(0, 120) + (desc.join('').length > 120 ? '…' : '');

  div.appendChild(badge);
  div.appendChild(titleDiv);
  div.appendChild(descDiv);
  panel.appendChild(div);

  recCount++;
  document.getElementById('rec-count').textContent = recCount + ' record' + (recCount !== 1 ? 's' : '');
  panel.scrollTop = panel.scrollHeight;
}

// ── Main demo runner ──────────────────────────────────────────────────────────
async function runDemo() {
  const btn = document.getElementById('run-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>&nbsp; Running…';

  // Clear everything and reset context store
  document.getElementById('terminal').innerHTML = '';
  document.getElementById('ctx-panel').innerHTML = '';
  recCount = 0;
  document.getElementById('rec-count').textContent = '0 records';

  const key      = document.getElementById('sc-select').value;
  const scenario = SCENARIOS[key];

  log('$ TraceContext Demo — ' + scenario.label, 'lc');
  log('$ Connecting to orchestrator…', 'lc');
  await sleep(400);

  // Status check
  try {
    const s = await fetch('/api/status');
    const sd = await s.json();
    if (sd.orchestrator !== 'online') {
      log('✗ Orchestrator offline — run: tracecontext serve', 'le');
      btn.disabled = false; btn.innerHTML = '▶ Run Demo'; return;
    }
    log('✓ Orchestrator online', 'lo');
  } catch {
    log('✗ Cannot reach orchestrator', 'le');
    btn.disabled = false; btn.innerHTML = '▶ Run Demo'; return;
  }

  // Reset context store for a clean run
  try { await fetch('/api/reset', {method:'POST'}); } catch {}
  await sleep(300);

  // ── Send commits ──────────────────────────────────────────────────────────
  log('', 'lm');
  log('─── Sending git commit events ───────────────────────────', 'lm');
  for (const commit of scenario.commits) {
    await sleep(300);
    log('$ git commit -m "' + commit.message.substring(0,52) + '…"', 'lc');
    log('  → POST /events  type: git_commit', 'li');
    try {
      const r  = await fetch('/api/events', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({type:'git_commit', data:{message:commit.message,diff:commit.diff}, metadata:{repo:'demo-repo',user:'developer'}})
      });
      const d = await r.json();
      log('  [' + (d.status||'received') + '] GPT-4o-mini generating ADR…', 'lo');
    } catch(e) { log('  [error] ' + e.message, 'le'); }
    await sleep(800);
  }

  // ── Send dead-ends ────────────────────────────────────────────────────────
  await sleep(300);
  log('', 'lm');
  log('─── Recording dead-ends ─────────────────────────────────', 'lm');
  for (const de of scenario.deadEnds) {
    await sleep(300);
    log('$ tracecontext dead-end: "' + de.approach.substring(0,42) + '…"', 'lc');
    try {
      const r  = await fetch('/api/events', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({type:'revert_detected', data:{approach:de.approach,reason:de.reason,alternative:de.alternative}, metadata:{repo:'demo-repo',user:'developer'}})
      });
      const d = await r.json();
      log('  [' + (d.status||'received') + '] Dead-end captured', 'ld');
    } catch(e) { log('  [error] ' + e.message, 'le'); }
    await sleep(600);
  }

  // ── Fetch context ─────────────────────────────────────────────────────────
  await sleep(500);
  log('', 'lm');
  log('─── Fetching AI-generated context ───────────────────────', 'lm');
  log('$ GET /context', 'lc');
  try {
    const r       = await fetch('/api/context');
    const d       = await r.json();
    const records = d.context || [];
    log('  ' + records.length + ' records generated by GPT-4o-mini', 'lo');
    await sleep(300);
    for (const rec of records) {
      addRecord(rec);
      const preview = rec.replace('[ADR] ','').replace('[DEAD_END] ','').split('\\n')[0].substring(0,60);
      log('  + ' + preview + '…', rec.includes('[ADR]') ? 'la' : 'ld');
      await sleep(80);
    }
  } catch(e) { log('  [error] ' + e.message, 'le'); }

  // ── MCP search simulation ─────────────────────────────────────────────────
  await sleep(500);
  log('', 'lm');
  log('─── Simulating AI tool MCP search calls ─────────────────', 'lm');
  for (const q of scenario.searchQueries) {
    await sleep(350);
    log('$ search_context("' + q + '")', 'ls');
    try {
      const r = await fetch('/api/context?query=' + encodeURIComponent(q));
      const d = await r.json();
      const n = (d.context||[]).length;
      log('  → ' + n + ' result' + (n!==1?'s':'') + ' returned to your AI tool', 'lo');
    } catch { log('  → error', 'le'); }
  }

  await sleep(400);
  log('', 'lm');
  log('✓ Demo complete — your AI tools now know your intent history!', 'lx');

  btn.disabled = false;
  btn.innerHTML = '▶ Run Demo';
}

function clearAll() {
  document.getElementById('terminal').innerHTML =
    '<p class="li"># Select a scenario above and click Run Demo</p>' +
    '<p class="li"># Git commits and dead-ends will stream here</p>' +
    '<p class="li"># GPT-4o-mini generates ADRs in real time</p>';
  document.getElementById('ctx-panel').innerHTML =
    '<p style="color:var(--muted);font-size:.82rem;text-align:center;margin-top:4rem;line-height:1.8">Run the demo to see<br>AI-generated ADRs and dead-end<br>records appear here</p>';
  recCount = 0;
  document.getElementById('rec-count').textContent = '0 records';
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function scrollTo(sel) {
  document.querySelector(sel).scrollIntoView({behavior:'smooth'});
}

function copyText(text, el) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = el.textContent;
    el.textContent = '✓';
    setTimeout(() => el.textContent = orig, 1500);
  });
}

function copyMcp(e) {
  const cfg = JSON.stringify({
    mcpServers: {
      tracecontext: {
        command: "tracecontext",
        args: ["mcp"],
        env: { ORCHESTRATOR_URL: "http://localhost:8000" }
      }
    }
  }, null, 2);
  navigator.clipboard.writeText(cfg).then(() => {
    const btn = e.target;
    const orig = btn.textContent;
    btn.textContent = '✓';
    setTimeout(() => btn.textContent = orig, 1500);
  });
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


# ── Startup ────────────────────────────────────────────────────────────────────

_proc = None


def _start_orchestrator():
    global _proc
    if _orch_ok():
        print("  ✓ Orchestrator already running at", ORCH)
        return
    print("  Starting orchestrator on port 8000…")
    _proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "tracecontext.orchestrator.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for i in range(25):
        time.sleep(1)
        if _orch_ok():
            print(f"  ✓ Orchestrator ready (PID {_proc.pid}, took {i+1}s)")
            return
    print("  ⚠  Orchestrator slow to start — demo may show connection errors")


if __name__ == "__main__":
    print()
    print("  ╔═══════════════════════════════════════╗")
    print("  ║   TraceContext  —  Developer Demo UI  ║")
    print("  ╚═══════════════════════════════════════╝")
    print()
    _start_orchestrator()
    print(f"  ✓ Demo UI starting at http://localhost:{PORT}")
    print()
    threading.Thread(
        target=lambda: [time.sleep(3), webbrowser.open(f"http://localhost:{PORT}")],
        daemon=True,
    ).start()
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
    finally:
        if _proc:
            _proc.terminate()
