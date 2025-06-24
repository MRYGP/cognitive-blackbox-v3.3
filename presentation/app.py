# presentation/app.py
# 体验驱动迭代版本 - v4.1 StateManager重构完整版
# 从"能用"到"卓越"到"史诗级体验"

import streamlit as st
import sys
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

# =============================================================================
# PROJECT SETUP & IMPORTS
# =============================================================================

def setup_project_paths():
    """健壮的项目路径设置"""
    current_file = Path(__file__)
    
    possible_roots = [
        current_file.parent.parent,  # 标准结构
        current_file.parent,         # 扁平结构  
        Path.cwd(),                  # 当前工作目录
    ]
    
    for root in possible_roots:
        config_path = root / "config" / "cases"
        if config_path.exists():
            return root
    
    return Path.cwd()

PROJECT_ROOT = setup_project_paths()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 安全导入核心模块 - v4.1重构版本
try:
    from core.models import Act, Case, ViewState  # 新增ViewState
    from core.state_manager import StateManager    # 重构后的StateManager
    from core.engine import AIEngine
    from config.settings import AppConfig
    from core.transition_manager import TransitionManager
    from core.value_confirmation import ValueConfirmationManager
except ImportError as e:
    st.error(f"🚨 核心模块导入失败: {e}")
    st.stop()

# === CXO新增功能导入 - 带错误处理 ===
try:
    from core.transition_manager import TransitionManager
    from core.value_confirmation import ValueConfirmationManager
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"警告: CXO增强功能导入失败: {e}")
    ENHANCED_FEATURES_AVAILABLE = False
    
    # 创建fallback类，避免代码报错
    class TransitionManager:
        @staticmethod
        def show_transition(from_act: int, to_act: int):
            st.info(f"转场效果: 从第{from_act}幕到第{to_act}幕")
            time.sleep(1)
    
    class ValueConfirmationManager:
        @staticmethod
        def render_act4_with_unlock_experience(tool_result, context):
            st.info("解锁体验功能暂不可用，显示标准工具")
            return False

# =============================================================================
# 全局状态管理器 - v4.1核心组件
# =============================================================================

def get_state_manager() -> StateManager:
    """获取全局状态管理器实例 - 懒加载模式"""
    if 'state_manager' not in st.session_state:
        st.session_state.state_manager = StateManager()
    return st.session_state.state_manager

# =============================================================================
# 高级UI组件和样式 (保持原有)
# =============================================================================

