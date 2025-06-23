# core/engine.py - 智能模型降级版本
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
        self.current_model = None  # 新增：跟踪当前使用的模型
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
            
            # 智能模型选择策略
            self._initialize_with_fallback()
            
            self.is_initialized = True
            self.debug_info['init_result'] = '初始化成功'
            logging.info("AI Engine initialized successfully.")
            
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {e}"
            self.debug_info['init_error'] = str(e)
            logging.error(self.error_message)

    def _initialize_with_fallback(self):
        """智能模型初始化 - 按配额友好程度排序"""
        # 模型选择优先级：从最便宜/配额最宽松到最昂贵
        model_priority = [
            'gemini-1.5-flash',        # 最便宜，配额最宽松
            'gemini-1.5-pro',          # 中等价格和配额
            'gemini-2.5-pro'           # 最昂贵，配额最严格
        ]
        
        for model_name in model_priority:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.current_model = model_name
                self.debug_info['model_init'] = f'{model_name}模型已初始化'
                break
            except Exception as e:
                self.debug_info[f'model_init_fail_{model_name}'] = str(e)
                continue
        
        if not self.model:
            raise ValueError("所有模型初始化失败")

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        """智能生成 - 包含配额感知的模型降级"""
        call_debug = {
            'timestamp': str(type(self).__name__),
            'is_initialized': self.is_initialized,
            'prompt_length': len(prompt),
            'model_available': self.model is not None,
            'current_model': self.current_model
        }
        
        if not self.is_initialized:
            call_debug['early_exit'] = 'AI引擎未初始化'
            self.debug_info['last_call'] = call_debug
            return self.error_message, False
        
        # 尝试当前模型，如果配额不足则降级
        result = self._try_generate_with_fallback(prompt, call_debug)
        self.debug_info['last_call'] = call_debug
        return result

    def _try_generate_with_fallback(self, prompt: str, call_debug: Dict) -> Tuple[str, bool]:
        """尝试生成，遇到配额问题时自动降级模型"""
        
        # 模型降级顺序
        fallback_models = [
            self.current_model,        # 当前模型
            'gemini-1.5-flash',        # 降级到Flash
            'gemini-1.5-pro',          # 再降级到1.5 Pro
        ]
        
        # 去重并保持顺序
        unique_models = []
        for model in fallback_models:
            if model and model not in unique_models:
                unique_models.append(model)
        
        for model_name in unique_models:
            try:
                call_debug[f'trying_model'] = model_name
                
                # 如果需要切换模型
                if self.current_model != model_name:
                    self.model = genai.GenerativeModel(model_name)
                    self.current_model = model_name
                    call_debug[f'switched_to_model'] = model_name
                
                # 执行API调用
                result = self._execute_api_call(prompt, call_debug)
                if result[1]:  # 如果成功
                    call_debug['successful_model'] = model_name
                    return result
                    
            except Exception as e:
                error_str = str(e)
                call_debug[f'error_{model_name}'] = error_str
                
                # 检查是否是配额错误
                if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                    call_debug[f'quota_exceeded_{model_name}'] = True
                    # 如果是配额错误，继续尝试下一个模型
                    continue
                else:
                    # 如果是其他错误，返回错误信息
                    return f"API调用异常: {e}", False
        
        # 所有模型都失败了
        call_debug['all_models_failed'] = True
        return "所有可用模型的配额都已耗尽，请稍后重试", False

    def _execute_api_call(self, prompt: str, call_debug: Dict) -> Tuple[str, bool]:
        """执行具体的API调用"""
        call_debug['safety_settings_prepared'] = True
        
        safety_settings = [
            {'category': c, 'threshold': 'BLOCK_NONE'} 
            for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 
                     'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']
        ]
        
        call_debug['api_call_start'] = '开始API调用'
        
        response = self.model.generate_content(prompt, safety_settings=safety_settings)
        
        call_debug['api_call_complete'] = 'API调用完成'
        call_debug['response_available'] = response is not None
        
        # 详细的响应分析
        if response:
            call_debug['response_type'] = str(type(response))
            call_debug['has_parts'] = hasattr(response, 'parts') and bool(response.parts)
            call_debug['has_text'] = hasattr(response, 'text')
            call_debug['has_candidates'] = hasattr(response, 'candidates') and bool(response.candidates)
            call_debug['has_prompt_feedback'] = hasattr(response, 'prompt_feedback')
            
            # 尝试获取文本
            if response.parts:
                call_debug['parts_count'] = len(response.parts) if response.parts else 0
                try:
                    text_result = response.text
                    call_debug['text_extraction'] = '成功通过response.text获取'
                    call_debug['text_length'] = len(text_result) if text_result else 0
                    return text_result, True
                except Exception as text_error:
                    call_debug['text_extraction_error'] = str(text_error)
            
            # 检查安全过滤
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    call_debug['block_reason'] = str(feedback.block_reason)
                    return f"内容被安全过滤拦截: {feedback.block_reason}", False
            
            # 检查candidates
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                call_debug['candidate_available'] = True
                if hasattr(candidate, 'finish_reason'):
                    call_debug['finish_reason'] = str(candidate.finish_reason)
        
        call_debug['final_result'] = 'API返回空响应'
        return "API返回空响应，请重试", False

    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息的方法"""
        return {
            'initialization': self.debug_info,
            'is_initialized': self.is_initialized,
            'error_message': self.error_message,
            'current_model': self.current_model,
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
