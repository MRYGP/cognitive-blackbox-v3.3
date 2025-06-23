# cognitive-blackbox/core/engine.py
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple

class AIEngine:
    def __init__(self):
        self.model = None
        self.error_message = None
        # We do NOT initialize here anymore.

    def initialize(self) -> bool:
        """
        [THE FINAL FIX IS HERE] This method is called EXPLICITLY from the main app,
        only when we are sure the Streamlit environment, including secrets, is ready.
        """
        if self.model: # Already initialized
            return True
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                self.error_message = "GEMINI_API_KEY not found in st.secrets."
                return False
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest') # Using a stable version
            self.error_message = None
            return True
        except Exception as e:
            self.error_message = f"AI Engine Init Error: {e}"
            return False

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if not self.model:
            return self.error_message or "AI引擎未初始化。", False
        # ... (The rest of the _generate and other methods from C's version remain the same)
        try:
            safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip(), True
            
            if hasattr(response, 'prompt_feedback') and hasattr(response.prompt_feedback, 'block_reason'):
                return f"内容被安全过滤拦截: {response.prompt_feedback.block_reason}", False
            
            return "AI未返回有效内容。", False
        except Exception as e:
            return f"API调用异常: {e}", False
            
    # --- generate_personalized_question and generate_personalized_tool remain the same as C's final version ---
    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        if not self.model: return "你真的确定这个判断是基于事实而非情感吗？"
        prompt = f"""你是一位资深的金融风险分析师。一位投资者对麦道夫投资机会选择了"{context.get('act1_choice', '未知选择')}"。请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。要求: 专业且尖锐, 直击要害, 避免说教。"""
        question, success = self._generate(prompt)
        return question if success else "从另一个角度看，这个决策最大的风险可能是什么？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        if not self.model: return f"抱歉 {context.get('user_name', '用户')}，AI引擎当前不可用，无法生成您的专属工具。"
        prompt = f"""请为用户"{context.get('user_name', '用户')}"创建一个光环效应免疫工具。用户信息: 姓名: {context.get('user_name', '用户')}, 决策原则: {context.get('user_principle', '理性决策')}, 麦道夫案例选择: {context.get('act1_choice', '未记录')}。请生成包含以下内容的Markdown格式工具: 1. 个人化欢迎语(包含姓名) 2. 3-4条决策检查清单 3. 光环效应预警信号 4. 紧急刹车机制。要求: 实用、简洁、200-300字。"""
        tool, success = self._generate(prompt)
        return tool if success else f"抱歉，无法生成您的专属工具。错误信息：{tool}"
