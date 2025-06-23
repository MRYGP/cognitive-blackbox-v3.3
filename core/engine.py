# core/engine.py - 案例感知版本 (修复上下文混乱)
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
        self.current_model = None
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
        
        result = self._try_generate_with_fallback(prompt, call_debug)
        self.debug_info['last_call'] = call_debug
        return result

    def _try_generate_with_fallback(self, prompt: str, call_debug: Dict) -> Tuple[str, bool]:
        """尝试生成，遇到配额问题时自动降级模型"""
        
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
                    continue
                else:
                    return f"API调用异常: {e}", False
        
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
        
        if response:
            call_debug['response_type'] = str(type(response))
            call_debug['has_parts'] = hasattr(response, 'parts') and bool(response.parts)
            call_debug['has_text'] = hasattr(response, 'text')
            call_debug['has_candidates'] = hasattr(response, 'candidates') and bool(response.candidates)
            call_debug['has_prompt_feedback'] = hasattr(response, 'prompt_feedback')
            
            if response.parts:
                call_debug['parts_count'] = len(response.parts) if response.parts else 0
                try:
                    text_result = response.text
                    call_debug['text_extraction'] = '成功通过response.text获取'
                    call_debug['text_length'] = len(text_result) if text_result else 0
                    return text_result, True
                except Exception as text_error:
                    call_debug['text_extraction_error'] = str(text_error)
            
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    call_debug['block_reason'] = str(feedback.block_reason)
                    return f"内容被安全过滤拦截: {feedback.block_reason}", False
            
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
        
        # 新增：获取当前案例信息
        case_id = context.get('case_id', 'unknown')
        user_choice = context.get('act1_choice', '未知选择')
        
        # 根据不同案例生成不同的提示词
        if case_id == 'madoff':
            case_context = "麦道夫庞氏骗局，这是一个关于光环效应的案例"
        elif case_id == 'lehman':
            case_context = "雷曼兄弟倒闭，这是一个关于确认偏误的案例"
        elif case_id == 'ltcm':
            case_context = "LTCM崩溃，这是一个关于过度自信的案例"
        else:
            case_context = "金融投资案例"
        
        prompt = f"""你是一位资深的金融风险分析师。在{case_context}中，一位投资者选择了"{user_choice}"。请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。要求: 专业且尖锐, 直击要害, 避免说教。"""
        
        question, success = self._generate(prompt)
        return question if success else "你真的确定这个判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        if not self.is_initialized:
            return self._get_fallback_tool(context)
        
        # 新增：获取当前案例信息
        case_id = context.get('case_id', 'unknown')
        user_name = context.get("user_name", "用户")
        user_principle = context.get("user_principle", "理性决策")
        user_choice = context.get("act1_choice", "未记录")
        
        # 根据不同案例生成不同的工具
        if case_id == 'madoff':
            bias_type = "光环效应"
            framework = "四维独立验证矩阵"
            case_name = "麦道夫案例"
        elif case_id == 'lehman':
            bias_type = "确认偏误"
            framework = "DOUBT思维模型"
            case_name = "雷曼兄弟案例"
        elif case_id == 'ltcm':
            bias_type = "过度自信效应"
            framework = "RISK思维模型"
            case_name = "LTCM案例"
        else:
            bias_type = "认知偏误"
            framework = "理性决策框架"
            case_name = "当前案例"
        
        prompt = f"""请为用户"{user_name}"创建一个{bias_type}免疫工具。

用户信息:
- 姓名: {user_name}
- 决策原则: {user_principle}  
- {case_name}选择: {user_choice}

请基于{framework}生成包含以下内容的Markdown格式工具:
1. 个人化欢迎语(包含姓名和{bias_type})
2. 3-4条针对{bias_type}的决策检查清单
3. {bias_type}的特定预警信号
4. 紧急刹车机制

要求: 实用、简洁、200-300字，内容必须针对{bias_type}而不是其他认知偏误。"""

        tool, success = self._generate(prompt)
        return tool if success else self._get_fallback_tool(context, case_id)
    
    def _get_fallback_tool(self, context: Dict[str, Any], case_id: str = 'unknown') -> str:
        user_name = context.get('user_name', '您')
        
        # 根据案例提供不同的后备工具
        if case_id == 'lehman':
            return f"""## 🛡️ {user_name}的确认偏误免疫系统
### DOUBT思维检查清单
- [ ] **D - Devil's Advocate**: 找人专门反驳你的观点
- [ ] **O - Opposite Evidence**: 主动搜集反向证据
- [ ] **U - Uncertainty Mapping**: 承认和量化不确定性
- [ ] **B - Base Rate**: 重视基础概率和历史数据
- [ ] **T - Time Horizon**: 扩展时间视野看问题
### ⚠️ 确认偏误预警信号
- 只关注支持自己观点的信息
- 忽视或曲解反面证据
- 过分相信历史经验
### 🚨 紧急刹车机制
**当出现选择性信息收集时，立即停止决策，强制寻找反面证据。**"""
        elif case_id == 'ltcm':
            return f"""## 🛡️ {user_name}的过度自信免疫系统
### RISK思维检查清单
- [ ] **R - Reality Check**: 现实检验，质疑模型假设
- [ ] **I - Ignorance Mapping**: 承认无知，识别知识盲区
- [ ] **S - Scenario Planning**: 情景规划，考虑极端情况
- [ ] **K - Kill Switch**: 设置止损机制
### ⚠️ 过度自信预警信号
- 过分相信模型预测
- 忽视小概率极端事件
- 认为自己比市场更聪明
### 🚨 紧急刹车机制
**当模型预测与现实出现偏差时，立即重新评估所有假设。**"""
        else:  # madoff 或默认
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
