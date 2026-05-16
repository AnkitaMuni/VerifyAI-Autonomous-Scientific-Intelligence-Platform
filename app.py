import streamlit as st
import os
import tempfile
import time
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import init_db, log_assessment, get_history
from agent import run_verification

st.set_page_config(page_title="VerifyAI | Scientific Intelligence", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")

# Premium, futuristic styling (glassmorphism)
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --primary: #58a6ff;
    --secondary: #bc8cff;
    --success: #7ee787;
    --warning: #d29922;
    --danger: #f85149;
    --bg-dark: #0d1117;
    --glass-bg: rgba(22, 27, 34, 0.6);
    --glass-border: rgba(255, 255, 255, 0.1);
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace;
}

.stApp {
    background: radial-gradient(circle at 20% 20%, #161b22 0%, #0d1117 100%);
    color: #e6edf3;
}

/* Glassmorphism Evolution */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4), inset 0 0 20px rgba(255,255,255,0.02);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
    transition: 0.5s;
}
.glass-card:hover::before { left: 100%; }
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(88, 166, 255, 0.4);
    box-shadow: 0 20px 50px 0 rgba(0, 150, 255, 0.15);
}

/* Agentic Pipeline Refinement */
.agent-pipeline {
    display: flex; align-items: center; justify-content: center;
    gap: 0; margin: 40px 0; padding: 10px;
}
.agent-node {
    display: flex; flex-direction: column; align-items: center; gap: 12px;
    position: relative; z-index: 5; transition: all 0.3s ease;
}
.agent-icon {
    width: 64px; height: 64px; border-radius: 18px;
    background: #161b22; border: 2px solid #30363d;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.agent-icon.active {
    background: rgba(88, 166, 255, 0.15); border-color: var(--primary);
    transform: scale(1.1) rotate(5deg);
    box-shadow: 0 0 30px rgba(88, 166, 255, 0.4);
    animation: agentPulse 2s infinite linear;
}
.agent-icon.done {
    background: rgba(46, 160, 67, 0.1); border-color: var(--success); color: var(--success);
}
.agent-label {
    font-size: 0.75em; font-weight: 700; color: #8b949e; text-align: center;
    letter-spacing: 0.1em; text-transform: uppercase; line-height: 1.4;
}
.agent-label.active { color: var(--primary); text-shadow: 0 0 10px rgba(88,166,255,0.5); }
.agent-label.done { color: var(--success); }

.agent-connector {
    flex: 1; height: 3px; min-width: 40px; max-width: 80px;
    background: #30363d; margin: 0 -10px; margin-top: -30px;
    position: relative; overflow: hidden;
}
.agent-connector.active {
    background: linear-gradient(90deg, var(--success), var(--primary));
}
.agent-connector.active::after {
    content: ''; position: absolute; top:0; left:-100%; width:100%; height:100%;
    background: linear-gradient(90deg, transparent, #fff, transparent);
    animation: flowLight 1.5s infinite linear;
}
.agent-connector.done { background: var(--success); }

@keyframes agentPulse {
    0% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.7); }
    70% { box-shadow: 0 0 0 15px rgba(88, 166, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
}
@keyframes flowLight {
    0% { left: -100%; } 100% { left: 100%; }
}

/* Orchestration Flow Container */
.orch-flow-container {
    background: rgba(13, 17, 23, 0.7); border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 16px; padding: 24px; margin-top: 20px;
}
.orch-step {
    display: flex; gap: 16px; align-items: flex-start;
    padding: 14px; border-radius: 12px; margin-bottom: 12px;
    background: rgba(255,255,255,0.02); border: 1px solid transparent;
    transition: 0.2s;
}
.orch-step:hover { background: rgba(88, 166, 255, 0.05); border-color: rgba(88, 166, 255, 0.2); }
.orch-step-icon {
    width: 36px; height: 36px; border-radius: 10px; background: rgba(88, 166, 255, 0.1);
    display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.orch-step-content { flex: 1; }
.orch-step-title { font-size: 0.9em; font-weight: 700; color: #fff; margin-bottom: 4px; }
.orch-step-desc { font-size: 0.8em; color: #8b949e; line-height: 1.5; }

/* Score Cards */
.score-stat-card {
    text-align: center; padding: 25px 20px; border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    position: relative; overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: 0.3s;
}
.score-stat-card:hover { transform: translateY(-3px); border-color: var(--primary); }
.score-stat-card::after {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.05), transparent);
    transform: rotate(45deg); transition: 0.5s; pointer-events: none;
}
.score-stat-card:hover::after { left: 100%; top: 100%; }

.score-val { 
    font-size: 2.8rem; font-weight: 800; color: #fff; 
    text-shadow: 0 0 20px rgba(88, 166, 255, 0.4);
}
.score-label { font-size: 0.75em; color: #8b949e; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 8px; font-weight: 600; }

/* Architecture Cards */
.arch-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 18px; text-align: left; height: 100%;
    transition: 0.3s; position: relative; overflow: hidden;
}
.arch-card:hover { border-color: var(--secondary); background: rgba(188,140,255,0.05); transform: translateY(-2px); }
.arch-card::after {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.03), transparent);
    transform: rotate(45deg); transition: 0.6s; pointer-events: none;
}
.arch-card:hover::after { left: 100%; top: 100%; }
.arch-label { font-size: 0.65em; color: var(--secondary); font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.arch-val { font-size: 0.95em; color: #fff; font-weight: 600; line-height: 1.4; }

/* Reviewer Cards Evolution */
.reviewer-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 20px; transition: 0.3s;
}
.reviewer-card:hover { background: rgba(255,255,255,0.04); border-color: rgba(88,166,255,0.3); }

/* Typography Hierarchy */
h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 800; letter-spacing: -0.02em; }
.gradient-text {
    background: linear-gradient(135deg, #fff 0%, var(--primary) 50%, var(--secondary) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Micro-interactions */
.stButton>button {
    border-radius: 12px; font-weight: 700; letter-spacing: 0.05em;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border: none; color: #fff; transition: 0.3s;
}
.stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 25px rgba(88, 166, 255, 0.3); }

.signal-bar-bg { background: rgba(255,255,255,0.05); border-radius: 10px; height: 10px; overflow: hidden; }
.signal-bar-fill { height: 100%; border-radius: 10px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }

.orch-terminal {
    background: #010409; border: 1px solid #30363d; border-radius: 12px;
    padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em;
    color: var(--success); line-height: 1.6; max-height: 300px; overflow-y: auto;
}

/* Repository Intelligence Components */
.community-stat-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px; margin-bottom: 24px;
}
.community-stat-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 16px; text-align: center;
    transition: 0.3s; position: relative; overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.community-stat-card:hover { 
    border-color: var(--primary); transform: translateY(-2px); 
    background: rgba(88,166,255,0.05);
    box-shadow: 0 8px 25px rgba(88, 166, 255, 0.15);
}
.stat-val { font-size: 1.5rem; font-weight: 800; color: #fff; margin-bottom: 4px; text-shadow: 0 0 10px rgba(255,255,255,0.2); }
.stat-label { font-size: 0.65em; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }

.evidence-item-ok {
    background: rgba(46, 160, 67, 0.08); border: 1px solid rgba(46, 160, 67, 0.2);
    color: #7ee787; font-size: 0.85em; margin-bottom: 8px; font-weight: 600;
}
.evidence-item-warn {
    background: rgba(210, 153, 34, 0.08); border: 1px solid rgba(210, 153, 34, 0.2);
    color: #d29922; font-size: 0.85em; margin-bottom: 8px; font-weight: 600;
}

.repo-status-badge {
    padding: 6px 14px; border-radius: 20px; font-size: 0.75em; font-weight: 800;
    text-transform: uppercase; letter-spacing: 1px; display: inline-block; margin: 10px 0;
}

.signal-card {
    background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px; padding: 20px; height: 100%;
}
.booster-item {
    color: #7ee787; font-size: 0.82em; padding: 4px 0; border-left: 2px solid rgba(46, 160, 67, 0.3); padding-left: 10px; margin: 6px 0;
}
.reducer-item {
    color: #d29922; font-size: 0.82em; padding: 4px 0; border-left: 2px solid rgba(210, 153, 34, 0.3); padding-left: 10px; margin: 6px 0;
}

.verification-item-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 18px; margin-bottom: 16px;
    transition: 0.2s;
}
.verification-item-card:hover { border-color: rgba(88,166,255,0.2); background: rgba(255,255,255,0.04); }

.explanation-text {
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    color: #c9d1d9 !important;
    text-align: justify !important;
    margin-bottom: 12px;
}

.trace-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: #8b949e;
    text-align: justify;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""<style>
:root {
    --os-bg: #050712;
    --os-panel: rgba(11, 18, 32, 0.74);
    --os-panel-2: rgba(17, 25, 42, 0.64);
    --os-line: rgba(176, 208, 255, 0.13);
    --os-text: #edf6ff;
    --os-muted: #94a3b8;
    --os-blue: #6bb8ff;
    --os-violet: #c59cff;
    --os-cyan: #7dd3fc;
    --os-green: #7ee787;
    --os-amber: #f5c451;
    --os-red: #ff6b6b;
    --os-shadow: 0 28px 90px rgba(0, 0, 0, 0.52);
}

