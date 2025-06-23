# cognitive-blackbox/core/engine.py
# -----------------------------------------------------------------------------
# The AI Engine for the Cognitive Black Box Application
# Version: v4.0 (Genesis Mode - FINAL & CORRECTED v18)
# Author: Hoshino AI PM
# This version corrects the critical IndentationError.
# -----------------------------------------------------------------------------

import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple
import logging
import random

logging.basicConfig(level=logging.INFO)

class AIEngine:
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.error_message = None
        self._initialize()

    def _initialize(self):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("API Key is missing in st.secrets.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            self.is_initialized = True
            logging.info("AI Engine initialized successfully.")
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {e}"
            logging.error(self.error_message)

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if not self.is_initialized:
            return self.error_message, False
        try:
            safety_settings = [{'category': c, 'threshold': 'BLOCK_NONE'} for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']]
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            if response.parts:
                return response.text, True
            else:
                feedback = response.prompt_feedback
                reason = feedback.block_reason if hasattr(feedback, 'block_reason') else 'Unknown'
                return f"内容被安全过滤拦截: {reason}", False
        except Exception as e:
            logging.error(f"API Call Failed: {e}")
            return f"API调用异常: {e}", False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            fallbacks = ["你真的确定这个判断是基于事实而非情感吗？", "从另一个角度看，这个决策最大的风险可能是什么？"]
            return random.choice(fallbacks)
        
        prompt = f"""你是一位资深的金融风险分析师。一位投资者对麦道夫投资机会选择了“{context.get('act1_choice', '未知选择')}”。请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。要求: 专业且尖锐, 直击要害, 避免说教。"""
        question, success = self._generate(prompt)
        return question if success else "你真的确定这个判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            return self._get_fallback_tool(context)
        
        prompt = f"""请为用户“{context.get("user_name", "用户")}”创建一个光环效应免疫工具。用户信息: 姓名: {context.get("user_name", "用户")}, 决策原则: {context.get("user_principle", "理性决策")}, 麦道夫案例选择: {context.get("act1_choice", "未记录")}。请生成包含以下内容的Markdown格式工具: 1. 个人化欢迎语(包含姓名) 2. 3-4条决策检查清单 3. 光环效应预警信号 4. 紧急刹车机制。要求: 实用、简洁、200-300字。"""
        tool, success = self._generate(prompt)
        return tool if success else self._get_fallback_tool(context)
    
    def _get_fallback_tool(self, context: Dict[str, Any]) -> str:
        user_name = context.get('user_name', '您')
        return f"""## 🛡️ {user_name}的光环效应免疫系统
### 决策检查清单
- [ ] **权威分离法**: 区分职位权威vs专业权威
- [ ] **透明度测试**: 所有信息是否完全透明？
- [ ] **独立验证**: 是否有真正独立的第三方证实？
- [ ] **反向思维**: 去除光环后我还会做同样决策吗？
### ⚠️ 预警信号
- 过分强调权威身份而非具体能力
- 信息不透明或"商业机密"
- 群体从众压力
### 🚨 紧急刹车机制
**出现任意两个预警信号时，立即暂停决策，寻求独立专业意见。**"""