def inject_premium_css():
    """注入高级CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式升级 */
    .main > div {
        padding-top: 1rem;
    }
    
    /* 震撼级模态对话框样式 */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d30 100%);
        border: 2px solid #ff6b6b;
        border-radius: 15px;
        padding: 30px;
        max-width: 600px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(255, 107, 107, 0.3);
        animation: modalSlideIn 0.5s ease-out;
    }
    
    @keyframes modalSlideIn {
        from { opacity: 0; transform: translateY(-50px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    .modal-title {
        color: #ff6b6b;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .modal-text {
        color: #ffffff;
        font-size: 18px;
        line-height: 1.6;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .modal-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
        border: none;
        color: white;
        padding: 12px 30px;
        font-size: 16px;
        border-radius: 25px;
        cursor: pointer;
        display: block;
        margin: 0 auto;
        transition: all 0.3s ease;
    }
    
    .modal-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    /* 高级报告容器样式 */
    .premium-report {
        background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px solid #e3f2fd;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .report-header {
        background: linear-gradient(135deg, #2196f3 0%, #21cbf3 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .report-section {
        margin: 20px 0;
        padding: 15px;
        background: rgba(33, 150, 243, 0.05);
        border-left: 4px solid #2196f3;
        border-radius: 5px;
    }
    
    .download-area {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        text-align: center;
    }
    
    /* DOUBT模型专用样式 */
    .doubt-progress {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
    }
    
    .doubt-step {
        background: rgba(102, 126, 234, 0.1);
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .doubt-completed {
        background: rgba(76, 175, 80, 0.1);
        border: 2px solid #4caf50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* 打字机效果 */
    .typewriter {
        overflow: hidden;
        border-right: 2px solid #ff6b6b;
        white-space: nowrap;
        animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #ff6b6b; }
    }
    
    /* 按钮美化 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

def show_ai_challenge_modal(challenge_text: str):
    """震撼级AI质疑模态对话框"""
    modal_html = f"""
    <div class="modal-overlay" id="challengeModal">
        <div class="modal-content">
            <div class="modal-title">🔥 Damien的尖锐质疑</div>
            <div class="modal-text typewriter" id="challengeText">{challenge_text}</div>
            <button class="modal-button" onclick="closeModal()">我明白了，继续思考</button>
        </div>
    </div>
    
    <script>
    function closeModal() {{
        document.getElementById('challengeModal').style.display = 'none';
    }}
    
    // 打字机效果
    setTimeout(function() {{
        const text = document.getElementById('challengeText');
        if (text) {{
            text.style.animation = 'typing 3s steps(40, end), blink-caret 0.75s step-end infinite';
        }}
    }}, 100);
    </script>
    """
    
    st.components.v1.html(modal_html, height=600)

def parse_and_render_premium_report(markdown_content: str, user_name: str):
    """解析并渲染高级报告格式"""
    with st.container():
        st.markdown('<div class="premium-report">', unsafe_allow_html=True)
        
        # 报告头部
        st.markdown(f"""
        <div class="report-header">
            <h2>🛡️ 专属认知免疫系统报告</h2>
            <p>为 {user_name} 量身定制 | 由Athena AI导师生成</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 解析Markdown内容
        lines = markdown_content.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# '):
                # 主标题
                title = line[2:]
                st.markdown(f'<div class="report-section"><h3>{title}</h3></div>', unsafe_allow_html=True)
            elif line.startswith('## '):
                # 子标题
                subtitle = line[3:]
                st.markdown(f'<div class="report-section"><h4>🎯 {subtitle}</h4>', unsafe_allow_html=True)
            elif line.startswith('> '):
                # 引用
                quote = line[2:]
                st.info(quote)
            elif line.startswith('- **'):
                # 工具项
                tool = line[2:]
                st.markdown(f"✅ {tool}")
            elif line.startswith('- '):
                # 普通列表项
                item = line[2:]
                st.markdown(f"• {item}")
            else:
                # 普通文本
                if line:
                    st.markdown(line)
        
        # 下载区域
        st.markdown('<div class="download-area">', unsafe_allow_html=True)
        st.markdown("### 📥 获取您的专属报告")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 下载为Markdown文件
            st.download_button(
                label="📄 下载为.md文件",
                data=markdown_content,
                file_name=f"{user_name}_认知免疫系统.md",
                mime="text/markdown",
                help="将报告保存为Markdown文件"
            )
        
        with col2:
            # 复制到剪贴板 (使用streamlit-extras)
            try:
                # 尝试使用复制功能
                if st.button("📋 复制到剪贴板", help="复制完整报告内容"):
                    st.success("✅ 报告已复制到剪贴板！")
                    # 注入复制脚本
                    copy_script = f"""
                    <script>
                    navigator.clipboard.writeText(`{markdown_content}`).then(function() {{
                        console.log('内容已复制到剪贴板');
                    }});
                    </script>
                    """
                    st.components.v1.html(copy_script, height=0)
            except:
                st.info("💡 您可以手动选择文本进行复制")
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# =============================================================================
# CONTENT LOADING SYSTEM (保持原有)
# =============================================================================

