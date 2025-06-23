# cognitive-blackbox/core/engine.py
# -----------------------------------------------------------------------------
# The AI Engine for the Cognitive Black Box Application
# Version: v3.3 (Genesis Mode - FINAL & CORRECTED v13)
# Author: Hoshino AI PM
# This version includes refined prompts and more robust error parsing to
# handle non-standard AI responses gracefully.
# -----------------------------------------------------------------------------

import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple

class AIEngine:
    def __init__(self):
        self.model = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key: raise ValueError("API Key not found in st.secrets")
            genai.configure(api_key=api_key)
            # Let's stick to a stable, well-tested model for now
            self.model = genai.GenerativeModel('gemini-2.5-pro') 
        except Exception as e:
            print(f"AI Engine Init Warning: {e}. Running in NO-AI mode.")

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if not self.model: return "AI引擎未激活，请检查API密钥。", False
        try:
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            
            # --- THE FINAL FIX IS HERE: Robust Response Parsing ---
            # Sometimes the model might finish for a reason like 'SAFETY'
            # even with BLOCK_NONE. We need to check if there is actual text.
            if response.parts:
                return response.text, True
            # If there are no parts, it means the response was blocked or empty.
            # We can inspect `response.prompt_feedback` for the reason.
            else:
                block_reason = response.prompt_feedback.block_reason
                error_msg = f"AI未能生成内容。原因: {block_reason}"
                return error_msg, False
                
        except Exception as e:
            return f"调用AI API时发生程序错误: {e}", False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        # --- Refined Prompt ---
        # We make the prompt less aggressive to avoid safety filters.
        prompt = f"""
        你是一位经验丰富的投资分析师，正在进行一次友好的压力测试。
        一位客户对一个投资机会（麦道夫案例）做出了“{context.get('act1_choice', '一个判断')}”的初步决策。
        请用一个有启发性的、引导思考的问题，来帮助他审视这个决策背后可能存在的思维盲点。问题要专业，但语气要具建设性。
        """
        question, success = self._generate(prompt)
        return question if success else "从另一个角度看，这个决策最大的风险可能是什么？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        # --- Refined Prompt ---
        # We give a more structured instruction to the AI.
        prompt = f"""
        你是一位世界级的认知科学家和决策教练。
        你的客户，名叫“{context.get('user_name', '用户')}”，刚刚学习了“麦道夫案例”，并总结出自己的核心决策原则：“{context.get('user_principle', '未提供')}”。
        他/她在案例第一幕的初步决策是：“{context.get('act1_choice', '未记录')}”。

        你的任务是，为这位客户生成一份专属的《决策免疫系统》报告。
        这份报告必须：
        1. 使用清晰、专业的Markdown格式。
        2. 包含一个欢迎语，提及客户的名字。
        3. 核心内容部分，必须包含一条**直接针对他/她的个人原则**的、具有可操作性的独特建议。
        4. 报告整体风格要积极、赋能，而不是批评。
        """
        tool, success = self._generate(prompt)
        # We add a fallback with more information for debugging
        return tool if success else f"抱歉，无法生成您的专属工具。AI返回的原始信息：{tool}"
