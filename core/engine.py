# core/engine.py
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple

class AIEngine:
    def __init__(self):
        self.model = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("API Key not found in st.secrets")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        except (AttributeError, KeyError, ValueError) as e:
            print(f"AI Engine Init Warning: {e}. Running in NO-AI mode.")

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if not self.model: return "AI引擎未激活，请检查API密钥。", False
        try:
            response = self.model.generate_content(prompt, safety_settings={'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'})
            return response.text, True
        except Exception as e: return f"AI响应生成时发生错误: {e}", False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        prompt = f"你是一位犀利的华尔街对冲基金经理。一个客户对“麦道夫”机会做出了“{context.get('act1_choice', '一个判断')}”的决策。请用一句简短、尖锐、直击要害的话来挑战他。"
        question, success = self._generate(prompt)
        return question if success else "你真的确定你的判断是基于事实，而不是希望吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        prompt = f"你是一位世界级的认知科学家。一个名叫“{context.get('user_name', '用户')}”的决策者学习了“麦道夫案例”，他的核心原则是：“{context.get('user_principle', '未提供')}”，第一幕决策是：“{context.get('act1_choice', '未记录')}”。请为他生成一个专属的“光环效应免疫系统”决策工具，必须包含一条针对他个人原则的独特建议。请使用Markdown格式化输出。"
        tool, success = self._generate(prompt)
        return tool if success else "抱歉，无法生成您的专属工具。"