.stApp {
    color: var(--os-text);
    background:
        radial-gradient(circle at 8% -8%, rgba(99, 102, 241, 0.20), transparent 34%),
        radial-gradient(circle at 84% 6%, rgba(14, 165, 233, 0.16), transparent 34%),
        radial-gradient(circle at 72% 92%, rgba(197, 156, 255, 0.12), transparent 36%),
        linear-gradient(135deg, #050712 0%, #08111f 44%, #05070d 100%);
    isolation: isolate;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -2;
    background-image:
        linear-gradient(rgba(125, 211, 252, 0.052) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125, 211, 252, 0.038) 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(circle at 50% 18%, black, transparent 76%);
}

.stApp::after {
    content: "";
    position: fixed;
    inset: -18%;
    pointer-events: none;
    z-index: -1;
    opacity: 0.22;
    background:
        radial-gradient(circle, rgba(107, 184, 255, 0.18) 0 2px, transparent 3px),
        radial-gradient(circle, rgba(197, 156, 255, 0.13) 0 1px, transparent 2px);
    background-size: 180px 180px, 260px 260px;
    animation: osParticleDrift 34s linear infinite;
}

@keyframes osParticleDrift {
    from { transform: translate3d(0, 0, 0); }
    to { transform: translate3d(-80px, -120px, 0); }
}

.block-container {
    max-width: 1480px;
    padding-top: 2.9rem;
    padding-bottom: 5rem;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 20% 0%, rgba(107, 184, 255, 0.14), transparent 45%),
        linear-gradient(180deg, rgba(10, 16, 28, 0.96), rgba(5, 8, 16, 0.98));
    border-right: 1px solid var(--os-line);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    opacity: 0.25;
}

.hero-shell {
    position: relative;
    margin: 8px auto 34px;
    padding: 44px 24px 34px;
    text-align: center;
    overflow: hidden;
}

.hero-shell::before {
    content: "";
    position: absolute;
    inset: 0 10%;
    z-index: -1;
    filter: blur(10px);
    background:
        radial-gradient(ellipse at top, rgba(107, 184, 255, 0.24), transparent 60%),
        radial-gradient(ellipse at 70% 20%, rgba(197, 156, 255, 0.18), transparent 48%);
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    border: 1px solid rgba(107, 184, 255, 0.22);
    border-radius: 999px;
    background: rgba(8, 13, 24, 0.58);
    color: var(--os-cyan);
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 900;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 16px 50px rgba(0,0,0,0.24);
}

.hero-kicker::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: var(--os-green);
    box-shadow: 0 0 18px var(--os-green);
    animation: osStatusBlink 1.7s ease-in-out infinite;
}

.hero-title {
    margin: 12px 0 4px;
    font-size: clamp(4.4rem, 8vw, 8.8rem);
    line-height: 0.92;
    font-weight: 900;
    letter-spacing: 0;
    background: linear-gradient(180deg, #ffffff 0%, #dbeafe 28%, #7dd3fc 62%, #c59cff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 32px rgba(107,184,255,0.32));
}

.hero-subtitle {
    margin: 0 auto;
    max-width: 880px;
    color: var(--os-muted);
    font-size: clamp(1rem, 2vw, 1.32rem);
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.hero-meta-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(160px, 1fr));
    gap: 12px;
    max-width: 860px;
    margin: 28px auto 0;
}

.hero-meta {
    border: 1px solid rgba(176, 208, 255, 0.12);
    border-radius: 18px;
    padding: 13px 16px;
    background: rgba(8, 13, 24, 0.48);
    color: #c8d7ea;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}

.glass-card {
    background:
        linear-gradient(135deg, rgba(18, 27, 45, 0.78), rgba(9, 13, 22, 0.68)) !important;
    border: 1px solid var(--os-line) !important;
    border-radius: 24px !important;
    box-shadow: var(--os-shadow), inset 0 1px 0 rgba(255,255,255,0.055) !important;
    backdrop-filter: blur(18px) saturate(1.22);
    -webkit-backdrop-filter: blur(18px) saturate(1.22);
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.35s ease, box-shadow 0.35s ease;
}

.glass-card:hover {
    transform: translateY(-3px);
    border-color: rgba(107, 184, 255, 0.32) !important;
    box-shadow: var(--os-shadow), 0 18px 60px rgba(47, 129, 247, 0.16), inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

h1, h2, h3 {
    letter-spacing: 0 !important;
}

.stTextInput input, [data-baseweb="select"] > div, [data-testid="stFileUploaderDropzone"] {
    background: rgba(5, 10, 20, 0.66) !important;
    border: 1px solid rgba(176, 208, 255, 0.14) !important;
    border-radius: 16px !important;
    color: var(--os-text) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 34px rgba(0,0,0,0.22);
}

[data-testid="stFileUploaderDropzone"] {
    padding: 26px !important;
}

.stButton>button {
    min-height: 3.1rem;
    border-radius: 16px;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #04111f;
    background: linear-gradient(135deg, rgba(107,184,255,0.98), rgba(197,156,255,0.95));
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow: 0 16px 42px rgba(47, 129, 247, 0.30), inset 0 1px 0 rgba(255,255,255,0.42);
}

.stButton>button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 22px 60px rgba(47, 129, 247, 0.38), 0 0 0 1px rgba(255,255,255,0.16);
}

.agent-icon {
    width: 70px;
    height: 70px;
    border-radius: 22px;
    background: linear-gradient(145deg, rgba(20, 31, 51, 0.96), rgba(7, 11, 20, 0.92));
    border: 1px solid rgba(176, 208, 255, 0.14);
    box-shadow: 0 16px 38px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.05);
}

.agent-icon.active {
    background:
        radial-gradient(circle at 28% 22%, rgba(255,255,255,0.20), transparent 26%),
        linear-gradient(145deg, rgba(47,129,247,0.36), rgba(197,156,255,0.22));
    border-color: rgba(107, 184, 255, 0.84);
    transform: scale(1.08);
    box-shadow: 0 0 0 1px rgba(107,184,255,0.28), 0 0 38px rgba(107,184,255,0.42), 0 20px 50px rgba(47,129,247,0.28);
    animation: osAgentPulse 1.9s infinite ease-out, osAliveFloat 4s ease-in-out infinite;
}

.agent-icon.done {
    background: linear-gradient(145deg, rgba(46, 160, 67, 0.18), rgba(9, 17, 23, 0.90));
    border-color: rgba(126, 231, 135, 0.58);
}

.agent-status-text {
    font-size: 0.66rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.agent-connector {
    height: 4px;
    border-radius: 999px;
    background: rgba(176, 208, 255, 0.12);
}

.agent-connector.active {
    background: linear-gradient(90deg, rgba(126,231,135,0.42), rgba(107,184,255,0.95));
    box-shadow: 0 0 20px rgba(107,184,255,0.36);
}

.agent-connector.done {
    background: linear-gradient(90deg, rgba(126,231,135,0.72), rgba(107,184,255,0.46));
}

@keyframes osAgentPulse {
    0% { box-shadow: 0 0 0 0 rgba(107,184,255,0.55), 0 0 38px rgba(107,184,255,0.36); }
    72% { box-shadow: 0 0 0 18px rgba(107,184,255,0), 0 0 38px rgba(107,184,255,0.36); }
    100% { box-shadow: 0 0 0 0 rgba(107,184,255,0), 0 0 38px rgba(107,184,255,0.36); }
}

@keyframes osAliveFloat {
    0%, 100% { translate: 0 0; }
    50% { translate: 0 -4px; }
}

.orchestration-shell {
    padding: 24px !important;
}

.orch-dot {
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: var(--os-green);
    box-shadow: 0 0 22px var(--os-green);
    animation: osStatusBlink 1.6s ease-in-out infinite;
}

@keyframes osStatusBlink {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.48; transform: scale(0.72); }
}

.orch-flow-container {
    background:
        radial-gradient(circle at 10% 0%, rgba(107,184,255,0.12), transparent 38%),
        rgba(5, 10, 20, 0.62);
    border: 1px solid rgba(107,184,255,0.18);
    border-radius: 22px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 18px 50px rgba(0,0,0,0.22);
}

.orch-step {
    border-radius: 18px;
    border: 1px solid rgba(176,208,255,0.10);
    background: linear-gradient(135deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015));
    transition: transform 0.25s ease, background 0.25s ease, border-color 0.25s ease;
}

.orch-step:hover {
    transform: translateX(3px);
    border-color: rgba(107,184,255,0.24);
}

.mcp-flow-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(145px, 1fr));
    gap: 12px;
    margin: 18px 0 18px;
}

.mcp-flow-card {
    min-height: 122px;
    padding: 14px;
    border-radius: 18px;
    background: linear-gradient(160deg, rgba(12, 21, 36, 0.78), rgba(4, 8, 16, 0.72));
    border: 1px solid rgba(176, 208, 255, 0.11);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.045);
    position: relative;
    overflow: hidden;
}

.mcp-flow-card::after {
    content: "";
    position: absolute;
    inset: auto 14px 12px 14px;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(107,184,255,0.75), transparent);
    opacity: 0.34;
}

