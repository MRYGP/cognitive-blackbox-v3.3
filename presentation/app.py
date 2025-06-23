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
except ImportError as e:
    st.error(f"🚨 核心模块导入失败: {e}")
    st.stop()

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
    """渲染案例选择页面 - v4.1重构版本"""
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
        render_act2_interaction_premium()
    elif act_num == 3:
        render_act3_interaction_doubt_model()  # 新增：第三幕DOUBT模型
    elif act_num == 4:
        render_act4_interaction_premium()
    
    # 导航按钮
    render_navigation(case, act_num)

# =============================================================================
# ACT INTERACTION FUNCTIONS - v4.1重构版本
# =============================================================================

def render_act1_interaction():
    """第一幕的交互逻辑 - v4.1重构版本"""
    sm = get_state_manager()
    
    st.subheader("🤔 您的决策是？")
    
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
    
    if st.button("✅ 确认我的决策", type="primary", key="confirm_act1_choice"):
        # 使用新的状态管理
        sm.update_context('act1_choice', choice)
        sm.advance_to_next_act()

def render_act2_interaction_premium():
    """第二幕的AI质疑逻辑 - v4.1重构版本"""
    sm = get_state_manager()
    
    if not sm.get_context('ai_question'):
        with st.spinner("🤖 Damien正在分析您的决策逻辑..."):
            try:
                question = sm.ai_engine.generate_personalized_question(sm.get_full_context())
                sm.update_context('ai_question', question)
                sm.show_challenge_modal()
            except Exception as e:
                sm.update_context('ai_question', "这个'完美'的机会，最让你不安的是什么？")
                sm.show_challenge_modal()
    
    question = sm.get_context('ai_question')
    
    if sm.is_challenge_modal_visible():
        show_ai_challenge_modal(question)
        
        if st.button("💭 关闭对话框，继续思考", key="close_modal_btn"):
            sm.hide_challenge_modal()
            st.rerun()
    else:
        st.success("✅ 您已接受了Damien的挑战！继续您的认知之旅...")
        st.info(f"🔄 回顾质疑：{question}")

