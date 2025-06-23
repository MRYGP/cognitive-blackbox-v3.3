# cognitive-blackbox/presentation/app.py
# -----------------------------------------------------------------------------
# Cognitive Black Box - Main Application Entry Point
# Version: v4.0 (Genesis Mode - FINAL & STABLE v18)
# Author: Hoshino AI PM
# This version removes @st.cache_data to eliminate any potential conflicts
# between caching and session state in the Streamlit Cloud environment.
# This prioritizes stability and predictability above all else.
# -----------------------------------------------------------------------------

import streamlit as st
import sys
import re
from pathlib import Path
import json
from typing import Dict, List, Optional

# --- Path Setup ---
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from core.models import Act, Case
from core.engine import AIEngine
from config.settings import AppConfig

# =============================================================================
# HELPER FUNCTIONS (THE FIX IS HERE)
# =============================================================================

# We REMOVE the @st.cache_data decorator.
# The function will now be executed on every run where it's needed,
# ensuring the freshest state and avoiding any caching side effects.
def load_and_parse_case(case_id: str) -> Optional[Case]:
    # ... (The rest of this function's code remains exactly the same)
    try:
        base_path = PROJECT_ROOT / "config" / "cases"
        case_json_path = base_path / f"{case_id}.json"
        with open(case_json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        script_file_path = base_path / data['script_file']
        with open(script_file_path, 'r', encoding='utf-8') as f: script_content = f.read()
    except FileNotFoundError:
        st.error(f"严重错误: 找不到案例 '{case_id}' 的配置文件或脚本文件。")
        return None
    def parse_script(content: str) -> Dict[int, Act]:
        acts: Dict[int, Act] = {}
        chunks = content.split("--- ACT_SEPARATOR ---")
        titles = ["决策代入", "现实击穿", "框架重构", "能力武装"]
        roles = ["host", "investor", "mentor", "assistant"]
        for i, chunk in enumerate(chunks):
            act_num = i + 1
            if not chunk.strip(): continue
            acts[act_num] = Act(
                act_id=act_num, title=titles[i] if i < len(titles) else f"第 {act_num} 幕",
                role_id=roles[i] if i < len(roles) else "assistant", content=chunk.strip())
        return acts
    parsed_acts = parse_script(script_content)
    return Case(id=data['id'], title=data['title'], tagline=data['tagline'], bias=data['bias'],
                icon=data['icon'], difficulty=data['difficulty'], duration_min=data['duration_min'],
                estimated_loss_usd=data['estimated_loss_usd'], acts=parsed_acts)

# --- The rest of the app.py file remains exactly the same as v15 ---
# (initialize_state, render_case_selection, render_act_view, main)
def initialize_state():
    if 'view' not in st.session_state: st.session_state.view = "selection"
    if 'case_id' not in st.session_state: st.session_state.case_id = None
    if 'case_obj' not in st.session_state: st.session_state.case_obj = None
    if 'act_num' not in st.session_state: st.session_state.act_num = 1
    if 'context' not in st.session_state: st.session_state.context = {}
    if 'engine' not in st.session_state: st.session_state.engine = AIEngine()

def render_case_selection():
    st.title(f"{AppConfig.PAGE_ICON} {AppConfig.PAGE_TITLE}")
    st.markdown("我们不教授知识，我们架构智慧。选择一个世界级失败案例，开启你的认知升级之旅。")
    for case_file in sorted(list((PROJECT_ROOT / "config" / "cases").glob("*.json"))):
        with open(case_file, 'r', encoding='utf-8') as f: data = json.load(f)
        with st.container(border=True):
            col1, col2 = st.columns([0.1, 0.9]); col1.header(data.get('icon', '❓'))
            with col2:
                st.subheader(data.get('title')); st.caption(f"{data.get('tagline')} | 认知偏误: {', '.join(data.get('bias', []))}")
            if st.button(f"进入 **{data.get('title')}** 体验", key=f"btn_{data.get('id')}"):
                st.session_state.view, st.session_state.case_id = "act", data.get('id')
                st.session_state.act_num, st.session_state.context = 1, {}
                st.rerun()

def render_act_view():
    case: Case = st.session_state.case_obj
    act_num = st.session_state.act_num
    if not case or act_num not in case.acts:
        st.error("无法加载当前幕的内容，请返回案例选择重试。")
        if st.button("返回案例选择"): st.session_state.view, st.session_state.case_id, st.session_state.case_obj = "selection", None, None; st.rerun()
        return
    act = case.acts[act_num]
    st.progress(act_num / len(case.acts), text=f"第 {act.act_id} 幕: {act.title}")
    st.markdown(act.content, unsafe_allow_html=True)
    if act.act_id == 1:
        options = ["A. 风险可控", "B. 小额试水", "C. 需要更多时间", "D. 拒绝投资"]
        choice = st.radio("您的决策是？", options, key="act1_choice", horizontal=True, label_visibility="collapsed")
        if st.button("确认我的决策", type="primary"):
            st.session_state.context['act1_choice'] = choice; st.session_state.act_num = 2; st.rerun()
    elif act.act_id == 2:
        if 'question' not in st.session_state.context:
            with st.spinner("AI正在分析您的决策..."):
                st.session_state.context['question'] = st.session_state.engine.generate_personalized_question(st.session_state.context)
        st.warning(f"**AI质疑:** {st.session_state.context.get('question')}")
    elif act.act_id == 4:
         with st.form("tool_form"):
            st.subheader("个性化决策工具生成"); name = st.text_input("您的姓名/昵称"); principle = st.text_area("您的核心决策原则")
            if st.form_submit_button("生成我的专属工具", type="primary"):
                st.session_state.context['user_name'], st.session_state.context['user_principle'] = name, principle
                with st.spinner("AI导师正在为您定制免疫系统..."):
                    st.session_state.context['tool'] = st.session_state.engine.generate_personalized_tool(st.session_state.context)
         if st.session_state.context.get('tool'):
             st.markdown("---"); st.subheader(f"为 {st.session_state.context.get('user_name','您')} 定制的决策免疫系统"); st.markdown(st.session_state.context['tool'], unsafe_allow_html=True)
    col1, _, col2 = st.columns([0.2, 0.6, 0.2])
    if act_num > 1 and col1.button("上一幕"): st.session_state.act_num -= 1; st.rerun()
    if act_num < len(case.acts) and col2.button("下一幕", type="primary"): st.session_state.act_num += 1; st.rerun()
    st.markdown("---")
    if st.button("返回案例选择"): st.session_state.view, st.session_state.case_id, st.session_state.case_obj = "selection", None, None; st.rerun()

def main():
    st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout="wide")
    initialize_state()
    if st.session_state.view == "act" and st.session_state.case_id:
        if st.session_state.case_obj is None or st.session_state.case_obj.id != st.session_state.case_id:
            st.session_state.case_obj = load_and_parse_case(st.session_state.case_id)
    if st.session_state.view == "selection": render_case_selection()
    elif st.session_state.view == "act": render_act_view()

if __name__ == "__main__":
    main()
