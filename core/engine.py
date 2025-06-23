# core/engine.py - 体验驱动迭代版本
# 从"能用"到"卓越"的大脑升级
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
            
            # 升级规约：使用Gemini 2.5 Pro作为主要模型
            self._initialize_with_premium_model()
            
            self.is_initialized = True
            self.debug_info['init_result'] = '初始化成功'
            logging.info("AI Engine initialized successfully with premium model.")
            
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"AI引擎初始化失败: {e}"
            self.debug_info['init_error'] = str(e)
            logging.error(self.error_message)

    def _initialize_with_premium_model(self):
        """升级规约：优先使用Gemini 2.5 Pro，体验驱动的模型选择"""
        # 新的优先级：质量优先，稳定性保障
        model_priority = [
            'gemini-2.5-pro',          # 主要模型：最高质量
            'gemini-1.5-pro',          # 降级选项：稳定备选
            'gemini-1.5-flash'         # 最终备选：确保可用性
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
        """高级生成方法 - 优化为体验驱动"""
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
        
        # 增强的生成配置：针对创意和深度优化
        try:
            call_debug['safety_settings_prepared'] = True
            
            safety_settings = [
                {'category': c, 'threshold': 'BLOCK_NONE'} 
                for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 
                         'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']
            ]
            
            # 体验优化：增强创意性和深度的生成配置
            generation_config = {
                'temperature': 0.8,        # 提高创意性
                'top_p': 0.9,             # 增加多样性
                'top_k': 40,
                'max_output_tokens': 2000  # 支持更长的回答
            }
            
            call_debug['api_call_start'] = '开始API调用'
            
            response = self.model.generate_content(
                prompt, 
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            call_debug['api_call_complete'] = 'API调用完成'
            call_debug['response_available'] = response is not None
            
            if response and response.parts:
                call_debug['parts_count'] = len(response.parts)
                try:
                    text_result = response.text
                    call_debug['text_extraction'] = '成功通过response.text获取'
                    call_debug['text_length'] = len(text_result) if text_result else 0
                    self.debug_info['last_call'] = call_debug
                    return text_result, True
                except Exception as text_error:
                    call_debug['text_extraction_error'] = str(text_error)
            
            # 如果主要方法失败，尝试降级策略
            return self._try_fallback_generation(prompt, call_debug)
            
        except Exception as e:
            # 配额或其他错误时的智能降级
            if '429' in str(e) or 'quota' in str(e).lower():
                return self._try_fallback_generation(prompt, call_debug)
            else:
                call_debug['exception'] = str(e)
                self.debug_info['last_call'] = call_debug
                return f"API调用异常: {e}", False

    def _try_fallback_generation(self, prompt: str, call_debug: Dict) -> Tuple[str, bool]:
        """智能降级生成策略"""
        fallback_models = ['gemini-1.5-pro', 'gemini-1.5-flash']
        
        for model_name in fallback_models:
            try:
                if self.current_model != model_name:
                    self.model = genai.GenerativeModel(model_name)
                    self.current_model = model_name
                    call_debug[f'fallback_to'] = model_name
                
                response = self.model.generate_content(prompt)
                if response and response.parts:
                    call_debug['fallback_success'] = model_name
                    self.debug_info['last_call'] = call_debug
                    return response.text, True
                    
            except Exception as e:
                call_debug[f'fallback_fail_{model_name}'] = str(e)
                continue
        
        self.debug_info['last_call'] = call_debug
        return "所有模型都暂时不可用，请稍后重试", False

    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息"""
        return {
            'initialization': self.debug_info,
            'is_initialized': self.is_initialized,
            'error_message': self.error_message,
            'current_model': self.current_model,
            'model_type': str(type(self.model)) if self.model else None
        }

拒绝投资", a good question is: "你的直觉很准，但你能清晰地说出，这个'完美'机会中，最让你不安的'红灯信号'是哪一个吗？"

Now, generate a new, unique question for the user's decision. Your answer must be a single question, no longer than 40 characters."""

        question, success = self._generate(prompt)
        return question if success else "这个'完美'的机会，最让你不安的是什么？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        """升级规约：案例感知的Athena角色工具生成"""
        if not self.is_initialized:
            return self._get_premium_fallback_tool(context)
        
        # 获取用户信息和案例信息
        case_id = context.get('case_id', 'unknown')
        user_name = context.get("user_name", "用户")
        user_principle = context.get("user_principle", "理性决策")
        user_choice = context.get("act1_choice", "未记录")
        
        # 根据案例动态确定偏误类型和框架
        if case_id == 'madoff':
            case_name = "Madoff Ponzi Scheme"
            bias_type = "光环效应"
            bias_english = "Halo Effect"
            framework = "四维独立验证矩阵"
        elif case_id == 'lehman':
            case_name = "Lehman Brothers Collapse"
            bias_type = "确认偏误"
            bias_english = "Confirmation Bias"
            framework = "DOUBT思维模型"
        elif case_id == 'ltcm':
            case_name = "LTCM Collapse"
            bias_type = "过度自信效应"
            bias_english = "Overconfidence Effect"
            framework = "RISK思维模型"
        else:
            case_name = "Financial Investment Case"
            bias_type = "认知偏误"
            bias_english = "Cognitive Bias"
            framework = "理性决策框架"
        
        # 案例感知的Athena角色Prompt
        prompt = f"""SYSTEM: 你是一位名叫"Athena"的AI决策导师，你服务过无数诺贝尔奖得主和顶级企业家。你的任务是为你的客户，撰写一份高度个人化、可作为其终身行为准则的《决策心智模型备忘录》。

USER CONTEXT:
- Case Studied: {case_name} ({bias_english})
- User Name: "{user_name}"
- User's Personal Principle: "{user_principle}"
- User's Initial Decision in the case: "{user_choice}"
- Target Cognitive Bias: {bias_type}
- Recommended Framework: {framework}

TASK: Generate a personalized "Cognitive Immune System" memo in Markdown format. The memo must strictly follow this structure and be specifically tailored to {bias_type}:

# 🛡️ 为 {user_name} 定制的【{bias_type}】免疫系统

> 核心原则整合："{user_principle}"——这正是您对抗{bias_type}的第一道防线。为了将它从'信念'变为'本能'，请在下次遇到类似情况时，将这句话大声朗读出来。

## 💡 基于您本次决策模式的专属建议

(Based on the user's "{user_choice}" in {case_name}, generate 1-2 unique, actionable suggestions specifically for preventing {bias_type}. Be creative and insightful.)

## ⚙️ 通用反制工具箱 - {framework}

- **工具一：** (Provide one core countermeasure specifically for {bias_type})
- **工具二：** (Provide another core countermeasure specifically for {bias_type})

请确保所有建议都针对{bias_type}，而不是其他认知偏误。"""

        tool, success = self._generate(prompt)
        return tool if success else self._get_premium_fallback_tool(context, case_id)
    
    def _get_premium_fallback_tool(self, context: Dict[str, Any], case_id: str = 'unknown') -> str:
        """案例感知的高质量备选工具"""
        user_name = context.get('user_name', '您')
        user_principle = context.get('user_principle', '理性决策')
        user_choice = context.get('act1_choice', '未记录')
        
        # 根据案例确定偏误类型和工具
        if case_id == 'lehman':
            bias_type = "确认偏误"
            framework = "DOUBT思维模型"
            tools = """- **工具一：** 魔鬼代言人法——主动寻找反对自己观点的证据和理由
- **工具二：** 反向验证法——强制收集与自己判断相冲突的信息"""
            suggestions = """基于您选择了"{user_choice}"，我建议您：
- 建立"反面证据收集"习惯，每个决策都要找到至少3个反对理由
- 设立"信息平衡检查点"，确保正反面信息的比例不低于3:2"""
        elif case_id == 'ltcm':
            bias_type = "过度自信效应"
            framework = "RISK思维模型"
            tools = """- **工具一：** 概率校准训练——定期检验自己预测的准确率，培养概率思维
- **工具二：** 极端情景压力测试——每个决策都要考虑1%极端情况的影响"""
            suggestions = """基于您选择了"{user_choice}"，我建议您：
- 建立"不确定性地图"，明确标注自己不知道的部分
- 设置"模型失效预警机制"，当现实偏离预期时立即重新评估"""
        else:  # madoff 或默认
            bias_type = "光环效应"
            framework = "四维独立验证矩阵"
            tools = """- **工具一：** 权威分离验证法——将个人魅力与专业能力严格区分
- **工具二：** 透明度压力测试——任何不透明的投资策略都是红旗信号"""
            suggestions = """基于您选择了"{user_choice}"，我建议您：
- 在面对权威人物时，先问自己："他的专业能力是否与投资决策直接相关？"
- 建立一个"48小时冷静期"规则，任何重大投资决策都要经过这个时间缓冲"""
        
        return f"""# 🛡️ 为 {user_name} 定制的【{bias_type}】免疫系统

> 核心原则整合："{user_principle}"——这正是您对抗{bias_type}的第一道防线。为了将它从'信念'变为'本能'，请在下次遇到类似情况时，将这句话大声朗读出来。

## 💡 基于您本次决策模式的专属建议

{suggestions.format(user_choice=user_choice)}

## ⚙️ 通用反制工具箱 - {framework}

{tools}"""
