# core/value_confirmation.py - 价值确认体验管理器
# 负责第四幕的"解锁宝箱"体验

import streamlit as st
from typing import Dict, Any

class ValueConfirmationManager:
    """价值确认体验管理器 - 创造"解锁宝箱"的成就感"""
    
    @staticmethod
    def get_unlock_styles() -> str:
        """获取解锁体验的CSS样式"""
        return """
        <style>
        .tool-preview-locked {
            filter: blur(8px);
            transition: filter 0.5s ease;
            opacity: 0.6;
            pointer-events: none;
            user-select: none;
        }
        
        .tool-preview-unlocked {
            filter: none;
            transition: filter 0.5s ease;
            opacity: 1;
        }
        
        .unlock-overlay {
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            color: white;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .unlock-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .unlock-description {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        
        .unlock-button {
            background: linear-gradient(45deg, #FFA726, #FF7043);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 167, 38, 0.4);
        }
        
        .unlock-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 167, 38, 0.6);
        }
        
        .value-badge {
            display: inline-block;
            background: linear-gradient(45deg, #FFD54F, #FFC107);
            color: #333;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin: 0 8px;
            box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
        }
        
        .achievement-animation {
            animation: achievementPulse 2s ease-in-out infinite;
        }
        
        @keyframes achievementPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .sparkle-effect {
            position: relative;
            overflow: hidden;
        }
        
        .sparkle-effect::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
            animation: sparkle 3s ease-in-out infinite;
        }
        
        @keyframes sparkle {
            0%, 100% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            50% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        </style>
        """
    
    @staticmethod
    def show_locked_tool_preview(tool_content: str, context: Dict[str, Any]) -> bool:
        """
        显示锁定状态的工具预览
        
        Args:
            tool_content: 生成的工具内容
            context: 用户上下文信息
            
        Returns:
            bool: 是否点击了解锁按钮
        """
        # 注入样式
        st.markdown(ValueConfirmationManager.get_unlock_styles(), unsafe_allow_html=True)
        
        # 获取用户信息
        user_name = context.get('user_name', '您')
        case_id = context.get('case_id', 'unknown')
        
        # 根据案例确定价值描述
        value_descriptions = {
            'madoff': {
                'framework': '四维独立验证矩阵',
                'benefit': '权威陷阱免疫能力',
                'description': '一套完整的投资决策防护系统，让您永远不会再被"权威光环"所迷惑。'
            },
            'lehman': {
                'framework': 'DOUBT思维模型', 
                'benefit': '确认偏误破解术',
                'description': '五步骤思维框架，训练您主动寻找反对证据的能力，避免经验主义陷阱。'
            },
            'ltcm': {
                'framework': 'RISK思维模型',
                'benefit': '过度自信校正器',
                'description': '概率思维训练系统，让您在面对复杂决策时保持清醒的不确定性意识。'
            }
        }
        
        case_info = value_descriptions.get(case_id, {
            'framework': '认知免疫系统',
            'benefit': '决策智慧升级',
            'description': '专属的认知偏误防护工具，提升您的决策质量和思维清晰度。'
        })
        
        # 显示解锁界面
        st.markdown(f"""
        <div class="unlock-overlay sparkle-effect achievement-animation">
            <div class="unlock-title">🎉 恭喜 {user_name}！您的专属智慧已准备就绪</div>
            <div class="unlock-description">
                您刚刚完成了一场深度的认知训练，现在已获得：<br>
                <span class="value-badge">{case_info['framework']}</span>
                <span class="value-badge">{case_info['benefit']}</span><br><br>
                {case_info['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示模糊的工具预览
        with st.container():
            st.markdown('<div class="tool-preview-locked">', unsafe_allow_html=True)
            
            # 显示工具的前几行作为预览
            preview_lines = tool_content.split('\n')[:8]
            preview_text = '\n'.join(preview_lines) + '\n\n*[内容已模糊处理，点击解锁查看完整内容]*'
            
            st.markdown(preview_text)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 解锁按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            unlock_clicked = st.button(
                "🗝️ 解锁我的专属智慧", 
                key="unlock_tool_button",
                help="点击获取您的完整认知免疫系统"
            )
        
        return unlock_clicked
    
    @staticmethod
    def show_unlocked_tool(tool_content: str, context: Dict[str, Any]) -> None:
        """
        显示已解锁的工具内容
        
        Args:
            tool_content: 生成的工具内容
            context: 用户上下文信息
        """
        # 注入样式
        st.markdown(ValueConfirmationManager.get_unlock_styles(), unsafe_allow_html=True)
        
        # 显示解锁成功的庆祝效果
        st.balloons()  # Streamlit内置的庆祝动画
        
        st.success("🎊 解锁成功！您的专属智慧现已激活！")
        
        # 显示完整工具内容
        with st.container():
            st.markdown('<div class="tool-preview-unlocked">', unsafe_allow_html=True)
            st.markdown(tool_content)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 提供下载或分享选项
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 下载我的认知免疫系统",
                data=tool_content,
                file_name=f"认知免疫系统_{context.get('user_name', 'user')}.md",
                mime="text/markdown",
                help="保存到本地，随时查阅"
            )
        
        with col2:
            if st.button("🔄 体验其他案例", key="try_other_cases"):
                from core.state_manager import get_state_manager
                sm = get_state_manager()
                sm.go_to_case_selection()
    
    @staticmethod
    def render_act4_with_unlock_experience(tool_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        渲染带有解锁体验的第四幕
        
        Args:
            tool_result: AI生成的工具结果
            context: 用户上下文信息
        """
        from core.state_manager import get_state_manager
        sm = get_state_manager()
        
        # 获取工具内容
        tool_content = tool_result.get('content', '') or tool_result.get('fallback_content', '')
        
        if not tool_content:
            st.error("工具生成失败，请重试")
            return
        
        # 检查是否已解锁
        if sm.is_tool_unlocked():
            # 已解锁，显示完整内容
            ValueConfirmationManager.show_unlocked_tool(tool_content, context)
        else:
            # 未解锁，显示锁定预览
            unlock_clicked = ValueConfirmationManager.show_locked_tool_preview(tool_content, context)
            
            if unlock_clicked:
                # 用户点击了解锁按钮
                sm.unlock_tool()
                st.rerun()  # 重新渲染页面以显示解锁内容