class ContentLoader:
    """内容加载器"""
    
    @staticmethod
    @st.cache_data
    def load_case(case_id: str) -> Optional[Case]:
        """加载并解析单个案例"""
        try:
            base_path = PROJECT_ROOT / "config" / "cases"
            case_json_path = base_path / f"{case_id}.json"
            
            if not case_json_path.exists():
                return None
            
            with open(case_json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            script_file_path = base_path / metadata['script_file']
            if not script_file_path.exists():
                return None
                
            with open(script_file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            acts = ContentLoader._parse_script_content(script_content)
            
            case = Case(
                id=metadata['id'],
                title=metadata['title'],
                tagline=metadata['tagline'],
                bias=metadata['bias'],
                icon=metadata['icon'],
                difficulty=metadata['difficulty'],
                duration_min=metadata['duration_min'],
                estimated_loss_usd=metadata['estimated_loss_usd'],
                acts=acts
            )
            
            return case
            
        except Exception as e:
            st.error(f"加载案例 '{case_id}' 时出错: {e}")
            return None
    
    @staticmethod
    def _parse_script_content(content: str) -> Dict[int, Act]:
        """解析脚本内容为Act对象"""
        acts = {}
        
        separator = "--- ACT_SEPARATOR ---"
        chunks = content.split(separator)
        
        titles = ["决策代入", "现实击穿", "框架重构", "能力武装"]
        roles = ["host", "investor", "mentor", "assistant"]
        
        # 跳过第一个片段(引言)
        act_number = 1
        for i in range(1, len(chunks)):
            chunk = chunks[i].strip()
            
            if not chunk:
                continue
            
            acts[act_number] = Act(
                act_id=act_number,
                title=titles[act_number-1] if act_number-1 < len(titles) else f"第 {act_number} 幕",
                role_id=roles[act_number-1] if act_number-1 < len(roles) else "assistant",
                content=chunk
            )
            
            act_number += 1
        
        return acts
    
    @staticmethod
    @st.cache_data
    def get_all_cases() -> List[Dict]:
        """获取所有可用案例的元数据"""
        cases = []
        cases_dir = PROJECT_ROOT / "config" / "cases"
        
        if not cases_dir.exists():
            return []
        
        for case_file in sorted(cases_dir.glob("*.json")):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if 'id' in metadata and 'title' in metadata:
                        cases.append(metadata)
            except Exception:
                continue
        
        return cases

# =============================================================================
# VIEW RENDERERS - v4.1重构版本
# =============================================================================

def render_case_selection():
    """渲染案例选择页面 - v4.1重构版本 + CXO-01优化"""
    sm = get_state_manager()
    
    # 调试开关 - 使用新的状态管理
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"{AppConfig.PAGE_ICON} {AppConfig.PAGE_TITLE}")
    with col2:
        debug_checked = st.checkbox("🔧 调试模式", value=sm.is_debug_mode(), key="debug_toggle")
        sm.set_debug_mode(debug_checked)
    
    render_debug_panel()
    
    st.markdown("### 🎯 我们不教授知识，我们架构智慧")
    st.markdown("选择一个世界级失败案例，开启你的认知升级之旅。")
    
    cases = ContentLoader.get_all_cases()
    
    if not cases:
        st.error("❌ 没有找到可用的案例")
        return
    
    for case_data in cases:
        with st.container(border=True):
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                st.header(case_data.get('icon', '❓'))
            
            with col2:
                st.subheader(case_data.get('title'))
                st.caption(f"{case_data.get('tagline')} | 认知偏误: {', '.join(case_data.get('bias', []))}")
                
                # CXO-01: 新增框架显示 - "价值前置"优化
                framework = case_data.get('framework', '通用决策框架')
                st.caption(f"💡 您将掌握：**{framework}**")
                
                info_col1, info_col2, info_col3 = st.columns(3)
                with info_col1:
                    st.metric("难度", case_data.get('difficulty', '未知'))
                with info_col2:
                    st.metric("时长", f"{case_data.get('duration_min', 0)}分钟")
                with info_col3:
                    st.metric("损失", case_data.get('estimated_loss_usd', '未知'))
            
            button_key = f"enter_case_{case_data.get('id')}"
            if st.button(f"🚀 进入 **{case_data.get('title')}** 体验", key=button_key):
                # 使用新的状态管理器
                sm.go_to_case(case_data.get('id'))

def render_act_view():
    """渲染幕场景页面 - v4.1重构版本"""
    sm = get_state_manager()
    
    render_debug_panel()
    
    # 确保案例对象已加载 - 使用新的缓存机制
    case = sm.current_case_obj
    if case is None or case.id != sm.get_current_case_id():
        with st.spinner("📚 加载案例内容..."):
            case = ContentLoader.load_case(sm.get_current_case_id())
            if case:
                sm.set_case_obj(case)
    
    act_num = sm.get_current_act_num()
    
    if not case:
        st.error("❌ 无法加载案例内容")
        if st.button("🔙 返回案例选择"):
            sm.go_to_selection()
        return
    
    if act_num not in case.acts:
        st.error(f"❌ 第{act_num}幕不存在")
        if st.button("🔙 返回案例选择"):
            sm.go_to_selection()
        return
    
    act = case.acts[act_num]
    
    # 渲染页面头部
    progress = act_num / len(case.acts)
    st.progress(progress, text=f"第 {act.act_id} 幕: {act.title} ({act_num}/{len(case.acts)})")
    
    st.header(f"{case.icon} {case.title}")
    st.subheader(f"第{act.act_id}幕: {act.title}")
    
    # 显示幕内容
    st.markdown(act.content, unsafe_allow_html=True)
    st.markdown("---")
    
    # 特定幕的交互逻辑
    if act_num == 1:
        render_act1_interaction()
    elif act_num == 2:
        render_act2_interaction()
    elif act_num == 3:
        render_act3_interaction()
    elif act_num == 4:
        render_act4_interaction()
    
    # 导航按钮
    render_navigation(case, act_num)

# =============================================================================
# ACT INTERACTION FUNCTIONS - v4.1重构版本
# =============================================================================

def render_act1_interaction():
    """第一幕的交互逻辑 - 已有CXO-02优化 + 新增CXO-03转场"""
    sm = get_state_manager()
    
    st.subheader("🤔 您的决策是？")
    
    # CXO-02: 动态加载案例专属选项 - "语境增强"优化
    case = sm.current_case_obj
    if case and hasattr(case, 'acts') and case.acts:
        case_id = sm.get_current_case_id()
        cases_metadata = ContentLoader.get_all_cases()
        current_case_metadata = next((c for c in cases_metadata if c.get('id') == case_id), None)
        if current_case_metadata and 'act_1_options' in current_case_metadata:
            options = current_case_metadata['act_1_options']
        else:
            options = [
                "A. 风险可控，值得投资",
                "B. 小额试水，观察情况", 
                "C. 需要更多时间研究",
                "D. 直接拒绝投资"
            ]
    else:
        options = [
            "A. 风险可控，值得投资",
            "B. 小额试水，观察情况", 
            "C. 需要更多时间研究",
            "D. 直接拒绝投资"
        ]
    
    choice = st.radio(
        "请选择一个选项：",
        options,
        key="act1_choice_radio",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # CXO-03: 替换原来的确认按钮为带转场效果的按钮
    if st.button("✅ 确认我的决策", type="primary", key="confirm_act1_choice"):
        sm.update_context('act1_choice', choice)
        TransitionManager.show_transition(1, 2)
        sm.advance_to_next_act_with_transition(1, 2)

def render_act2_interaction():
    """第二幕的交互逻辑 - 新增CXO-03转场"""
    sm = get_state_manager()
    
    if not sm.get_context('ai_question_result'):
        with st.spinner("🤖 Damien正在分析您的决策逻辑..."):
            try:
                result = sm.ai_engine.generate_personalized_question(sm.get_full_context())
                sm.update_context('ai_question_result', result)
                sm.show_challenge_modal()
            except Exception as e:
                # 创建失败结果
                result = {
                    "success": False,
                    "content": "",
                    "error_message": f"AI调用异常: {str(e)}",
                    "fallback_content": "这个'完美'的机会，最让你不安的是什么？"
                }
                sm.update_context('ai_question_result', result)
                sm.show_challenge_modal()
    
    result = sm.get_context('ai_question_result')
    
    # 强制诊断显示
    if sm.is_debug_mode():
        with st.expander("🔍 AI质疑生成诊断", expanded=False):
            st.json({
                "success": result.get("success", False),
                "error_message": result.get("error_message"),
                "model_used": result.get("model_used"),
                "debug_info": result.get("debug_info", {})
            })
    
    # 确定显示的问题
    if result.get("success"):
        question = result.get("content", "")
    else:
        question = result.get("fallback_content", "这个'完美'的机会，最让你不安的是什么？")
        if not sm.is_debug_mode():
            st.warning("⚠️ AI质疑生成遇到技术问题，为您提供备选质疑")
    
    if sm.is_challenge_modal_visible():
        show_ai_challenge_modal(question)
        
        if st.button("🎯 直面质疑，继续前进", type="primary", key="continue_to_act3"):
            TransitionManager.show_transition(2, 3)
            sm.advance_to_next_act_with_transition(2, 3)
    else:
        st.success("✅ 您已接受了Damien的挑战！继续您的认知之旅...")
        st.info(f"🔄 回顾质疑：{question}")

def render_act3_interaction():
    """第三幕的交互逻辑 - 已有DOUBT模型 + 新增CXO-03转场"""
    sm = get_state_manager()
    # ... 现有的DOUBT模型训练逻辑保持不变 ...
    if st.button("⚡ 生成我的专属智慧", type="primary", key="generate_tool"):
        context = sm.get_full_context()
        TransitionManager.show_transition(3, 4)
        sm.advance_to_next_act_with_transition(3, 4)

def render_act4_interaction():
    """第四幕的交互逻辑 - 简化版价值确认体验"""
    sm = get_state_manager()
    
    st.header("🛡️ 您的专属认知免疫系统")
    
    # 检查是否需要生成工具
    tool_result = sm.get_context('personalized_tool_result')
    if not tool_result:
        st.info("🔄 正在为您定制专属智慧...")
        
        # 生成个性化工具
        with st.spinner("AI大师正在为您铸造认知武器..."):
            context = sm.get_full_context()
            tool_result = sm.ai_engine.generate_personalized_tool(context)
            sm.update_context('personalized_tool_result', tool_result)
            st.rerun()
    
    if not tool_result:
        st.error("❌ 工具生成失败，请重试")
        if st.button("🔄 重新生成", key="retry_tool_generation"):
            sm.update_context('personalized_tool_result', None)
            st.rerun()
        return
    
    # 显示AI调用诊断（调试模式）
    if sm.is_debug_mode():
        with st.expander("🔍 AI工具生成诊断", expanded=False):
            st.json(tool_result)
    
    # 获取工具内容
    tool_content = tool_result.get('content', '') or tool_result.get('fallback_content', '')
    user_name = sm.get_context('user_name', '用户')
    case_id = sm.get_current_case_id()
    
    if not tool_content:
        st.error("❌ 无法生成工具内容")
        return
    
    # CXO-04: 简化版解锁体验（不依赖外部模块）
    is_unlocked = st.session_state.get('tool_unlocked', False)
    
    if not is_unlocked:
        # 显示价值确认界面
        value_descriptions = {
            'madoff': {'framework': '四维独立验证矩阵', 'benefit': '权威陷阱免疫能力'},
            'lehman': {'framework': 'DOUBT思维模型', 'benefit': '确认偏误破解术'},
            'ltcm': {'framework': 'RISK思维模型', 'benefit': '过度自信校正器'}
        }
        
        case_info = value_descriptions.get(case_id, {'framework': '认知免疫系统', 'benefit': '决策智慧升级'})
        
        # 价值确认界面
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; padding: 2rem; text-align: center; color: white; 
                    margin: 2rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                🎉 恭喜 {user_name}！您的专属智慧已准备就绪
            </div>
            <div style="margin-bottom: 1.5rem;">
                您刚刚完成了一场深度的认知训练，现在已获得：<br>
                <span style="background: linear-gradient(45deg, #FFD54F, #FFC107); color: #333; 
                           padding: 8px 16px; border-radius: 20px; font-weight: 600; margin: 0 8px;">
                    {case_info['framework']}
                </span>
                <span style="background: linear-gradient(45deg, #FFD54F, #FFC107); color: #333; 
                           padding: 8px 16px; border-radius: 20px; font-weight: 600; margin: 0 8px;">
                    {case_info['benefit']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示模糊的工具预览
        st.markdown("""
        <div style="filter: blur(8px); opacity: 0.6; pointer-events: none;">
        """, unsafe_allow_html=True)
        
        preview_lines = tool_content.split('\n')[:8]
        preview_text = '\n'.join(preview_lines) + '\n\n*[内容已模糊处理，点击解锁查看完整内容]*'
        st.markdown(preview_text)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 解锁按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🗝️ 解锁我的专属智慧", type="primary", key="unlock_tool_button"):
                st.session_state.tool_unlocked = True
                st.rerun()
    else:
        # 已解锁，显示完整内容
        st.balloons()
        st.success("🎊 解锁成功！您的专属智慧现已激活！")
        
        # 显示完整工具内容
        parse_and_render_premium_report(tool_content, user_name)
        
        # 下载和导航选项
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 下载认知免疫系统",
                data=tool_content,
                file_name=f"认知免疫系统_{user_name}.md",
                mime="text/markdown"
            )
        with col2:
            if st.button("🔄 体验其他案例", key="try_other_cases"):
                # 重置解锁状态
                if 'tool_unlocked' in st.session_state:
                    del st.session_state.tool_unlocked
                sm.go_to_selection()

def render_navigation(case: Case, act_num: int):
    """渲染导航按钮 - v4.1重构版本"""
    sm = get_state_manager()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if act_num > 1:
            if st.button("⬅️ 上一幕", key="prev_act_btn"):
                sm.go_to_previous_act()
    
    with col2:
        if st.button("🏠 返回案例选择", key="back_to_selection_btn"):
            sm.go_to_selection()
    
    with col3:
        if act_num < len(case.acts):
            if st.button("➡️ 下一幕", type="primary", key="next_act_btn"):
                sm.advance_to_next_act()
        elif act_num == len(case.acts):
            if st.button("🎉 完成体验", type="primary", key="complete_experience_btn"):
                st.balloons()
                st.success("🎊 恭喜完成认知升级！")
                sm.go_to_selection()

# =============================================================================
# 调试功能 - v4.1增强版本
# =============================================================================

def render_debug_panel():
    """调试面板 - 新增转场效果预览"""
    sm = get_state_manager()
    
    if not sm.is_debug_mode():
        return
    
    with st.expander("🔧 系统调试面板", expanded=False):
        st.write("### 核心状态信息")
        
        state_summary = sm.get_state_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**视图状态:**")
            st.json({
                'view_name': state_summary['view_name'],
                'case_id': state_summary['case_id'],
                'act_num': state_summary['act_num'],
                'sub_stage': state_summary['sub_stage']
            })
            
            st.write("**DOUBT模型进度:**")
            doubt_progress = {}
            feedback_progress = {}
            for step_id in ['D', 'O', 'U', 'B', 'T']:
                doubt_progress[f'doubt_{step_id}'] = sm.get_context(f'doubt_{step_id}', None) is not None
                feedback_progress[f'feedback_{step_id}'] = sm.get_context(f'feedback_{step_id}', None) is not None
            st.json({
                'answers': doubt_progress,
                'feedbacks': feedback_progress,
                'current_feedback_visible': sm.is_showing_feedback(),
                'current_feedback_content': sm.get_current_feedback()[:50] + '...' if len(sm.get_current_feedback()) > 50 else sm.get_current_feedback()
            })
        
        with col2:
            st.write("**系统状态:**")
            st.json({
                'debug_mode': state_summary['show_debug'],
                'modal_visible': state_summary['show_challenge_modal'],
                'case_cached': state_summary['has_case_obj_cache'],
                'ai_initialized': state_summary['ai_engine_initialized']
            })
            
            st.write("**AI引擎状态:**")
            if sm.ai_engine:
                debug_info = sm.ai_engine.get_debug_info()
                st.json({
                    'is_initialized': debug_info['is_initialized'],
                    'current_model': debug_info['current_model'],
                    'error': debug_info['error_message']
                })
        
        st.write("**上下文数据:**")
        context = sm.get_full_context()
        if context:
            # 隐藏敏感信息，只显示键
            context_summary = {k: f"<{type(v).__name__}>" if len(str(v)) > 100 else v for k, v in context.items()}
            st.json(context_summary)
        else:
            st.write("空")
        
        # 调试操作
        st.write("### 调试操作")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 重置所有状态"):
                sm.reset_all()
        
        with col2:
            if st.button("📊 输出完整日志"):
                st.code(f"完整状态: {state_summary}")
        
        with col3:
            if st.button("🧪 测试AI引擎"):
                with st.spinner("测试中..."):
                    result = sm.ai_engine._generate("请回答'AI引擎正常'")
                    if result.get("success"):
                        st.success(f"✅ AI测试成功: {result.get('content', '')}")
                    else:
                        st.error(f"❌ AI测试失败: {result.get('error_message', '未知错误')}")
                        st.json(result.get("debug_info", {}))
        
        with col4:
            if st.button("🎯 跳到第三幕"):
                if sm.get_current_case_id():
                    sm.current_state.act_num = 3
                    sm.current_state.sub_stage = 0
                    st.rerun()
                else:
                    st.error("请先选择一个案例")
        
        # CXO-03: 转场效果测试 - 直接实现，不依赖缺失的方法
        st.subheader("🎬 转场效果测试")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("预览 1→2 转场", key="preview_1_to_2"):
                if ENHANCED_FEATURES_AVAILABLE:
                    TransitionManager.show_transition(1, 2)
                else:
                    st.info("转场功能暂不可用")
        
        with col2:
            if st.button("预览 2→3 转场", key="preview_2_to_3"):
                if ENHANCED_FEATURES_AVAILABLE:
                    TransitionManager.show_transition(2, 3)
                else:
                    st.info("转场功能暂不可用")
        
        with col3:
            if st.button("预览 3→4 转场", key="preview_3_to_4"):
                if ENHANCED_FEATURES_AVAILABLE:
                    TransitionManager.show_transition(3, 4)
                else:
                    st.info("转场功能暂不可用")
        
        # CXO-04: 解锁状态控制
        st.subheader("🔓 解锁状态控制")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔒 锁定工具", key="lock_tool_debug"):
                if hasattr(sm, 'reset_tool_unlock_status'):
                    sm.reset_tool_unlock_status()
                    st.success("工具已锁定")
                else:
                    if 'tool_unlocked' in st.session_state:
                        del st.session_state.tool_unlocked
                    st.success("工具已锁定")
        with col2:
            if st.button("🔓 解锁工具", key="unlock_tool_debug"):
                if hasattr(sm, 'unlock_tool'):
                    sm.unlock_tool()
                    st.success("工具已解锁")
                else:
                    st.session_state.tool_unlocked = True
                    st.success("工具已解锁")
        
        # 显示当前解锁状态
        is_unlocked = st.session_state.get('tool_unlocked', False)
        st.write(f"当前解锁状态: {'🔓 已解锁' if is_unlocked else '🔒 已锁定'}")

# =============================================================================
# MAIN APPLICATION - v4.1重构版本
# =============================================================================

def main():
    """主应用程序入口 - v4.1重构版本"""
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 注入高级CSS样式
    inject_premium_css()
    
    # 获取状态管理器（自动初始化）
    sm = get_state_manager()
    
    try:
        if sm.is_in_selection_view():
            render_case_selection()
        elif sm.is_in_act_view():
            render_act_view()
        else:
            st.error(f"未知的视图状态: {sm.get_current_view()}")
            sm.go_to_selection()
            
    except Exception as e:
        st.error(f"应用运行时错误: {e}")
        st.error("请尝试刷新页面或联系技术支持")
        
        if st.button("🔄 完全重启应用"):
            sm.reset_all()

if __name__ == "__main__":
    main()
