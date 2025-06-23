# cognitive-blackbox/core/engine.py
# -----------------------------------------------------------------------------
# The AI Engine for the Cognitive Black Box Application
# Version: v4.0 (Genesis Mode - FINAL & CORRECTED v19)
# Author: C, with syntax fix by Hoshino
# This version is based on C's debug-enhanced code, with the critical
# SyntaxError (Chinese comma) in the prompt fixed.
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
        self.debug_info = {}
        self._initialize()

    def _initialize(self):
        try:
            self.debug_info['init_step'] = '开始初始化'
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                self.debug_info['init_error'] = 'API Key未找到'
                raise ValueError("API Key is missing in st.secrets.")
            self.debug_info['api_key_status'] = f'API Key获取成功: {api_key[:10]}...'
            genai.configure(api_key=api_key)
            self.debug_info['genai_config'] = '已配置genai'
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            self.debug_info['model_init'] = 'gemini-1.5-pro-latest模型已初始化'
            self.is_initialized = True
            self.debug_info['init_result'] = '初始化成功'
            logging.info("AI Engine initialized successfully.")
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {e}"
            self.debug_info['init_error'] = str(e)
            logging.error(self.error_message)

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        call_debug = {'timestamp': str(type(self).__name__), 'is_initialized': self.is_initialized, 'prompt_length': len(prompt), 'model_available': self.model is not None}
        if not self.is_initialized:
            call_debug['early_exit'] = 'AI引擎未初始化'
            self.debug_info['last_call'] = call_debug
            return self.error_message, False
        try:
            call_debug['safety_settings_prepared'] = True
            safety_settings = [{'category': c, 'threshold': 'BLOCK_NONE'} for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']]
            call_debug['api_call_start'] = '开始API调用'
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            call_debug['api_call_complete'] = 'API调用完成'
            call_debug['response_available'] = response is not None
            if response:
                call_debug['response_type'] = str(type(response)); call_debug['has_parts'] = hasattr(response, 'parts') and bool(response.parts); call_debug['has_text'] = hasattr(response, 'text'); call_debug['has_candidates'] = hasattr(response, 'candidates') and bool(response.candidates); call_debug['has_prompt_feedback'] = hasattr(response, 'prompt_feedback')
                if response.parts:
                    call_debug['parts_count'] = len(response.parts) if response.parts else 0
                    try:
                        text_result = response.text; call_debug['text_extraction'] = '成功通过response.text获取'; call_debug['text_length'] = len(text_result) if text_result else 0; self.debug_info['last_call'] = call_debug; return text_result, True
                    except Exception as text_error: call_debug['text_extraction_error'] = str(text_error)
                if hasattr(response, 'prompt_feedback'):
                    feedback = response.prompt_feedback
                    if hasattr(feedback, 'block_reason') and feedback.block_reason: call_debug['block_reason'] = str(feedback.block_reason); self.debug_info['last_call'] = call_debug; return f"内容被安全过滤拦截: {feedback.block_reason}", False
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]; call_debug['candidate_available'] = True
                    if hasattr(candidate, 'finish_reason'): call_debug['finish_reason'] = str(candidate.finish_reason)
            call_debug['final_result'] = 'API返回空响应'; self.debug_info['last_call'] = call_debug
            return "API返回空响应，请重试", False
        except Exception as e:
            call_debug['exception'] = str(e); call_debug['exception_type'] = str(type(e)); self.debug_info['last_call'] = call_debug; logging.error(f"API Call Failed: {e}"); return f"API调用异常: {e}", False

    def get_debug_info(self) -> Dict[str, Any]:
        return {'initialization': self.debug_info, 'is_initialized': self.is_initialized, 'error_message': self.error_message, 'model_type': str(type(self.model)) if self.model else None}

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            fallbacks = ["你真的确定这个判断是基于事实而非情感吗？", "从另一个角度看，这个决策最大的风险可能是什么？"]
            return random.choice(fallbacks)
        
        # --- THE SYNTAX FIX IS HERE: Replaced Chinese comma with English comma ---
        prompt = f"""你是一位世界级的、以尖锐和反向思维著称的对冲基金经理，你的名字叫“Damien”。你的任务是压力测试客户的投资逻辑。你只说一句最核心、最致命的质疑。USER CONTEXT: - Case: Madoff Ponzi Scheme - User's Initial Decision: "{context.get('act1_choice', '一个判断')}" TASK: Based on the user's decision, generate one sharp, insightful question to challenge their core assumption. EXAMPLE: - If user chose "相信权威", a good question is: "权威的‘光环’，是否让你忽视了最基本的财务常识？" - If user chose "拒绝投资", a good question is: "你的直觉很准,但你能清晰地说出,这个'完美'机会中,最让你不安的'红灯信号'是哪一个吗？" Now, generate a new, unique question for the user's decision. Your answer must be a single question, no longer than 40 characters."""
        question, success = self._generate(prompt)
        return question if success else "你真的确定这个判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        # (This function remains the same as C's correct version)
        if not self.is_initialized: return self._get_fallback_tool(context)
        prompt = f"""你是一位名叫“Athena”的AI决策导师，你服务过无数诺贝尔奖得主和顶级企业家。你的任务是为你的客户，撰写一份高度个人化、可作为其终身行为准则的《决策心智模型备忘录》。USER CONTEXT: - Case Studied: Madoff Ponzi Scheme (Halo Effect) - User Name: "{context.get('user_name', '用户')}" - User's Personal Principle: "{context.get('user_principle', '未提供')}" - User's Initial Decision in the case: "{context.get('act1_choice', '未记录')}" TASK: Generate a personalized "Cognitive Immune System" memo in Markdown format. The memo must strictly follow this structure: # 🛡️ 为 {context.get('user_name')} 定制的【光环效应】免疫系统 > 核心原则整合：“{context.get('user_principle')}”——这正是您对抗思维惯性的第一道防线。为了将它从‘信念’变为‘本能’，请在下次遇到类似权威时，将这句话大声朗读出来。 ## 💡 基于您本次决策模式的专属建议 (Based on the user's "{context.get('act1_choice')}", generate 1-2 unique, actionable suggestions here. Be creative and insightful.) ## ⚙️ 通用反制工具箱 - **工具一：** (Provide one core, standardized countermeasure for the Halo Effect) - **工具二：** (Provide another core, standardized countermeasure for the Halo Effect)"""
        tool, success = self._generate(prompt)
        return tool if success else self._get_fallback_tool(context)
    
    def _get_fallback_tool(self, context: Dict[str, Any]) -> str:
        # (This function remains the same as C's correct version)
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