.mcp-flow-card.active {
    border-color: rgba(107,184,255,0.46);
    box-shadow: 0 0 34px rgba(107,184,255,0.16), inset 0 1px 0 rgba(255,255,255,0.08);
}

.mcp-flow-card.done {
    border-color: rgba(126,231,135,0.30);
}

.mcp-flow-label {
    color: var(--os-cyan);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-weight: 900;
}

.mcp-flow-name {
    color: #fff;
    font-size: 0.88rem;
    font-weight: 850;
    margin-top: 8px;
    line-height: 1.25;
}

.mcp-flow-meta {
    color: var(--os-muted);
    font-size: 0.74rem;
    line-height: 1.42;
    margin-top: 8px;
}

.orch-terminal {
    background: linear-gradient(180deg, rgba(1, 4, 9, 0.94), rgba(2, 8, 17, 0.90));
    border: 1px solid rgba(176,208,255,0.12);
    border-radius: 18px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 16px 44px rgba(0,0,0,0.25);
}

.score-stat-card {
    border-radius: 22px;
    background:
        radial-gradient(circle at 50% 0%, rgba(107,184,255,0.12), transparent 54%),
        linear-gradient(135deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.012) 100%);
    border: 1px solid rgba(176,208,255,0.12);
    box-shadow: 0 14px 42px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.05);
}

.score-ring {
    width: 116px;
    height: 116px;
    margin: 0 auto 12px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background:
        radial-gradient(circle at center, rgba(8, 13, 24, 0.95) 0 57%, transparent 58%),
        conic-gradient(var(--ring-color, var(--os-blue)) calc(var(--score, 0) * 1%), rgba(176,208,255,0.10) 0);
    box-shadow: 0 0 36px rgba(107,184,255,0.22), inset 0 0 24px rgba(0,0,0,0.42);
    position: relative;
}

.score-ring::after {
    content: "";
    position: absolute;
    inset: 9px;
    border-radius: inherit;
    border: 1px solid rgba(255,255,255,0.07);
}