def render_act3_interaction_doubt_model():
    """第三幕的DOUBT模型互动 - v4.1全新实现"""
    sm = get_state_manager()
    
    # DOUBT模型的5个步骤
    doubt_steps = [
        {
            "id": "D", 
            "title": "魔鬼代言人 (Devil's Advocate)",
            "question": "请列出3个反对您第一幕决策的理由：",
            "placeholder": "例如：1. 历史业绩可能是伪造的...\n2. 投资策略过于保密...\n3. 回报率在统计上不可能..."
        },
        {
            "id": "O", 
            "title": "反向证据 (Opposite Evidence)",
            "question": "如果这是一个陷阱，您会寻找哪些警告信号？",
            "placeholder": "例如：信息不透明、回避具体问题、缺乏独立审计..."
        },
        {
            "id": "U", 
            "title": "不确定性地图 (Uncertainty Mapping)",
            "question": "在这个决策中，您最不确定的3个要素是什么？",
            "placeholder": "例如：真实的风险评级、管理层能力、市场环境变化..."
        },
        {
            "id": "B", 
            "title": "基础概率 (Base Rate)",
            "question": "类似的投资机会，历史上的失败率大约是多少？",
            "placeholder": "例如：高收益投资的90%最终失败、新基金的75%在5年内关闭..."
        },
        {
            "id": "T", 
            "title": "时间视野 (Time Horizon)",
            "question": "如果这个决策在5年后被证明是错误的，您希望当时的自己多考虑什么？",
            "placeholder": "例如：更长期的市场周期、黑天鹅事件、团队稳定性..."
        }
    ]
    
    current_stage = sm.get_sub_stage()
    
    st.markdown('<div class="doubt-progress">', unsafe_allow_html=True)
    st.markdown(f"### 🛡️ DOUBT思维模型 - 智慧武器库")
    st.markdown(f"**解锁进度: {current_stage}/5** | 构建您的认知防护盾")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示已完成的步骤
    for i in range(current_stage):
        step = doubt_steps[i]
        answer = sm.get_context(f'doubt_{step["id"]}', '未记录')
        
        st.markdown('<div class="doubt-completed">', unsafe_allow_html=True)
        with st.expander(f"✅ {step['id']} - {step['title']} (已完成)", expanded=False):
            st.write(f"**您的反思:** {answer}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 当前步骤
    if current_stage < len(doubt_steps):
        current_step = doubt_steps[current_stage]
        
        st.markdown("---")
        st.markdown('<div class="doubt-step">', unsafe_allow_html=True)
        st.subheader(f"🎯 步骤 {current_stage + 1}: {current_step['id']} - {current_step['title']}")
        
        with st.form(f"doubt_step_{current_step['id']}"):
            st.markdown(current_step['question'])
            
            answer = st.text_area(
                "您的深度思考:",
                placeholder=current_step['placeholder'],
                height=120,
                key=f"doubt_answer_{current_step['id']}"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("💡 **提示**: 请诚实面对自己的认知盲点，这是构建智慧防护盾的关键。")
            with col2:
                submitted = st.form_submit_button(f"🔒 锁定 {current_step['id']} 符文", type="primary")
            
            if submitted and answer.strip():
                sm.update_context(f'doubt_{current_step["id"]}', answer.strip())
                sm.advance_sub_stage()
                st.success(f"✅ {current_step['title']} 符文已解锁！")
                time.sleep(1)  # 短暂停顿增强仪式感
                st.rerun()
            elif submitted:
                st.error("请输入您的深度思考再继续")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 完成所有步骤后的总结
    if current_stage >= len(doubt_steps):
        st.markdown("---")
        st.balloons()  # 庆祝效果
        st.success("🎉 恭喜！您已经成功构建了完整的DOUBT认知防护盾！")
        
        with st.expander("🛡️ 您的DOUBT思维武器库总览", expanded=True):
            st.markdown("### 🏆 您的认知升级成果")
            
            for step in doubt_steps:
                answer = sm.get_context(f'doubt_{step["id"]}', '未记录')
                st.markdown(f"#### {step['id']} - {step['title']}")
                st.info(answer)
                st.markdown("---")
        
        st.markdown("### 🚀 恭喜解锁认知新层次！")
        st.markdown("您已经具备了系统性的**反向思维能力**，这将成为您在未来决策中的核心竞争优势。")
        
        if st.button("⚡ 继续前往第四幕：获取专属AI工具", type="primary", key="doubt_complete_btn"):
            sm.advance_to_next_act()

def render_act4_interaction_premium():
    """第四幕的工具生成逻辑 - v4.1重构版本"""
    sm = get_state_manager()
    
    with st.form("personalized_tool_form"):
        st.subheader("🛠️ 个性化决策工具生成")
        st.markdown("**由世界级AI导师Athena为您定制**")
        
        name = st.text_input(
            "您的姓名/昵称", 
            placeholder="请输入您的姓名",
            key="user_name_input"
        )
        
        principle = st.text_area(
            "您的核心决策原则",
            placeholder="例如：我注重数据驱动决策，相信长期价值投资...",
            height=100,
            key="user_principle_input"
        )
        
        submitted = st.form_submit_button("🚀 生成我的专属免疫系统", type="primary")
        
        if submitted:
            if not name.strip():
                st.error("请输入您的姓名")
            else:
                sm.update_context('user_name', name.strip())
                sm.update_context('user_principle', principle.strip())
                
                with st.spinner("🤖 Athena正在为您定制终身决策免疫系统..."):
                    try:
                        tool = sm.ai_engine.generate_personalized_tool(sm.get_full_context())
                        sm.update_context('personalized_tool', tool)
                    except Exception as e:
                        st.error(f"工具生成失败: {e}")
    
    # 使用高级报告渲染器
    if sm.get_context('personalized_tool'):
        st.markdown("---")
        st.subheader("🎯 您的专属认知免疫系统已生成")
        
        tool_content = sm.get_context('personalized_tool')
        user_name = sm.get_context('user_name', '用户')
        
        parse_and_render_premium_report(tool_content, user_name)

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
    """调试面板 - v4.1增强版本"""
    sm = get_state_manager()
    
    if not sm.is_debug_mode():
        return
    
    with st.expander("🔧 v4.1状态管理调试面板", expanded=True):
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
            for step_id in ['D', 'O', 'U', 'B', 'T']:
                doubt_progress[f'doubt_{step_id}'] = sm.get_context(f'doubt_{step_id}', None) is not None
            st.json(doubt_progress)
        
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
                    result, success = sm.ai_engine._generate("请回答'AI引擎正常'")
                    if success:
                        st.success(f"✅ AI测试成功: {result}")
                    else:
                        st.error(f"❌ AI测试失败: {result}")
        
        with col4:
            if st.button("🎯 跳到第三幕"):
                if sm.get_current_case_id():
                    sm.current_state.act_num = 3
                    sm.current_state.sub_stage = 0
                    st.rerun()
                else:
                    st.error("请先选择一个案例")

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
