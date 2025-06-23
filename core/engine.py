# cognitive-blackbox/core/engineGEMINI_API_KEY")
            if not api_key:
                raise ValueError("API Key is missing or empty in st.secrets.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest').py
# -----------------------------------------------------------------------------
# The AI Engine for the Cognitive Black Box Application
# Version: v4.0 (Genesis Mode - FINAL & SYNTAX CORRECTED v17)
# Author: H
            # A simple test call to verify the key and model access
            self.model.generate_content("test", generation_config={"max_output_tokens": 5})
            
            self.is_initialized = True
oshino AI PM, with fix from C's diagnosis
# This version corrects the critical SyntaxError in the fallback tool string.
# -----------------------------------------------------------------------------

import streamlit as st
import google.generativeai as genai            self.error_message = None
            logging.info("AI Engine initialized successfully.")

        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {
from typing import Dict, Any, Tuple
import logging
import random

logging.basicConfig(level=logging.INFO)

class AIEngine:
    def __init__(self):
        self.model = None
type(e).__name__} - {e}"
            logging.error(self.error_message)

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if not self.is_initialized:
            return self.error_message, False
        
        try:
            safety_settings =        self.is_initialized = False
        self.error_message = None
        self._initialize()

    def _initialize(self):
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key: raise ValueError("API Key is missing in st.secrets.")
            
            genai.configure(api_key=api_key)
            self.model = genai {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT':.GenerativeModel('gemini-1.5-pro-latest')
            self.is_initialized = True
            logging.info("AI Engine initialized successfully.")
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {e}"
            logging.error(self.error_message)

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        if 'BLOCK_NONE',
            }
            response = self.model.generate_content(prompt, safety_settings=safety_settings)

            if response.candidates and response.candidates[0].content.parts:
                return response.text, True
            else:
                feedback = response.prompt_feedback
                block_reason not self.is_initialized: return self.error_message, False
        try:
            safety_settings = [{'category': c, 'threshold': 'BLOCK_NONE'} for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EX = feedback.block_reason if hasattr(feedback, 'block_reason') else 'Unknown'
                error_msg = f"AI未能生成内容。原因: {block_reason}"
                logging.warning(error_msg)
PLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']]
            response = self.model.                return error_msg, False
                
        except Exception as e:
            error_message = f"generate_content(prompt, safety_settings=safety_settings)
            if response.parts: return response.text, True
            else:
                feedback = response.prompt_feedback
                reason = feedback.block_reason调用AI API时发生程序错误: {e}"
            logging.error(error_message)
            return error if hasattr(feedback, 'block_reason') else 'Unknown'
                return f"内容被安全过滤拦截: {reason}", False
        except Exception as e:
            logging.error(f"API Call Failed: {e}")_message, False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        # --- THE SYNTAX FIX IS HERE ---
        prompt = f"""你是一位犀利的华
            return f"API调用异常: {e}", False

    def generate_personalized_question(self,尔街对冲基金经理。一个客户对“麦道夫”机会做出了“{context.get('act1_choice', '一个判断')}”的决策。请用一句简短、尖锐、直击要害的话来挑战他。"""
        question, success = self._generate(prompt)
        return question if success else context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            fallbacks = ["你真的确定这个判断是基于事实而非情感吗？", "从另一个角度看，这个决策最大的风险可能是什么？"]
            return random.choice(fallbacks)
        prompt = f"你是一位资深的金融 "你真的确定你的判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context:风险分析师。一位投资者对麦道夫投资机会选择了“{context.get('act1_choice', '未知选择')}”。请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。 Dict[str, Any]) -> str:
        prompt = f"""你是一位世界级的认知科学家。一个名叫“{context.get('user_name', '用户')}”的决策者学习了“麦道夫案例”，他的核心原则是：“{context.get('user_principle', '未提供')}”，第一幕决策是：“{context.get('act1_choice', '未记录')}”。请为他生成一个专属的“光环效应免疫系统要求: 专业且尖锐, 直击要害, 避免说教。"
        question, success = self._generate(prompt)
        return question if success else "你真的确定这个判断是基于事实而非情感吗”决策工具，必须包含一条针对他个人原则的独特建议。请使用Markdown格式化输出。"""
        tool, success = self._generate(prompt)
        return tool if success else f"抱歉，无法生成您的？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            return self._get_fallback_tool(context)
        prompt = f'请为用户"{context.get("user_name", "用户")}"创建一个光环效应免疫工具专属工具。错误信息：{tool}"
