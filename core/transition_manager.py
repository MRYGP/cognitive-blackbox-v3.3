# config/transitions.py - 叙事转场配置
# 电影级别的过场文本，营造沉浸式体验

import streamlit as st
import time
from typing import Dict, Any

# 需要从新创建的配置文件导入
try:
    from config.transitions import TRANSITION_TEXTS, TRANSITION_STYLE
except ImportError:
    # Fallback 配置，如果配置文件导入失败
    TRANSITION_TEXTS = {
        "1_to_2": {
            "text": "⏳ 现实的冰水，即将浇下...",
            "subtitle": "第二幕：现实击穿",
            "duration": 2.5
        },
        "2_to_3": {
            "text": "🔨 击碎旧地图，是为了绘制新大陆...",
            "subtitle": "第三幕：认知重构", 
            "duration": 2.5
        },
        "3_to_4": {
            "text": "⚡ 理论已成，开始铸造你的武器...",
            "subtitle": "第四幕：智慧武装",
            "duration": 2.5
        }
    }
    
    TRANSITION_STYLE = """<style>
    .transition-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 60vh;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    .transition-main-text {
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        animation: fadeInUp 1s ease-out forwards;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>"""

class TransitionManager:
    """电影级转场效果管理器"""
    
    @staticmethod
    def show_transition(from_act: int, to_act: int) -> None:
        """显示转场动画"""
        transition_key = f"{from_act}_to_{to_act}"
        transition_config = TRANSITION_TEXTS.get(transition_key, {
            "text": "✨ 故事继续...",
            "subtitle": f"第{to_act}幕",
            "duration": 2.0
        })
        
        # 清空当前页面
        main_container = st.empty()
        
        with main_container.container():
            # 注入CSS样式
            st.markdown(TRANSITION_STYLE, unsafe_allow_html=True)
            
            # 渲染转场界面
            st.markdown(f"""
            <div class="transition-container">
                <div class="transition-main-text">{transition_config['text']}</div>
                <div class="transition-subtitle">{transition_config['subtitle']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 等待指定时间
            time.sleep(transition_config['duration'])
        
        # 清空转场内容
        main_container.empty()

# 文件末尾必须有这个类定义，确保可以被导入
