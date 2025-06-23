# presentation/app.py
# 在原有代码基础上添加调试功能
# 版本: v3.3 + DEBUG_ENHANCEMENT

import streamlit as st
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# =============================================================================
# PROJECT SETUP & IMPORTS (保持原有结构)
# =============================================================================

def setup_project_paths():
    """健壮的项目路径设置"""
    current_file = Path(__file__)
    
    possible_roots = [
        current_file.parent.parent,  # 标准结构: presentation/app.py -> project_root
        current_file.parent,         # 扁平结构: app.py -> project_root  
        Path.cwd(),                  # 当前工作目录
    ]
    
    for root in possible_roots:
        config_path = root / "config" / "cases"
        if config_path.exists():
            print(f"✅ 项目根目录确定: {root}")
            return root
    
    print("⚠️ 警告: 无法找到config/cases目录，使用当前目录")
    return Path.cwd()

PROJECT_ROOT = setup_project_paths()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 安全导入核心模块
try:
    from core.models import Act, Case
    from core.engine import AIEngine
    from config.settings import AppConfig
    print("✅ 核心模块导入成功")
except ImportError as e:
    st.error(f"🚨 核心模块导入失败: {e}")
    st.error("请检查项目结构和依赖项")
    st.stop()

# =============================================================================
# 新增：调试功能
# =============================================================================

def render_debug_panel():
    """新增：调试面板 - 显示AI引擎的详细状态"""
    if not st.session_state.get('show_debug', False):
        return
    
    with st.expander("🔧 AI调试面板", expanded=True):
        st.write("### AI引擎状态诊断")
        
        if 'ai_engine' in st.session_state:
            engine = st.session_state.ai_engine
            debug_info = engine.get_debug_info()
            
            # 显示初始化状态
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**初始化状态:**")
                if debug_info['is_initialized']:
                    st.success("✅ AI引擎已初始化")
                else:
                    st.error("❌ AI引擎初始化失败")
                    
                if debug_info['error_message']:
                    st.error(f"错误: {debug_info['error_message']}")
            
            with col2:
                st.write("**模型信息:**")
                st.code(f"模型类型: {debug_info['model_type']}")
            
            # 显示详细的初始化信息
            if 'initialization' in debug_info:
                st.write("**初始化详情:**")
                st.json(debug_info['initialization'])
            
            # 显示最后一次API调用的详细信息
            if 'last_call' in debug_info['initialization']:
                st.write("**最后一次API调用详情:**")
                st.json(debug_info['initialization']['last_call'])
        
        else:
            st.warning("AI引擎未创建")
        
        # 新增：手动测试AI调用
        st.write("### 手动测试AI调用")
        test_prompt = st.text_input("输入测试提示词:", value="请说'Hello World'")
        
        if st.button("🧪 测试AI调用"):
            if 'ai_engine' in st.session_state:
                with st.spinner("测试中..."):
                    result, success = st.session_state.ai_engine._generate(test_prompt)
                    
                if success:
                    st.success(f"✅ 测试成功: {result}")
                else:
                    st.error(f"❌ 测试失败: {result}")
                
                # 显示这次测试的调试信息
                debug_info = st.session_state.ai_engine.get_debug_info()
                if 'last_call' in debug_info['initialization']:
                    st.write("**本次测试的调试信息:**")
                    st.json(debug_info['initialization']['last_call'])
            else:
                st.error("AI引擎不可用")

# =============================================================================
# CONTENT LOADING SYSTEM (保持原有结构，添加调试)
# =============================================================================