.score-val {
    font-size: 2.45rem;
    font-weight: 900;
    line-height: 1;
    animation: osMetricRise 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes osMetricRise {
    from { opacity: 0; transform: translateY(8px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.community-stat-card, .arch-card, .verification-item-card, .signal-card, .reviewer-card {
    border-radius: 18px !important;
    border-color: rgba(176,208,255,0.11) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 14px 38px rgba(0,0,0,0.16);
}

.verification-item-card:hover, .community-stat-card:hover, .arch-card:hover, .reviewer-card:hover {
    transform: translateY(-3px);
    border-color: rgba(107,184,255,0.28) !important;
}

.repo-tree {
    background: linear-gradient(180deg, rgba(1,4,9,0.94), rgba(4,10,20,0.92));
    border: 1px solid rgba(176,208,255,0.12);
    border-radius: 20px;
    padding: 18px;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 16px 42px rgba(0,0,0,0.22);
    max-height: 380px;
    overflow: auto;
}

.repo-root {
    color: var(--os-blue);
    font-weight: 900;
    margin-bottom: 8px;
}

.repo-tree-row {
    color: #c9d7ea;
    font-size: 0.78rem;
    line-height: 1.8;
    white-space: nowrap;
}

.tree-branch {
    color: rgba(107,184,255,0.40);
}

.artifact-chip {
    display: inline-flex;
    border-radius: 999px;
    padding: 3px 9px;
    margin-left: 7px;
    border: 1px solid rgba(107,184,255,0.18);
    background: rgba(107,184,255,0.08);
    color: var(--os-cyan);
    font-size: 0.62rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.ai-disclosure {
    margin: 12px 0;
    border-radius: 18px;
    border: 1px solid rgba(176,208,255,0.10);
    background: rgba(255,255,255,0.024);
    overflow: hidden;
}

.ai-disclosure summary {
    cursor: pointer;
    padding: 15px 18px;
    color: #fff;
    font-weight: 850;
    letter-spacing: 0.03em;
    list-style: none;
}

.ai-disclosure summary::-webkit-details-marker {
    display: none;
}

.ai-disclosure summary::after {
    content: "+";
    float: right;
    color: var(--os-blue);
    font-size: 1.2rem;
}

.ai-disclosure[open] summary::after {
    content: "-";
}

.ai-disclosure-body {
    padding: 0 18px 18px;
    color: var(--os-muted);
    animation: osDisclosureIn 0.28s ease both;
}

@keyframes osDisclosureIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(176,208,255,0.12) !important;
    border-radius: 18px !important;
    background: rgba(8, 13, 24, 0.52) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 14px 38px rgba(0,0,0,0.14);
    overflow: hidden;
}

div[data-testid="stExpander"] summary {
    color: #eaf4ff !important;
    font-weight: 850;
}

@media (max-width: 1100px) {
    .mcp-flow-grid, .hero-meta-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .agent-pipeline {
        overflow-x: auto;
        justify-content: flex-start;
    }
}

@media (max-width: 720px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero-title {
        font-size: 4.1rem;
    }
    .hero-meta-grid, .mcp-flow-grid {
        grid-template-columns: 1fr;
    }
    .glass-card {
        padding: 20px !important;
    }
}
</style>""", unsafe_allow_html=True)

st.markdown("""
<section class="hero-shell">
    <div class="hero-kicker">Scientific Intelligence OS</div>
    <h1 class="hero-title">VerifyAI</h1>
    <center><p class="hero-subtitle">Autonomous Scientific Intelligence Platform</p></center>
    <div class="hero-meta-grid">
        <div class="hero-meta">Multi-Agent Verification</div>
        <div class="hero-meta">Repository Intelligence</div>
        <div class="hero-meta">Evidence-Grounded Trust</div>
    </div>
</section>
""", unsafe_allow_html=True)

if not os.path.exists('assessments.db'): init_db()

with st.sidebar:
    st.header("⚙️ Platform Config")
    
    api_key = st.text_input("Gemini API Key", type="password")
    github_api_key = st.text_input("GitHub API Token", type="password", help="Use to avoid rate limits when scanning repositories.")
        
    model_name = st.selectbox("AI Brain", ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-2.5-pro"])
    st.markdown("---")
    st.markdown("**Powered by Gemini & MCP Intelligence**")

# Input Section
st.subheader("📥 Ingest Research Artifacts")
c1, c2 = st.columns(2)
with c1:
    uploaded_file = st.file_uploader("1. Upload Academic PDF", type="pdf")

if uploaded_file:
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get('current_file_id') != current_file_id:
        st.session_state['current_file_id'] = current_file_id
        try:
            import re
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            text = "".join(page.extract_text() + "\n" for page in reader.pages[:10])
            regex_repos = re.findall(r'https?://(?:www\.)?(?:github\.com|gitlab\.com)/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', text)
            st.session_state['extracted_repo'] = regex_repos[0] if regex_repos else ""
        except Exception:
            st.session_state['extracted_repo'] = ""
        uploaded_file.seek(0)

with c2:
    default_url = st.session_state.get('extracted_repo', "")
    repo_url = st.text_input("2. Target Repository URL (Auto-extracted)", value=default_url, placeholder="https://github.com/...")

if uploaded_file:
    if st.button("🚀 Initialize Multi-Agent Audit", use_container_width=True, type="primary"):
        st.session_state['running'] = True
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            st.session_state['tmp_path'] = tmp.name
        st.session_state['paper_name'] = uploaded_file.name
        st.session_state['repo_url'] = repo_url
        st.session_state['model_name'] = model_name
        st.session_state['api_key'] = api_key
        st.session_state['github_api_key'] = github_api_key
        if 'final_state' in st.session_state: del st.session_state['final_state']
st.markdown('</div>', unsafe_allow_html=True)

# Live Agent Execution
if st.session_state.get('running'):

    # Agent definitions — order matches pipeline
    AGENTS = [
        ("📄", "Paper\nAnalysis", "paper"),
        ("📂", "Repository\nIntelligence", "repo"),
        ("📊", "Plausibility\nVerification", "plaus"),
        ("👨‍⚖️", "Reviewer\nSimulation", "review"),
        ("🏁", "Scientific\nTrust", "trust"),
    ]

    # Mapping: log keywords → which agent index is active
    AGENT_KEYWORDS = {
        "paper": 0, "pdf": 0, "ingesting": 0, "extracting": 0, "parsing": 0,
        "repository": 1, "github": 1, "artifact": 1, "clone": 1, "tree": 1,
        "plausibility": 2, "benchmark": 2, "claim": 2, "scientific plausibility": 2,
        "reviewer": 3, "review board": 3, "peer": 3, "consensus": 3,
        "trust": 4, "credibility": 4, "auditor": 4, "final": 4,
    }

    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
        <div class='orch-dot'></div>
        <span style='font-size:0.78em;color:#8b949e;letter-spacing:0.1em;text-transform:uppercase;font-weight:600;'>
            Autonomous Multi-Agent Orchestration — Live Execution
        </span>
    </div>""", unsafe_allow_html=True)

    pipeline_ph  = st.empty()   # agent node pipeline
    terminal_ph  = st.empty()   # terminal log
    status_ph    = st.empty()   # current action line

    log_history   = []
    orch_state    = {"active": 0, "done": set()}

    def _render_pipeline(active_idx, done_set, log_lines):
        # Build pipeline HTML
        nodes_html = ""
        for i, (icon, label, _) in enumerate(AGENTS):
            if i in done_set:
                icon_cls, lbl_cls, status_txt, status_col = "done", "done", "✓ Done", "#7ee787"
            elif i == active_idx:
                icon_cls, lbl_cls, status_txt, status_col = "active", "active", "⚡ Running", "#58a6ff"
            else:
                icon_cls, lbl_cls, status_txt, status_col = "waiting", "", "· Queued", "#484f58"

            nodes_html += f"""
            <div class='agent-node'>
                <div class='agent-icon {icon_cls}'>{icon}</div>
                <div class='agent-label {lbl_cls}'>{label.replace(chr(10), '<br>')}</div>
                <div class='agent-status-text' style='color:{status_col};'>{status_txt}</div>
            </div>"""

            if i < len(AGENTS) - 1:
                conn_cls = "done" if i in done_set else ("active" if i == active_idx else "")
                nodes_html += f"<div class='agent-connector {conn_cls}'></div>"

        flow_steps = [
            ("Paper Agent", "PDF Parser", "Claims + Methodology"),
            ("Repository Agent", "GitHub Intelligence", "Artifacts + Signals"),
            ("Plausibility Agent", "Reasoning Engine", "Benchmark Feasibility"),
            ("Reviewer Agent", "Peer Review Simulator", "Consensus Board"),
            ("Trust Agent", "Score Synthesizer", "Scientific Confidence"),
        ]
        toolflow_html = ""
        for flow_idx, (agent_name, tool_name, result_name) in enumerate(flow_steps):
            state_cls = "done" if flow_idx in done_set else ("active" if flow_idx == active_idx else "")
            toolflow_html += f"""
            <div class='mcp-flow-card {state_cls}'>
                <div class='mcp-flow-label'>Agent -> Tool -> Result</div>
                <div class='mcp-flow-name'>{agent_name}</div>
                <div class='mcp-flow-meta'>{tool_name}<br>{result_name}</div>
            </div>"""

        # Build terminal lines
        terminal_lines = ""
        for line in log_lines[-12:]:
            terminal_lines += f"<div class='orch-line-done'>› {line}</div>"
        if log_lines:
            terminal_lines += f"<div class='orch-line-active'>█ Processing...</div>"

        pipeline_ph.markdown(f"""<div class='glass-card orchestration-shell' style='padding:24px;'>
<div style='display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:6px;'>
    <div style='display:flex;align-items:center;gap:10px;'>
        <div class='orch-dot'></div>
        <span style='font-size:0.72em;color:#7dd3fc;letter-spacing:0.14em;text-transform:uppercase;font-weight:900;'>Autonomous Agent Runtime</span>
    </div>
    <span style='font-size:0.72em;color:#94a3b8;letter-spacing:0.08em;text-transform:uppercase;'>MCP-style coordination layer</span>
</div>
<div class='agent-pipeline'>{nodes_html}</div>
<div class='mcp-flow-grid'>{toolflow_html}</div>
<div class='orch-terminal'>{terminal_lines}</div>
</div>""", unsafe_allow_html=True)

    def log_callback(msg):
        log_history.append(msg)
        msg_lower = msg.lower()
        for kw, idx in AGENT_KEYWORDS.items():
            if kw in msg_lower and idx > orch_state["active"]:
                # Mark previous as done
                for prev in range(orch_state["active"], idx):
                    orch_state["done"].add(prev)
                orch_state["active"] = idx
                break
        _render_pipeline(orch_state["active"], orch_state["done"], log_history)
        status_ph.markdown(f"""
        <div style='font-family:monospace;font-size:0.85em;color:#58a6ff;
                    padding:8px 14px;border-left:3px solid #58a6ff;
                    background:rgba(88,166,255,0.05);border-radius:0 6px 6px 0;
                    margin:4px 0;'>
            <strong>AGENT →</strong> {msg}
        </div>""", unsafe_allow_html=True)
        time.sleep(0.08)

    # Initial render
    _render_pipeline(0, set(), [])

    try:
        state = run_verification(
            st.session_state['tmp_path'],
            repo_url=st.session_state.get('repo_url', ''),
            model_name=st.session_state['model_name'],
            api_key=st.session_state.get('api_key'),
            github_api_key=st.session_state.get('github_api_key'),
            update_log_callback=log_callback
        )
        # Mark all done on completion
        for i in range(len(AGENTS)):
            orch_state["done"].add(i)
        _render_pipeline(len(AGENTS), orch_state["done"], log_history + ["✅ All agents completed. Rendering audit report..."])
        status_ph.empty()

        st.session_state['final_state'] = state
        st.session_state['running'] = False
        log_assessment(st.session_state['paper_name'], model_name, state.get('credibility_score', 0), state.get('transparency_score', 0), state.get('methodology_score', 0), "N/A")
        st.rerun()
    except Exception as e:
        st.error(f"Critical System Failure: {str(e)}")
        st.session_state['running'] = False



# Results Rendering
if 'final_state' in st.session_state and not st.session_state.get('running'):
    state = st.session_state['final_state']
    paper_name = st.session_state.get('paper_name', 'Uploaded Paper')

    # ── Completed Orchestration Banner ──────────────────────────────────────
    repo_url_disp = st.session_state.get('repo_url', '')
    _AGENTS_DISP = [
        ("📄", "Paper Analysis Agent",        "Ingested PDF, extracted claims, methodology matrix, datasets"),
        ("📂", "Repository Intelligence Agent","Inspected GitHub tree, detected artifacts, fetched community signals"),
        ("📊", "Plausibility Verification Agent","Evaluated benchmark plausibility, cross-referenced domain knowledge"),
        ("👨‍⚖️", "Reviewer Simulation Agent",  "Synthesized 5-panel peer review board with calibrated confidence"),
        ("🏁", "Scientific Trust Agent",       "Computed credibility score, trust trajectory, executive summary"),
    ]

    nodes_done_html = ""
    for icon, name, desc in _AGENTS_DISP:
        nodes_done_html += f"""
        <div class='agent-node'>
            <div class='agent-icon done'>{icon}</div>
            <div class='agent-label done' style='font-size:0.65em;'>{name.replace(' ', '<br>')}</div>
            <div class='agent-status-text' style='color:#7ee787;'>✓ Done</div>
        </div>"""
        if name != _AGENTS_DISP[-1][1]:
            nodes_done_html += "<div class='agent-connector done'></div>"

    # ── Orchestration Provenance Panel Data ──────────────────────────────────
    repo_data_prov = state.get('repo_analysis', {})
    arts_prov = repo_data_prov.get('artifacts', {})
    det_prov  = repo_data_prov.get('detected_list', [])
    comm_prov = repo_data_prov.get('community_signals', {})
    mm_prov   = state.get('methodology_matrix', {})

    st.markdown(f"""<div class='glass-card' style='padding:16px 24px;border:1px solid rgba(46,160,67,0.2);'>
<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;'>
<span class='audit-complete-badge'>✅ Audit Complete — {paper_name}</span>
<span style='font-size:0.75em;color:#8b949e;'>5 agents · Evidence-grounded · Artifact-based</span>
</div>
<div class='agent-pipeline'>{nodes_done_html}</div>

<!-- Orchestration Tool Flow -->
<div class='orch-flow-container'>
<div style='font-size:0.7em;color:#8b949e;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.1em;'>Agent-Tool Coordination Flow</div>
<div class='orch-step'>
<div class='orch-step-icon'>📄</div>
<div class='orch-step-content'>
<div class='orch-step-title'>Paper Analysis Agent → Tool: PDF-Parser</div>
<div class='orch-step-desc explanation-text'>Extracted architecture, benchmarks, and claims from {paper_name}. Identified {len(mm_prov)} methodology signals.</div>
</div>
</div>
<div class='orch-step'>
<div class='orch-step-icon'>📂</div>
<div class='orch-step-content'>
<div class='orch-step-title'>Repository Agent → Tool: GitHub-Intelligence</div>
<div class='orch-step-desc explanation-text'>Scanned branch '{repo_data_prov.get('branch','main')}'. Validated {len(det_prov)} artifacts. Propagated community trust signals (⭐{comm_prov.get('stars',0)}).</div>
</div>
</div>
<div class='orch-step'>
<div class='orch-step-icon'>📊</div>
<div class='orch-step-content'>
<div class='orch-step-title'>Plausibility Agent → Tool: Reasoning-Engine</div>
<div class='orch-step-desc explanation-text'>Validated benchmark realism for {state.get('research_domain','domain')}. Evaluated parameter/compute consistency.</div>
</div>
</div>
<div class='orch-step'>
<div class='orch-step-icon'>👨‍⚖️</div>
<div class='orch-step-content'>
<div class='orch-step-title'>Reviewer Agent → Tool: Peer-Review-Simulator</div>
<div class='orch-step-desc explanation-text'>Synthesized {len(state.get('reviewer_consensus',{}))} expert perspectives with strengths, limitations, concerns, and improvements.</div>
</div>
</div>
<div class='orch-step'>
<div class='orch-step-icon'>🏁</div>
<div class='orch-step-content'>
<div class='orch-step-title'>Scientific Trust Agent → Tool: Score-Synthesizer</div>
<div class='orch-step-desc explanation-text'>Generated credibility, methodology, transparency, and staged trust trajectory outputs without changing scoring logic.</div>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    # ── Orchestration Provenance Panel ───────────────────────────────────────

    prov_items = [
        ("📄 Paper Analysis Agent",   f"PDF ingested · {len(mm_prov)} methodology dimensions parsed · Claims extracted · Domain: {state.get('research_domain','?')}",        "#58a6ff"),
        ("📂 Repository Intelligence","Status: " + repo_data_prov.get('status','No repo') + f" · {len(det_prov)} artifacts detected" + (f" · ⭐{comm_prov.get('stars',0)}" if comm_prov.get('stars') else ""), "#bc8cff"),
        ("📊 Plausibility Agent",     f"{len(state.get('claim_plausibility_analysis',[]))} benchmark claims evaluated against domain knowledge",                               "#d29922"),
        ("👨‍⚖️ Reviewer Agent",        f"{len(state.get('reviewer_consensus',{}))} peer reviewers simulated · Calibrated academic perspectives",                               "#58a6ff"),
        ("🏁 Scientific Trust Agent", f"Credibility: {state.get('credibility_score',0):.1f} · Transparency: {state.get('transparency_score',0):.1f} · Methodology: {state.get('methodology_score',0):.1f}", "#2ea043"),
    ]

    with st.expander("🔍 Orchestration Provenance — Agent Execution Summary", expanded=False):
        for agent_name, detail, color in prov_items:
            st.markdown(f"""
            <div style='display:flex;gap:12px;align-items:flex-start;padding:8px 12px;margin:4px 0;
                        background:rgba(22,27,34,0.6);border-radius:8px;border-left:3px solid {color};'>
                <span style='font-weight:700;color:{color};font-size:0.88em;min-width:220px;'>{agent_name}</span>
                <span style='color:#c9d1d9;font-size:0.84em;'>{detail}</span>
            </div>""", unsafe_allow_html=True)

    # ── 1. Executive Dashboard + Research Strengths ─────────────────────────

    st.markdown(f"## 📑 {state.get('research_domain', 'Research Audit')} | <span style='color:#bc8cff;font-size:1.2rem;'>{state.get('paper_positioning','')}</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='explanation-text' style='border-left:3px solid #bc8cff; padding:10px 20px; background:rgba(188,140,255,0.03); border-radius:0 12px 12px 0;'>{state.get('executive_summary','Summary pending...')}</div>", unsafe_allow_html=True)

    # ── Architecture Grounding Card ──────────────────────────────────────────
    arch = state.get('architecture_details', {})
    if arch:
        a1, a2, a3, a4 = st.columns(4)
        with a1: st.markdown(f"<div class='arch-card'><div class='arch-label'>Model</div><div class='arch-val'>{arch.get('model_name','Stated')}</div></div>", unsafe_allow_html=True)
        with a2: st.markdown(f"<div class='arch-card'><div class='arch-label'>Parameters</div><div class='arch-val'>{arch.get('parameter_count','N/A')}</div></div>", unsafe_allow_html=True)
        with a3: st.markdown(f"<div class='arch-card'><div class='arch-label'>Base</div><div class='arch-val'>{arch.get('base_model','Custom')}</div></div>", unsafe_allow_html=True)
        with a4: st.markdown(f"<div class='arch-card'><div class='arch-label'>Method</div><div class='arch-val'>{arch.get('key_technique','Standard')}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # Scores + Radar side by side
    score_col, radar_col = st.columns([1, 2])
    with score_col:
        cred = state.get('credibility_score', 0)
        meth = state.get('methodology_score', 0)
        trans = state.get('transparency_score', 0)
        
        st.markdown(f"""
        <div style='display:flex; flex-direction:column; gap:16px;'>
            <div class='score-stat-card'>
                <div class='score-ring' style='--score:{min(max(cred, 0), 100):.1f};--ring-color:#6bb8ff;'>
                    <div class='score-val'>{cred:.1f}</div>
                </div>
                <div class='score-label'>Scientific Credibility</div>
            </div>
            <div class='score-stat-card'>
                <div class='score-ring' style='--score:{min(max(meth, 0), 100):.1f};--ring-color:#c59cff;'>
                    <div class='score-val'>{meth:.1f}</div>
                </div>
                <div class='score-label'>Methodological Quality</div>
            </div>
            <div class='score-stat-card'>
                <div class='score-ring' style='--score:{min(max(trans, 0), 100):.1f};--ring-color:#7ee787;'>
                    <div class='score-val'>{trans:.1f}</div>
                </div>
                <div class='score-label'>Structural Transparency</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        personality = state.get('research_personality', '')
        if personality:
            st.markdown(f"<div class='explanation-text' style='margin-top:20px; padding:12px 18px; background:rgba(188,140,255,0.1); border-radius:12px; border:1px solid rgba(188,140,255,0.3); color:#bc8cff;'>🧬 <strong style='color:#fff;'>Research DNA:</strong> {personality}</div>", unsafe_allow_html=True)

    with radar_col:
        if cred or meth or trans:
            categories = ['Scientific Credibility', 'Methodological Quality', 'Structural Transparency', 'Repository Completeness', 'Benchmark Transparency']
            repo_arts = state.get('repo_analysis', {}).get('artifacts', {})
            repo_score = min(100, sum(1 for v in repo_arts.values() if v) / max(len(repo_arts), 1) * 100) if repo_arts else 50
            bench_score = (cred + meth) / 2
            vals = [cred, meth, trans, repo_score, bench_score]
            fig_radar = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=categories + [categories[0]],
                fill='toself', fillcolor='rgba(88,166,255,0.15)',
                line=dict(color='#58a6ff', width=2),
                marker=dict(color='#bc8cff', size=8)
            ))
            fig_radar.update_layout(
                title=dict(text="RESEARCH DNA FINGERPRINT", font=dict(size=22, color='#fff', family='Outfit', weight=800), x=0.5, y=0.98, xanchor='center'),
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', color='#8b949e'),
                    angularaxis=dict(gridcolor='rgba(255,255,255,0.08)', color='#c9d1d9')
                ),
                paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
                margin=dict(l=40, r=40, t=80, b=20), height=350
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    # Research Strengths
    strengths = state.get('research_strengths', {})
    if strengths:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🌟 Research Strengths")
        s_cols = st.columns(4)
        labels = [("💡 Innovation", "strongest_innovation"), ("🔎 Transparency", "strongest_transparency_signal"),
                  ("⚙️ Engineering", "strongest_engineering_signal"), ("🎓 Contribution", "strongest_scientific_contribution")]
        for col, (label, key) in zip(s_cols, labels):
            with col:
                val = strengths.get(key, 'N/A')
                st.markdown(f"<div style='padding:12px;background:rgba(46,160,67,0.07);border:1px solid rgba(46,160,67,0.25);border-radius:8px;font-size:0.82em;'><strong style='color:#7ee787;'>{label}</strong><br><span style='color:#c9d1d9;'>{val}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 2. Repository Intelligence Findings ──────────────────────────────────
    st.markdown("## 🔭 Repository Intelligence Findings")
    st.caption("Static repository analysis · Artifact-based validation · Structural reproducibility assessment")

    repo_data = state.get('repo_analysis', {})
    artifacts = repo_data.get('artifacts', {})
    repo_status = repo_data.get('status', 'No Repository')
    repo_url_val = state.get('repo_url', '')

    # Status badge — use nuanced labels
    badge_color = "#2ea043" if any(w in repo_status for w in ["Full-Stack","Training-Ready"]) else ("#d29922" if any(w in repo_status for w in ["Partial","Inference","Artifact"]) else "#f85149")
    if repo_url_val:
        st.markdown(f"<a href='{repo_url_val}' target='_blank' style='color:#58a6ff;font-size:0.9em;'>🔗 {repo_url_val}</a>", unsafe_allow_html=True)
    st.markdown(f"<span class='repo-status-badge' style='background:{badge_color}22;color:{badge_color};border:1px solid {badge_color};'>● {repo_status}</span>", unsafe_allow_html=True)

    if artifacts:
        total = len(artifacts)
        present_count = sum(1 for v in artifacts.values() if v)
        completeness_pct = int(present_count / total * 100) if total else 0

        # Community Signals Grid
        comm = repo_data.get('community_signals', {})
        if comm:
            st.markdown(f"""
            <div class='community-stat-grid'>
                <div class='community-stat-card'><div class='stat-val'>{comm.get('stars',0)}</div><div class='stat-label'>GITHUB STARS</div></div>
                <div class='community-stat-card'><div class='stat-val'>{comm.get('forks',0)}</div><div class='stat-label'>FORKS</div></div>
                <div class='community-stat-card'><div class='stat-val'>{comm.get('contributors',0)}</div><div class='stat-label'>CONTRIBUTORS</div></div>
                <div class='community-stat-card'><div class='stat-val'>{repo_data.get('branch','main')}</div><div class='stat-label'>ACTIVE BRANCH</div></div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # Completeness progress bar
        bar_color = "#2ea043" if completeness_pct >= 60 else ("#d29922" if completeness_pct >= 30 else "#f85149")
        st.markdown(f"""
        <div class='signal-bar-wrap'>
            <div class='signal-bar-label'>Structural Reproducibility Index — {present_count}/{total} signals detected ({completeness_pct}%)</div>
            <div class='signal-bar-bg'><div class='signal-bar-fill' style='width:{completeness_pct}%; background:linear-gradient(90deg,{bar_color},{bar_color}aa);'></div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.markdown("<div style='font-size:0.8em; font-weight:800; color:var(--success); margin-bottom:12px; letter-spacing:0.05em;'>✅ DETECTED ARTIFACTS</div>", unsafe_allow_html=True)
            found = [k for k, v in artifacts.items() if v]
            for k in found[:10]:
                icon = "📁" if k.endswith('/') or '.' not in k else "📄"
                st.markdown(f"<div class='evidence-item-ok' style='border-radius:10px; padding:10px 15px;'>{icon} {k}</div>", unsafe_allow_html=True)
            if len(found) > 10:
                st.caption(f"+ {len(found)-10} more artifacts detected")
                
        with right_col:
            st.markdown("<div style='font-size:0.8em; font-weight:800; color:var(--warning); margin-bottom:12px; letter-spacing:0.05em;'>⚠️ ABSENT SIGNALS</div>", unsafe_allow_html=True)
            missing = [k for k, v in artifacts.items() if not v]
            for k in missing[:12]:
                st.markdown(f"<div class='evidence-item-warn' style='border-radius:10px; padding:10px 15px;'>🔍 {k}</div>", unsafe_allow_html=True)
    else:
        st.info("No repository was analyzed. Provide a GitHub URL to enable full artifact-based validation.")

    confidence_impact = repo_data.get('confidence_impact', {})
    boosters = confidence_impact.get('boosters', [])
    reducers = confidence_impact.get('reducers', [])
    if boosters or reducers:
        st.markdown("<br>", unsafe_allow_html=True)
        b_col, r_col = st.columns(2)
        with b_col:
            st.markdown("**🟢 Reproducibility Signals — Positive**")
            for b in boosters:
                st.markdown(f"<div class='booster-item'>↑ {b}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with r_col:
            st.markdown("**🟡 Reproducibility Signals — Attention Areas**")
            for r in reducers:
                st.markdown(f"<div class='reducer-item'>→ {r}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tree = repo_data.get('tree_structure', [])
    repro = state.get('reproducibility_evidence_analysis', {})
    tree_col, analysis_col = st.columns([1, 2])
    with tree_col:
        if tree:
            st.markdown("**📂 Repository Structure**")
            artifact_tokens = ("readme", "requirement", "environment", "docker", "train", "eval", "test", "inference", "predict", "config", "checkpoint", "weight", "notebook", "license", "workflow")
            tree_rows = []
            for i, path in enumerate(tree):
                branch = "`--" if i == len(tree) - 1 else "|--"
                safe_path = html.escape(str(path))
                chip = "<span class='artifact-chip'>signal</span>" if any(token in str(path).lower() for token in artifact_tokens) else ""
                tree_rows.append(f"<div class='repo-tree-row'><span class='tree-branch'>{branch}</span> <span class='tree-file'>{safe_path}</span>{chip}</div>")
            st.markdown(f"<div class='repo-tree'><div class='repo-root'>repo/</div>{''.join(tree_rows)}</div>", unsafe_allow_html=True)
    with analysis_col:
        conf = repro.get('reproducibility_confidence', '')
        if conf:
            conf_color = "#2ea043" if conf == "High" else ("#d29922" if conf == "Moderate" else "#f85149")
            st.markdown(f"**Reproducibility Confidence:** <span style='color:{conf_color};font-weight:700;'>{conf}</span>", unsafe_allow_html=True)
            st.caption(repro.get('reproducibility_confidence_reason', ''))
        assessment_text = html.escape(repro.get('structural_reproducibility_assessment', 'No assessment available.'))
        trace_html = "".join(
            f"<div class='trace-item'>💡 {html.escape(str(trace))}</div>"
            for trace in repro.get('reasoning_traces', [])
        )
        st.markdown(f"""
        <details class='ai-disclosure' open>
            <summary>Structural Reproducibility Assessment</summary>
            <div class='ai-disclosure-body explanation-text'>{assessment_text}</div>
            <div class='ai-disclosure-body'>{trace_html}</div>
        </details>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 3. Evidence-Based Verification + Trust Graph ─────────────────────────
    ev_col, trust_col = st.columns([1, 2])
    with ev_col:
        st.markdown("### 🧪 Evidence-Based Verification")
        st.caption("Evaluating transparency signals — not claiming execution of models")
        ev_list = state.get('evidence_verification', [])
        if ev_list:
            for ev in ev_list:
                s = ev.get('status', '')
                s_color = "#2ea043" if "Fully" in s else ("#d29922" if "Partially" in s else "#8b949e")
                st.markdown(f"""
                <details class='ai-disclosure verification-item-card' open>
                    <summary style='display:flex; justify-content:space-between; align-items:center; gap:14px;'>
                        <strong style='color:#fff;'>{ev.get('dimension','')}</strong>
                        <span style='color:{s_color}; font-size:0.8em; font-weight:700;'>{s.upper()}</span>
                    </summary>
                    <div class='ai-disclosure-body explanation-text'>{ev.get('detail', '')}</div>
                </details>""", unsafe_allow_html=True)
        else:
            # Fallback: plausibility checks
            for p in state.get('claim_plausibility_analysis', []):
                status = p.get('status', '')
                color = "#2ea043" if any(w in status for w in ["Consistent", "Plausible", "Competitive"]) else "#d29922"
                st.markdown(f"""
                <details class='ai-disclosure verification-item-card' open>
                    <summary style='display:flex; justify-content:space-between; align-items:center; gap:14px;'>
                        <strong style='color:#fff;'>{p.get('check','')}</strong>
                        <span style='color:{color}; font-size:0.8em; font-weight:700;'>{status.upper()}</span>
                    </summary>
                    <div class='ai-disclosure-body' style='color:#8b949e; font-size:0.75em; margin-bottom:4px; text-transform:uppercase;'>Certainty: {p.get('certainty_level','?')}</div>
                    <div class='ai-disclosure-body explanation-text'>{p.get('reason', '')}</div>
                </details>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with trust_col:
        st.markdown("### 📊 Conceptual Plausibility Analysis")
        st.caption("Cross-referencing stated architecture with domain baselines")
        plaus = state.get('claim_plausibility_analysis', [])
        if plaus:
            for p in plaus:
                status = p.get('status', '')
                color = "#2ea043" if any(w in status for w in ["Consistent", "Plausible", "Competitive"]) else "#d29922"
                st.markdown(f"""
                <details class='ai-disclosure verification-item-card' open>
                    <summary style='display:flex; justify-content:space-between; align-items:center; gap:14px;'>
                        <strong style='color:#fff;'>{p.get('check','')}</strong>
                        <span style='color:{color}; font-size:0.8em; font-weight:700;'>{status.upper()}</span>
                    </summary>
                    <div class='ai-disclosure-body' style='color:#8b949e; font-size:0.75em; margin-bottom:4px; text-transform:uppercase;'>Certainty: {p.get('certainty_level','?')}</div>
                    <div class='ai-disclosure-body explanation-text'>{p.get('reason', '')}</div>
                </details>""", unsafe_allow_html=True)
        else:
            st.info("Conceptual analysis pending...")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Dynamic Scientific Trust Trajectory ──────────────────────────────────────
if 'final_state' in st.session_state and not st.session_state.get('running'):
    state = st.session_state['final_state']
    repo_data = state.get('repo_analysis', {})
    repo_status = repo_data.get('status', 'No Repository Provided')

    st.markdown("## 🛸 Dynamic Scientific Trust Trajectory")
    st.caption("How confidence evolves as evidence is verified · Evidence-grounded · Stage-by-stage reasoning")



    # Build stage scores from real evidence
    _arts = repo_data.get('artifacts', {})
    _comm = repo_data.get('community_signals', {})
    _repro = state.get('reproducibility_evidence_analysis', {})
    _cred  = float(state.get('credibility_score') or 65)
    _meth  = float(state.get('methodology_score') or 65)
    _trans = float(state.get('transparency_score') or 65)

    def _stage_score(base, boosters, reducers):
        return min(100, max(10, base + sum(boosters) + sum(reducers)))

    # Stage 1
    _s1 = _stage_score(50, [10 if _meth > 65 else 5], [])
    _s1_pos = ["+10 Methodology parsed" if _meth > 65 else "+5 Baseline established"]
    _s1_neg = []

    # Stage 2: Methodology matrix
    mm = state.get('methodology_matrix', {})
    _present_m = [k for k, v in mm.items() if v == "Present"]
    _missing_m = [k for k, v in mm.items() if v == "Not Specified"]
    _s2 = _stage_score(_s1, [len(_present_m) * 3], [-len(_missing_m) * 2])
    _s2_pos = [f"+{len(_present_m)*3} methodology dimensions confirmed"] if _present_m else []
    _s2_neg = [f"-{len(_missing_m)*2} dimensions unspecified"] if _missing_m else []

    # Stage 3: Repository structure
    _s3_boost = (8 if _arts.get("README.md") else 0) + (5 if (_arts.get("requirements.txt") or _arts.get("environment.yml")) else 0) + (5 if _arts.get("configs/") else 0)
    _s3 = _stage_score(_s2, [_s3_boost], [-5 if "Minimal" in repo_status else 0])
    _s3_pos = [f"+{_s3_boost} structural artifacts verified"]
    _s3_neg = ["-5 minimal repository structure" if "Minimal" in repo_status else ""]

    # Stage 4: Artifact validation
    _s4_boost = sum([8 if _arts.get("train.py") else 0, 6 if _arts.get("eval.py") else 0,
                     5 if _arts.get("inference.py") else 0, 7 if _arts.get("checkpoints") else 0,
                     4 if _arts.get("notebooks") else 0, 5 if _arts.get("CI/CD files") else 0])
    _s4_reduce = (-5 if not _arts.get("train.py") else 0) + (-4 if not _arts.get("eval.py") else 0)
    _s4 = _stage_score(_s3, [_s4_boost], [_s4_reduce])
    _s4_pos = [f"+{_s4_boost} reproducibility artifacts confirmed"] if _s4_boost else []
    _s4_neg = [f"{_s4_reduce} critical scripts absent"] if _s4_reduce < 0 else []

    # Stage 5: Benchmark
    _plaus = state.get('claim_plausibility_analysis', [])
    _plaus_pos_n = sum(1 for p in _plaus if any(w in p.get('status','') for w in ["Consistent","Plausible","Competitive"]))
    _plaus_risk_n = sum(1 for p in _plaus if "Ambitious" in p.get('status','') or "Validation" in p.get('status',''))
    _s5 = _stage_score(_s4, [_plaus_pos_n * 5], [-_plaus_risk_n * 4])
    _s5_pos = [f"+{_plaus_pos_n*5} benchmark claims plausible"] if _plaus_pos_n else []
    _s5_neg = [f"-{_plaus_risk_n*4} claims need validation"] if _plaus_risk_n else []

    # Stage 6: Community
    _stars = int(_comm.get('stars') or 0)
    _forks = int(_comm.get('forks') or 0)
    _contrib = int(_comm.get('contributors') or 0)
    _s6_boost = min(12, int(_stars/500)*3 + int(_forks/100)*2 + min(_contrib, 5))
    _s6 = _stage_score(_s5, [_s6_boost], [])
    _s6_pos = [f"+{_s6_boost} community adoption (⭐{_stars} ⑂{_forks})"] if _s6_boost else ["No community data"]

    # Stage 7: Reviewer consensus
    _consensus_count = len(state.get('reviewer_consensus', {}))
    _s7_boost = min(8, _consensus_count * 2)
    _s7 = _stage_score(_s6, [_s7_boost], [])
    _s7_pos = [f"+{_s7_boost} reviewer perspectives"]

    # Stage 8: Final — anchored to credibility_score
    _s8 = round(_cred, 1)

    stages = [
        ("📄 Paper Ingested",        round(_s1, 1), _s1_pos, _s1_neg,  "Baseline from paper structure"),
        ("🔬 Methodology Parsed",    round(_s2, 1), _s2_pos, _s2_neg,  f"{len(_present_m)} dimensions confirmed"),
        ("📂 Repository Analyzed",   round(_s3, 1), _s3_pos, _s3_neg,  f"Status: {repo_status}"),
        ("🗂 Artifact Validation",    round(_s4, 1), _s4_pos, _s4_neg,  "Reproducibility artifacts scanned"),
        ("📊 Benchmark Verification", round(_s5, 1), _s5_pos, _s5_neg, f"{_plaus_pos_n} claims plausible"),
        ("🌐 Community Signals",     round(_s6, 1), _s6_pos, [],        f"⭐{_stars} | ⑂{_forks}"),
        ("👨‍⚖️ Reviewer Consensus",   round(_s7, 1), _s7_pos, [],        f"{_consensus_count} reviewers"),
        ("🏁 Final Confidence",      round(_s8, 1), [f"Credibility: {_s8}/100"], [], f"Scientific credibility: {_s8}/100"),
    ]

    x_labels = [s[0] for s in stages]
    y_scores  = [s[1] for s in stages]

    hover_texts = []
    for label, score, pos, neg, summary in stages:
        tip = f"<b>{label}</b><br>Confidence: <b>{score}%</b><br>─────────────<br>{summary}"
        if pos and pos[0]: tip += "<br>" + "<br>".join(f"✅ {p}" for p in pos if p)
        if neg and neg[0]: tip += "<br>" + "<br>".join(f"⚠ {n}" for n in neg if n)
        hover_texts.append(tip)

    def _score_color(s):
        return "#2ea043" if s >= 75 else ("#d29922" if s >= 60 else "#f85149")

    node_colors = [_score_color(s) for s in y_scores]
    node_colors[-1] = "#bc8cff"

    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(x=x_labels, y=[min(s+8,100) for s in y_scores], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig_traj.add_trace(go.Scatter(x=x_labels, y=[max(s-8,0) for s in y_scores], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(88,166,255,0.08)', showlegend=False, hoverinfo='skip'))
    fig_traj.add_trace(go.Scatter(
        x=x_labels, y=y_scores, mode='lines+markers+text', name='Trust Trajectory',
        line=dict(color='#58a6ff', width=3.5, shape='spline'),
        marker=dict(size=[12]*7 + [22], color=node_colors, symbol=['circle']*7 + ['star'], line=dict(color='#0d1117', width=2)),
        text=[f"  {s}%" for s in y_scores], textposition="top center", textfont=dict(size=10, color='#c9d1d9'),
        hovertemplate="%{customdata}<extra></extra>", customdata=hover_texts,
    ))
    fig_traj.add_hline(y=75, line=dict(color='rgba(46,160,67,0.25)', width=1, dash='dot'))
    fig_traj.add_hline(y=50, line=dict(color='rgba(210,153,34,0.2)', width=1, dash='dot'))
    fig_traj.add_annotation(x=x_labels[-1], y=76, text="High Confidence Zone", showarrow=False, font=dict(size=9, color='rgba(46,160,67,0.6)'), xanchor='right')
    fig_traj.add_annotation(x=x_labels[-1], y=51, text="Moderate Zone", showarrow=False, font=dict(size=9, color='rgba(210,153,34,0.5)'), xanchor='right')
    fig_traj.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,17,23,0.6)',
        font=dict(color='#e6edf3', family='Inter, sans-serif'), showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-18, tickfont=dict(size=10, color='#8b949e'), fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, range=[20, 105], ticksuffix='%', tickfont=dict(size=10, color='#8b949e'), fixedrange=True),
        margin=dict(l=20, r=20, t=30, b=90), height=380,
        hoverlabel=dict(bgcolor='#161b22', bordercolor='#58a6ff', font=dict(color='#e6edf3', size=12, family='Inter')),
    )

    st.markdown("### 🧬 Scientific Trust Trajectory")
    st.caption("Conceptual evolution of research confidence throughout the autonomous audit pipeline")
    
    traj_graph_col, traj_panel_col = st.columns([3, 1])
    with traj_graph_col:
        st.plotly_chart(fig_traj, use_container_width=True, config={"displayModeBar": False})
    with traj_panel_col:
        final_score = y_scores[-1]
        badge_label = "High Confidence" if final_score >= 75 else ("Moderate Confidence" if final_score >= 55 else "Limited Evidence")
        badge_col_c = "#2ea043" if final_score >= 75 else ("#d29922" if final_score >= 55 else "#f85149")
        st.markdown(f"""
        <div style='text-align:center;padding:18px 10px;background:rgba(13,17,23,0.7);border:1px solid {badge_col_c}44;border-radius:12px;margin-bottom:14px;'>
            <div style='font-size:2.4rem;font-weight:900;color:{badge_col_c};'>{final_score:.0f}<span style='font-size:1rem;color:#8b949e;'>/100</span></div>
            <div style='margin:6px 0;padding:4px 12px;display:inline-block;background:{badge_col_c}22;border:1px solid {badge_col_c};border-radius:16px;font-size:0.78em;font-weight:700;color:{badge_col_c};'>{badge_label}</div>
            <div style='color:#8b949e;font-size:0.75em;margin-top:6px;'>Final Scientific Confidence</div>
        </div>""", unsafe_allow_html=True)
        all_boosters = repo_data.get('confidence_impact', {}).get('boosters', [])
        all_reducers  = repo_data.get('confidence_impact', {}).get('reducers', [])
        if all_boosters:
            st.markdown("<span style='font-size:0.8em;font-weight:700;color:#7ee787;'>⬆ TRUST DRIVERS</span>", unsafe_allow_html=True)
            for b in all_boosters[:4]:
                st.markdown(f"<div style='font-size:0.75em;color:#c9d1d9;padding:3px 0;border-left:2px solid #2ea043;padding-left:6px;margin:3px 0;'>{b}</div>", unsafe_allow_html=True)
        if all_reducers:
            st.markdown("<span style='font-size:0.8em;font-weight:700;color:#ffa198;margin-top:8px;display:block;'>⬇ RISK FACTORS</span>", unsafe_allow_html=True)
            for r in all_reducers[:3]:
                st.markdown(f"<div style='font-size:0.75em;color:#c9d1d9;padding:3px 0;border-left:2px solid #d29922;padding-left:6px;margin:3px 0;'>{r}</div>", unsafe_allow_html=True)
        rc = _repro.get('reproducibility_confidence', '')
        if rc:
            rc_col = "#2ea043" if rc == "High" else ("#d29922" if rc == "Moderate" else "#f85149")
            st.markdown(f"<div style='margin-top:10px;text-align:center;padding:6px;background:{rc_col}11;border:1px solid {rc_col}44;border-radius:8px;font-size:0.78em;color:{rc_col};'>🔬 Reproducibility: <strong>{rc}</strong></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── Reviewer, Community, Confidence sections ─────────────────────────────────
if 'final_state' in st.session_state and not st.session_state.get('running'):
    state = st.session_state['final_state']
    repo_data = state.get('repo_analysis', {})

    # Reviewer Simulation
    st.markdown("### 👨‍⚖️ Peer Review Board Simulation")
    st.caption("5-panel reviewer simulation — balanced, constructive, academically calibrated | Click ▼ for full reasoning")
    consensus = state.get('reviewer_consensus', {})
    if consensus:
        r_cols = st.columns(min(len(consensus), 3))
        for idx, (rev_name, details) in enumerate(consensus.items()):
            with r_cols[idx % 3]:
                conf_lvl = details.get('confidence_level', 'Moderate')
                conf_color = "#2ea043" if conf_lvl == "High" else ("#d29922" if conf_lvl == "Moderate" else "#8b949e")
                conf_bg = f"{conf_color}22"
                strengths_short = (details.get('strengths','') or '')[:120]
                concern_short = (details.get('constructive_concerns','') or '')[:100]
                st.markdown(f"""
                <div class='reviewer-card'>
                    <strong>{rev_name}</strong><br>
                    <span class='conf-badge' style='background:{conf_bg};color:{conf_color};border:1px solid {conf_color};'>● {conf_lvl} Confidence</span><br>
                    <div class='explanation-text' style='margin-top:10px;'>{details.get('perspective','')[:150]}...</div>
                    <span style='font-size:0.82em; color:#7ee787;'>✅ {strengths_short}...</span><br>
                    <span style='font-size:0.82em; color:#d29922;'>⚠ {concern_short}...</span>
                </div>""", unsafe_allow_html=True)
                with st.expander("▼ Full Analysis"):
                    st.markdown(f"**🟢 Strengths:** {details.get('strengths','')}")
                    st.markdown(f"**🟡 Limitations:** {details.get('limitations','')}")
                    st.markdown(f"**🟠 Constructive Concerns:** {details.get('constructive_concerns','')}")
                    st.markdown(f"**🚀 Actionable Improvements:** {details.get('actionable_improvements','')}")
    st.markdown("#### ❓ Expert Follow-Up Questions")
    for q in state.get('reviewer_questions', []):
        st.markdown(f"<div class='trace-item'>❓ {q}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🏁 Final Audit Conclusion")
    st.markdown(f"<div class='explanation-text' style='padding:15px; background:rgba(46,160,67,0.05); border-radius:10px; border-left:4px solid var(--success);'>{state.get('final_reviewer_perspective', 'Audit complete.')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Community Trust Signals
    community = repo_data.get('community_signals', {})
    if community and community.get('stars') is not None:
        st.markdown("### 🌐 Community Trust Signals")
        st.caption("Real-world adoption metrics from GitHub — community trust is a key scientific credibility signal")
        def fmt_num(n):
            if isinstance(n, int) and n >= 1000: return f"{n/1000:.1f}k"
            return str(n) if n is not None else "N/A"
        
        metrics = [
            ("⭐ Stars", fmt_num(community.get('stars', 0))),
            ("🍴 Forks", fmt_num(community.get('forks', 0))),
            ("👥 Contributors", fmt_num(community.get('contributors', 0))),
            ("👁 Watchers", fmt_num(community.get('watchers', 0))),
            ("🔓 License", community.get('license', 'N/A') or 'N/A'),
            ("📅 Updated", community.get('last_updated', 'N/A') or 'N/A'),
        ]

        # Consolidate into ONE markdown to preserve CSS grid
        cards_html = "".join([f"""
            <div class='community-stat-card' style='padding: 12px 8px;'>
                <div class='stat-val' style='font-size:1.3rem;'>{val}</div>
                <div class='stat-label' style='font-size:0.6em;'>{label}</div>
            </div>""" for label, val in metrics])
        
        st.markdown(f"<div class='community-stat-grid' style='grid-template-columns: repeat(6, 1fr);'>{cards_html}</div>", unsafe_allow_html=True)
        
        stars_c = int(community.get('stars') or 0)
        forks_c = int(community.get('forks') or 0)
        contrib_c = int(community.get('contributors') or 0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Recalibrate baselines for "Elite Research" status
        baselines = [
            ("Research Adoption Index (Stars)", stars_c, 200000, "#58a6ff"),
            ("Community Vitality (Forks)", forks_c, 50000, "#bc8cff"),
            ("Collaborative Reach (Contributors)", contrib_c, 500, "#7ee787")
        ]
        
        for bar_label, val, target, bar_col in baselines:
            pct = min(val / target * 100, 100)
            st.markdown(f"""
            <div class='signal-bar-wrap' style='margin-bottom:20px;'>
                <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px;'>
                    <div>
                        <div class='signal-bar-label' style='margin-bottom:2px;'>{bar_label}</div>
                        <div style='font-size:0.7em; color:#8b949e;'>Target Baseline: {fmt_num(target)} signals</div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-size:1.1rem; font-weight:900; color:{bar_col}; line-height:1;'>{pct:.1f}%</div>
                        <div style='font-size:0.65em; color:#8b949e; text-transform:uppercase; letter-spacing:1px;'>Elite Standing</div>
                    </div>
                </div>
                <div class='signal-bar-bg' style='height:8px; background:rgba(255,255,255,0.03);'>
                    <div class='signal-bar-fill' style='width:{pct:.1f}%; background:linear-gradient(90deg, {bar_col}88, {bar_col}); box-shadow: 0 0 15px {bar_col}33;'></div>
                </div>
            </div>""", unsafe_allow_html=True)
        
        lang = community.get('language', 'N/A')
        desc = community.get('description', '')
        footer_text = f"🔧 **{lang}**" + (f" &nbsp;|&nbsp; {desc}" if desc else "")
        st.markdown(f"<div style='margin-top:10px; color:#8b949e; font-size:0.85em; border-top:1px solid rgba(255,255,255,0.05); padding-top:15px;'>{footer_text}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Scientific Confidence Interpretation
    st.markdown("### 🧭 Scientific Confidence Interpretation")
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown("**✅ What VerifyAI CAN evaluate**")
        st.markdown("<div class='explanation-text'>", unsafe_allow_html=True)
        st.markdown("""
- Repository structure & artifact completeness
- Documentation quality & clarity
- Methodological transparency in the paper
- Benchmark claim plausibility vs. domain knowledge
- Engineering maturity signals
- Configuration & checkpoint availability
""")
        st.markdown("</div>", unsafe_allow_html=True)
    with i2:
        st.markdown("**⚠️ What VerifyAI CANNOT guarantee**")
        st.markdown("<div class='explanation-text'>", unsafe_allow_html=True)
        st.markdown("""
- Whether results are numerically reproducible
- Execution of large-scale models
- Third-party independent replication
- Dataset availability or access rights
- Community-level validation
""")
        st.markdown("</div>", unsafe_allow_html=True)
    with i3:
        st.markdown("**📖 Transparency ≠ Truth**")
        st.markdown("<div class='explanation-text'>", unsafe_allow_html=True)
        st.markdown("""
A high transparency score reflects **openness and documentation quality**, not guaranteed correctness.
A low score reflects **limited public evidence**, not fraud.
All audits are based on **static artifact analysis** — not runtime execution.
""")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.15), rgba(255,255,255,0)); margin-top: 4rem; margin-bottom: 1.5rem;">
<div style="text-align: center; color: rgba(255, 255, 255, 0.5); font-family: monospace; font-size: 0.85rem; letter-spacing: 0.05em;">
    Engineered by <span style="color: #64ffda; font-weight: 600;">Ankita Muni</span>
    <div style="margin-top: 0.5rem;">
        <a href="https://github.com/AnkitaMuni" target="_blank" style="color: #a8b2d1; text-decoration: none; margin: 0 10px; transition: color 0.2s;">⚡ GitHub</a> • 
        <a href="https://linkedin.com/in/ankita-muni-66512331a" target="_blank" style="color: #a8b2d1; text-decoration: none; margin: 0 10px; transition: color 0.2s;">💼 LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)

