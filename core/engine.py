# core/engine.py - 在原有代码基础上增强调试功能
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
        self.debug_info = {}  # 新增：调试信息收集
        self._initialize()

    def _initialize(self):
        try:
            # 新增：详细的初始化调试
            self.debug_info['init_step'] = '开始初始化'
            
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                self.debug_info['init_error'] = 'API Key未找到'
                raise ValueError("API Key is missing in st.secrets.")
            
            self.debug_info['api_key_status'] = f'API Key获取成功: {api_key[:10]}...'
            
            genai.configure(api_key=api_key)
            self.debug_info['genai_config'] = '已配置genai'
            
            # 保持原有的模型名称
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
        # 新增：详细的调用调试信息
        call_debug = {
            'timestamp': str(type(self).__name__),
            'is_initialized': self.is_initialized,
            'prompt_length': len(prompt),
            'model_available': self.model is not None
        }
        
        if not self.is_initialized:
            call_debug['early_exit'] = 'AI引擎未初始化'
            self.debug_info['last_call'] = call_debug
            return self.error_message, False
            
        try:
            # 新增：记录调用前状态
            call_debug['safety_settings_prepared'] = True
            
            safety_settings = [
                {'category': c, 'threshold': 'BLOCK_NONE'} 
                for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 
                         'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']
            ]
            
            call_debug['api_call_start'] = '开始API调用'
            
            # 执行原有的API调用逻辑
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            
            call_debug['api_call_complete'] = 'API调用完成'
            call_debug['response_available'] = response is not None
            
            # 新增：详细的响应分析
            if response:
                call_debug['response_type'] = str(type(response))
                call_debug['has_parts'] = hasattr(response, 'parts') and bool(response.parts)
                call_debug['has_text'] = hasattr(response, 'text')
                call_debug['has_candidates'] = hasattr(response, 'candidates') and bool(response.candidates)
                call_debug['has_prompt_feedback'] = hasattr(response, 'prompt_feedback')
                
                # 尝试获取文本的多种方法
                if response.parts:
                    call_debug['parts_count'] = len(response.parts) if response.parts else 0
                    try:
                        text_result = response.text
                        call_debug['text_extraction'] = '成功通过response.text获取'
                        call_debug['text_length'] = len(text_result) if text_result else 0
                        self.debug_info['last_call'] = call_debug
                        return text_result, True
                    except Exception as text_error:
                        call_debug['text_extraction_error'] = str(text_error)
                
                # 检查安全过滤
                if hasattr(response, 'prompt_feedback'):
                    feedback = response.prompt_feedback
                    if hasattr(feedback, 'block_reason') and feedback.block_reason:
                        call_debug['block_reason'] = str(feedback.block_reason)
                        self.debug_info['last_call'] = call_debug
                        return f"内容被安全过滤拦截: {feedback.block_reason}", False
                
                # 检查candidates
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    call_debug['candidate_available'] = True
                    if hasattr(candidate, 'finish_reason'):
                        call_debug['finish_reason'] = str(candidate.finish_reason)
            
            call_debug['final_result'] = 'API返回空响应'
            self.debug_info['last_call'] = call_debug
            return "API返回空响应，请重试", False
            
        except Exception as e:
            call_debug['exception'] = str(e)
            call_debug['exception_type'] = str(type(e))
            self.debug_info['last_call'] = call_debug
            logging.error(f"API Call Failed: {e}")
            return f"API调用异常: {e}", False

    def get_debug_info(self) -> Dict[str, Any]:
        """新增：获取调试信息的方法"""
        return {
            'initialization': self.debug_info,
            'is_initialized': self.is_initialized,
            'error_message': self.error_message,
            'model_type': str(type(self.model)) if self.model else None
        }

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            fallbacks = ["你真的确定这个判断是基于事实而非情感吗？", "从另一个角度看，这个决策最大的风险可能是什么？"]
            return random.choice(fallbacks)
        
        prompt = f"""你是一位资深的金融风险分析师。一位投资者对麦道夫投资机会选择了"{context.get('act1_choice', '未知选择')}"。请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。要求: 专业且尖锐, 直击要害, 避免说教。"""
        question, success = self._generate(prompt)
        return question if success else "你真的确定这个判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            return self._get_fallback_tool(context)
        
        prompt = f"""请为用户"{context.get("user_name", "用户")}"创建一个光环效应免疫工具。用户信息: 姓名: {context.get("user_name", "用户")}, 决策原则: {context.get("user_principle", "理性决策")}, 麦道夫案例选择: {context.get("act1_choice", "未记录")}。请生成包含以下内容的Markdown格式工具: 1. 个人化欢迎语(包含姓名) 2. 3-4条决策检查清单 3. 光环效应预警信号 4. 紧急刹车机制。要求: 实用、简洁、200-300字。"""
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