class ContentLoader:
    """内容加载器 - 负责加载和解析案例内容"""
    
    @staticmethod
    @st.cache_data
    def load_case(case_id: str) -> Optional[Case]:
        """加载并解析单个案例 - 原有逻辑保持不变"""
        try:
            print(f"🔄 开始加载案例: {case_id}")
            
            base_path = PROJECT_ROOT / "config" / "cases"
            case_json_path = base_path / f"{case_id}.json"
            
            if not case_json_path.exists():
                print(f"❌ 案例配置文件不存在: {case_json_path}")
                return None
            
            with open(case_json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                print(f"✅ 案例元数据加载成功: {metadata.get('title')}")
            
            script_file_path = base_path / metadata['script_file']
            if not script_file_path.exists():
                print(f"❌ 脚本文件不存在: {script_file_path}")
                return None
            
            with open(script_file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
                print(f"✅ 脚本内容加载成功: {len(script_content)}字符")
            
            # 使用原有的解析逻辑
            acts = ContentLoader._parse_script_content(script_content)
            print(f"✅ 脚本解析完成: {len(acts)}个幕")
            
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
            
            print(f"✅ 案例对象创建成功: {case.title}")
            return case
            
        except Exception as e:
            print(f"❌ 加载案例失败: {e}")
            st.error(f"加载案例 '{case_id}' 时出错: {e}")
            return None
    
    @staticmethod
    def _parse_script_content(content: str) -> Dict[int, Act]:
        """保持原有的解析逻辑"""
        acts = {}
        
        separator = "--- ACT_SEPARATOR ---"
        chunks = content.split(separator)
        
        print(f"🔍 脚本分割结果: {len(chunks)}个片段")
        
        titles = ["决策代入", "现实击穿", "框架重构", "能力武装"]
        roles = ["host", "investor", "mentor", "assistant"]
        
        # 关键修复: 跳过第一个片段(通常是引言)，从第二个片段开始处理
        act_number = 1
        for i in range(1, len(chunks)):  # 从索引1开始，跳过chunks[0]
            chunk = chunks[i].strip()
            
            if not chunk:  # 跳过空片段
                continue
            
            acts[act_number] = Act(
                act_id=act_number,
                title=titles[act_number-1] if act_number-1 < len(titles) else f"第 {act_number} 幕",
                role_id=roles[act_number-1] if act_number-1 < len(roles) else "assistant",
                content=chunk
            )
            
            print(f"✅ 第{act_number}幕解析完成: {len(chunk)}字符")
            act_number += 1
        
        return acts
    
    @staticmethod
    @st.cache_data
    def get_all_cases() -> List[Dict]:
        """获取所有可用案例的元数据 - 保持原有逻辑"""
        cases = []
        cases_dir = PROJECT_ROOT / "config" / "cases"
        
        if not cases_dir.exists():
            print("❌ 案例目录不存在")
            return []
        
        for case_file in sorted(cases_dir.glob("*.json")):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if 'id' in metadata and 'title' in metadata:
                        cases.append(metadata)
                        print(f"✅ 发现案例: {metadata['title']}")
            except Exception as e:
                print(f"⚠️ 跳过损坏的案例文件: {case_file.name} - {e}")
        
        print(f"✅ 总共加载了 {len(cases)} 个案例")
        return cases

# =============================================================================
# STATE MANAGEMENT SYSTEM (保持原有结构)
# =============================================================================

class StateManager:
    """状态管理器 - 负责管理所有session_state"""
    
    @staticmethod
    def initialize():
        """初始化所有必要的session_state变量"""
        if 'view' not in st.session_state:
            st.session_state.view = "selection"
            print("🔄 初始化视图状态: selection")
        
        if 'case_id' not in st.session_state:
            st.session_state.case_id = None
            print("🔄 初始化案例ID: None")
        
        if 'case_obj' not in st.session_state:
            st.session_state.case_obj = None
            print("🔄 初始化案例对象: None")
        
        if 'act_num' not in st.session_state:
            st.session_state.act_num = 1
            print("🔄 初始化幕数: 1")
        
        if 'context' not in st.session_state:
            st.session_state.context = {}
            print("🔄 初始化上下文: {}")
        
        if 'ai_engine' not in st.session_state:
            st.session_state.ai_engine = AIEngine()
            print("🔄 初始化AI引擎")
        
        # 新增：调试模式开关
        if 'show_debug' not in st.session_state:
            st.session_state.show_debug = False
    
    @staticmethod
    def switch_to_case(case_id: str):
        """切换到指定案例的第一幕"""
        st.session_state.view = "act"
        st.session_state.case_id = case_id
        st.session_state.act_num = 1
        st.session_state.context = {}
        print(f"🔄 切换到案例: {case_id}")
    
    @staticmethod
    def switch_to_selection():
        """返回案例选择页面"""
        st.session_state.view = "selection"
        st.session_state.case_id = None
        st.session_state.case_obj = None
        st.session_state.act_num = 1
        st.session_state.context = {}
        print("🔄 返回案例选择")
    
    @staticmethod
    def next_act():
        """进入下一幕"""
        st.session_state.act_num += 1
        print(f"🔄 进入第{st.session_state.act_num}幕")
    
    @staticmethod
    def prev_act():
        """返回上一幕"""
        if st.session_state.act_num > 1:
            st.session_state.act_num -= 1
            print(f"🔄 返回第{st.session_state.act_num}幕")

# =============================================================================
# VIEW RENDERERS (保持原有结构，添加调试功能)
# =============================================================================

def render_case_selection():
    """渲染案例选择页面 - 保持原有逻辑"""
    # 新增：调试开关
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"{AppConfig.PAGE_ICON} {AppConfig.PAGE_TITLE}")
    with col2:
        if st.checkbox("🔧 调试模式", key="debug_toggle"):
            st.session_state.show_debug = True
        else:
            st.session_state.show_debug = False
    
    # 显示调试面板
    render_debug_panel()
    
    st.markdown("### 🎯 我们不教授知识，我们架构智慧")
    st.markdown("选择一个世界级失败案例，开启你的认知升级之旅。")
    
    cases = ContentLoader.get_all_cases()
    
    if not cases:
        st.error("❌ 没有找到可用的案例")
        return
    
    # 保持原有的案例显示逻辑
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
                StateManager.switch_to_case(case_data.get('id'))
                st.rerun()

def render_act_view():
    """渲染幕场景页面 - 保持原有逻辑，添加调试"""
    # 调试面板
    render_debug_panel()
    
    # 确保案例对象已加载
    if st.session_state.case_obj is None or st.session_state.case_obj.id != st.session_state.case_id:
        with st.spinner("📚 加载案例内容..."):
            st.session_state.case_obj = ContentLoader.load_case(st.session_state.case_id)
    
    case = st.session_state.case_obj
    act_num = st.session_state.act_num
    
    if not case:
        st.error("❌ 无法加载案例内容")
        if st.button("🔙 返回案例选择"):
            StateManager.switch_to_selection()
            st.rerun()
        return
    
    if act_num not in case.acts:
        st.error(f"❌ 第{act_num}幕不存在")
        if st.button("🔙 返回案例选择"):
            StateManager.switch_to_selection()
            st.rerun()
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
    
    # 特定幕的交互逻辑 - 保持原有逻辑
    if act_num == 1:
        render_act1_interaction()
    elif act_num == 2:
        render_act2_interaction()
    elif act_num == 4:
        render_act4_interaction()
    
    # 导航按钮
    render_navigation(case, act_num)

def render_act1_interaction():
    """第一幕的交互逻辑 - 保持原有"""
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
        st.session_state.context['act1_choice'] = choice
        print(f"✅ 用户选择: {choice}")
        StateManager.next_act()
        st.rerun()

def render_act2_interaction():
    """第二幕的AI质疑逻辑 - 保持原有，添加调试信息"""
    if 'ai_question' not in st.session_state.context:
        with st.spinner("🤖 AI正在分析您的决策..."):
            try:
                # 新增：在调试模式下显示调用前状态
                if st.session_state.get('show_debug'):
                    st.info("🔧 调试：开始调用generate_personalized_question")
                
                question = st.session_state.ai_engine.generate_personalized_question(
                    st.session_state.context
                )
                st.session_state.context['ai_question'] = question
                print(f"✅ AI质疑生成成功: {question}")
                
                # 新增：在调试模式下显示成功信息
                if st.session_state.get('show_debug'):
                    st.success(f"🔧 调试：AI调用成功，返回: {question}")
                
            except Exception as e:
                print(f"❌ AI质疑生成失败: {e}")
                st.session_state.context['ai_question'] = "你确定这个决策是基于理性分析的吗？"
                
                # 新增：在调试模式下显示错误信息
                if st.session_state.get('show_debug'):
                    st.error(f"🔧 调试：AI调用失败: {e}")
    
    question = st.session_state.context.get('ai_question')
    st.warning(f"**🔥 AI质疑:** {question}")
    
    if st.button("💭 我需要重新思考", key="rethink_button"):
        st.info("很好！重新思考是智慧决策者的标志。继续下一幕了解更多...")

def render_act4_interaction():
    """第四幕的工具生成逻辑 - 保持原有，添加调试信息"""
    with st.form("personalized_tool_form"):
        st.subheader("🛠️ 个性化决策工具生成")
        
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
        
        submitted = st.form_submit_button("🚀 生成我的专属工具", type="primary")
        
        if submitted:
            if not name.strip():
                st.error("请输入您的姓名")
            else:
                st.session_state.context['user_name'] = name.strip()
                st.session_state.context['user_principle'] = principle.strip()
                
                with st.spinner("🤖 AI导师正在为您定制决策免疫系统..."):
                    try:
                        # 新增：在调试模式下显示调用前状态
                        if st.session_state.get('show_debug'):
                            st.info("🔧 调试：开始调用generate_personalized_tool")
                        
                        tool = st.session_state.ai_engine.generate_personalized_tool(
                            st.session_state.context
                        )
                        st.session_state.context['personalized_tool'] = tool
                        print(f"✅ 个性化工具生成成功")
                        
                        # 新增：在调试模式下显示成功信息
                        if st.session_state.get('show_debug'):
                            st.success(f"🔧 调试：AI工具生成成功，长度: {len(tool)}字符")
                        
                    except Exception as e:
                        print(f"❌ 个性化工具生成失败: {e}")
                        st.error(f"工具生成失败: {e}")
                        
                        # 新增：在调试模式下显示错误信息
                        if st.session_state.get('show_debug'):
                            st.error(f"🔧 调试：AI工具生成失败: {e}")
    
    # 显示生成的工具
    if 'personalized_tool' in st.session_state.context:
        st.markdown("---")
        st.subheader(f"🎯 专属决策免疫系统")
        tool_content = st.session_state.context['personalized_tool']
        st.markdown(tool_content, unsafe_allow_html=True)

def render_navigation(case: Case, act_num: int):
    """渲染导航按钮 - 保持原有"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if act_num > 1:
            if st.button("⬅️ 上一幕", key="prev_act_btn"):
                StateManager.prev_act()
                st.rerun()
    
    with col2:
        if st.button("🏠 返回案例选择", key="back_to_selection_btn"):
            StateManager.switch_to_selection()
            st.rerun()
    
    with col3:
        if act_num < len(case.acts):
            if st.button("➡️ 下一幕", type="primary", key="next_act_btn"):
                StateManager.next_act()
                st.rerun()
        elif act_num == len(case.acts):
            if st.button("🎉 完成体验", type="primary", key="complete_experience_btn"):
                st.balloons()
                st.success("🎊 恭喜完成认知升级！")
                StateManager.switch_to_selection()
                st.rerun()

# =============================================================================
# MAIN APPLICATION (保持原有)
# =============================================================================

def main():
    """主应用程序入口"""
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .stProgress .st-bo {
        background-color: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    StateManager.initialize()
    
    try:
        if st.session_state.view == "selection":
            render_case_selection()
        elif st.session_state.view == "act":
            render_act_view()
        else:
            st.error(f"未知的视图状态: {st.session_state.view}")
            StateManager.switch_to_selection()
            st.rerun()
            
    except Exception as e:
        st.error(f"应用运行时错误: {e}")
        print(f"❌ 应用错误: {e}")
        if st.button("🔄 重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            StateManager.initialize()
            st.rerun()

if __name__ == "__main__":
    main()
