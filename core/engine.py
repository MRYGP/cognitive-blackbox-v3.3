# core/engine.py - v4.1 强制诊断版本
# 信息透明原则：无论成功失败，都要让用户知道真相
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple
import logging
import json

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
        """恢复高质量优先策略：优先使用最佳模型，确保用户体验"""
        model_priority = [
            'gemini-2.5-pro',          # 主要模型：最高质量
            'gemini-1.5-pro',          # 备选选项：稳定高质量
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

    def _generate(self, prompt: str) -> Dict[str, Any]:
        """
        强制诊断版本的生成方法
        返回完整的诊断信息，绝不静默失败
        """
        result = {
            "success": False,
            "content": "",
            "error_message": None,
            "raw_response": None,
            "model_used": self.current_model,
            "prompt_length": len(prompt),
            "debug_info": {}
        }
        
        # 引擎初始化检查
        if not self.is_initialized:
            result["error_message"] = f"AI引擎未初始化: {self.error_message}"
            result["debug_info"]["engine_status"] = "未初始化"
            return result
        
        # 模型可用性检查
        if not self.model:
            result["error_message"] = "AI模型不可用"
            result["debug_info"]["model_status"] = "模型未加载"
            return result
        
        try:
            result["debug_info"]["api_call_start"] = "开始API调用"
            
            # 安全设置
            safety_settings = [
                {'category': c, 'threshold': 'BLOCK_NONE'} 
                for c in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 
                         'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']
            ]
            
            # 生成配置
            generation_config = {
                'temperature': 0.8,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2000
            }
            
            # 执行API调用
            response = self.model.generate_content(
                prompt, 
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            result["debug_info"]["api_call_complete"] = "API调用完成"
            result["raw_response"] = str(response) if response else "空响应"
            
            # 详细的响应检查
            if not response:
                result["error_message"] = "API返回空响应"
                result["debug_info"]["response_status"] = "空响应"
                return result
            
            if not hasattr(response, 'parts') or not response.parts:
                result["error_message"] = "API响应缺少内容部分"
                result["debug_info"]["response_status"] = "无parts属性或parts为空"
                result["debug_info"]["response_attributes"] = dir(response)
                return result
            
            # 提取文本内容
            try:
                text_content = response.text
                result["debug_info"]["text_extraction"] = "成功提取文本"
                result["debug_info"]["text_length"] = len(text_content) if text_content else 0
                
                if not text_content or text_content.strip() == "":
                    result["error_message"] = "API返回空文本内容"
                    result["debug_info"]["content_status"] = "文本为空"
                    return result
                
                # 成功情况
                result["success"] = True
                result["content"] = text_content.strip()
                result["debug_info"]["final_status"] = "成功"
                
                return result
                
            except Exception as text_error:
                result["error_message"] = f"文本提取失败: {str(text_error)}"
                result["debug_info"]["text_extraction_error"] = str(text_error)
                return result
            
        except Exception as e:
            # 捕获所有API调用异常
            error_msg = str(e)
            result["error_message"] = f"API调用异常: {error_msg}"
            result["debug_info"]["exception_type"] = type(e).__name__
            result["debug_info"]["exception_details"] = error_msg
            
            # 特殊错误类型标记
            if '429' in error_msg or 'quota' in error_msg.lower():
                result["debug_info"]["error_category"] = "配额限制"
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                result["debug_info"]["error_category"] = "网络错误"
            else:
                result["debug_info"]["error_category"] = "未知错误"
            
            return result

    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息"""
        return {
            'initialization': self.debug_info,
            'is_initialized': self.is_initialized,
            'error_message': self.error_message,
            'current_model': self.current_model,
            'model_type': str(type(self.model)) if self.model else None
        }

    def generate_personalized_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成个性化质疑问题 - Damien角色 - 强制诊断版本"""
        case_id = context.get('case_id', 'unknown')
        user_choice = context.get('act1_choice', '未记录')
        
        prompt = f"""你是一位名叫Damien的对冲基金经理，专门以尖锐质疑著称。用户在{case_id}案例中选择了"{user_choice}"。
        
请生成一个不超过40字符的尖锐质疑问题，让用户重新思考自己的决策。要求：
1. 直接针对用户的选择
2. 语气尖锐但专业
3. 一句话，40字符以内"""
        
        result = self._generate(prompt)
        
        # 如果失败，提供fallback但保留错误信息
        if not result["success"]:
            result["fallback_content"] = "这个'完美'的机会，最让你不安的是什么？"
        
        return result

    def generate_athena_feedback(self, context: Dict[str, Any], step_id: str, step_title: str, user_input: str) -> Dict[str, Any]:
        """生成Athena导师的智慧反馈 - 强制诊断版本"""
        case_id = context.get('case_id', 'unknown')
        
        # 根据案例确定偏误类型
        bias_mapping = {
            'madoff': "光环效应",
            'lehman': "确认偏误", 
            'ltcm': "过度自信效应"
        }
        bias_type = bias_mapping.get(case_id, "认知偏误")
        
        prompt = f"""你是一位名叫Athena的AI智慧导师，温暖而睿智。一个学生正在学习对抗{bias_type}，刚刚为DOUBT模型中的"{step_title}"概念，写下了他的思考：

"{user_input}"

请用一句充满智慧和鼓励的话来点评他的思考。要求：
1. 既要肯定他的努力，又要启发更深层思考
2. 温暖鼓励的语调，体现导师的智慧
3. 控制在50字以内
4. 不要重复用户的原话

示例风格："这种反思很有价值！你已经开始用批判性思维审视表面的完美，这正是突破{bias_type}的关键第一步。"""

        result = self._generate(prompt)
        
        # 如果失败，提供个性化fallback
        if not result["success"]:
            fallback_feedbacks = {
                'D': f"很好的批判性思考！质疑看似完美的机会，正是对抗{bias_type}的第一步。",
                'O': f"优秀的警觉性！寻找反向证据能帮你避开{bias_type}的陷阱。",
                'U': f"诚实面对不确定性需要勇气，这种自省正是智慧决策的基础。",
                'B': f"用概率思维看待机会，这种理性分析能有效防范{bias_type}。",
                'T': f"从长远视角审视决策，这种时间维度的思考展现了真正的智慧。"
            }
            result["fallback_content"] = fallback_feedbacks.get(step_id, f"很好的思考！继续保持这种理性分析的精神。")
        
        return result

    def generate_personalized_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """案例感知的Athena角色工具生成 - 强制诊断版本"""
        
        # 获取用户信息和案例信息
        case_id = context.get('case_id', 'unknown')
        user_name = context.get("user_name", "用户")
        user_principle = context.get("user_principle", "理性决策")
        user_choice = context.get("act1_choice", "未记录")
        
        # 诊断用户输入
        input_diagnostics = {
            "case_id": case_id,
            "user_name": user_name,
            "user_principle": user_principle,
            "user_choice": user_choice,
            "context_keys": list(context.keys())
        }
        
        # 根据案例动态确定偏误类型和框架
        case_mapping = {
            'madoff': {
                "case_name": "Madoff Ponzi Scheme",
                "bias_type": "光环效应",
                "bias_english": "Halo Effect",
                "framework": "四维独立验证矩阵"
            },
            'lehman': {
                "case_name": "Lehman Brothers Collapse",
                "bias_type": "确认偏误",
                "bias_english": "Confirmation Bias", 
                "framework": "DOUBT思维模型"
            },
            'ltcm': {
                "case_name": "LTCM Collapse",
                "bias_type": "过度自信效应",
                "bias_english": "Overconfidence Effect",
                "framework": "RISK思维模型"
            }
        }
        
        case_info = case_mapping.get(case_id, {
            "case_name": "Financial Investment Case",
            "bias_type": "认知偏误",
            "bias_english": "Cognitive Bias",
            "framework": "理性决策框架"
        })
        
        # 构建详细的prompt
        prompt = f"""SYSTEM: 你是一位名叫"Athena"的AI决策导师，你服务过无数诺贝尔奖得主和顶级企业家。你的任务是为你的客户，撰写一份高度个人化、可作为其终身行为准则的《决策心智模型备忘录》。

USER CONTEXT:
- Case Studied: {case_info["case_name"]} ({case_info["bias_english"]})
- User Name: "{user_name}"
- User's Personal Principle: "{user_principle}"
- User's Initial Decision in the case: "{user_choice}"
- Target Cognitive Bias: {case_info["bias_type"]}
- Recommended Framework: {case_info["framework"]}

TASK: Generate a personalized "Cognitive Immune System" memo in Markdown format. The memo must strictly follow this structure and be specifically tailored to {case_info["bias_type"]}:

# 🛡️ 为 {user_name} 定制的【{case_info["bias_type"]}】免疫系统

> 核心原则整合："{user_principle}"——这正是您对抗{case_info["bias_type"]}的第一道防线。为了将它从'信念'变为'本能'，请在下次遇到类似情况时，将这句话大声朗读出来。

## 💡 基于您本次决策模式的专属建议

(Based on the user's "{user_choice}" in {case_info["case_name"]}, generate 1-2 unique, actionable suggestions specifically for preventing {case_info["bias_type"]}. Be creative and insightful.)

## ⚙️ 通用反制工具箱 - {case_info["framework"]}

- **工具一：** (Provide one core countermeasure specifically for {case_info["bias_type"]})
- **工具二：** (Provide another core countermeasure specifically for {case_info["bias_type"]})

请确保所有建议都针对{case_info["bias_type"]}，而不是其他认知偏误。"""

        result = self._generate(prompt)
        
        # 添加输入诊断信息
        result["input_diagnostics"] = input_diagnostics
        result["case_info"] = case_info
        
        # 如果失败，提供高质量fallback
        if not result["success"]:
            result["fallback_content"] = self._get_premium_fallback_tool(context, case_id)
        
        return result
    
    def _get_premium_fallback_tool(self, context: Dict[str, Any], case_id: str = 'unknown') -> str:
        """案例感知的高质量备选工具"""
        user_name = context.get('user_name', '用户')
        user_principle = context.get('user_principle', '理性决策')
        user_choice = context.get('act1_choice', '未记录')
        
        # 根据案例确定偏误类型和工具
        if case_id == 'lehman':
            bias_type = "确认偏误"
            framework = "DOUBT思维模型"
            tools = """- **工具一：** 魔鬼代言人法——主动寻找反对自己观点的证据和理由
- **工具二：** 反向验证法——强制收集与自己判断相冲突的信息"""
            suggestions = f"""基于您选择了"{user_choice}"，我建议您：
- 建立"反面证据收集"习惯，每个决策都要找到至少3个反对理由
- 设立"信息平衡检查点"，确保正反面信息的比例不低于3:2"""
        elif case_id == 'ltcm':
            bias_type = "过度自信效应"
            framework = "RISK思维模型"
            tools = """- **工具一：** 概率校准训练——定期检验自己预测的准确率，培养概率思维
- **工具二：** 极端情景压力测试——每个决策都要考虑1%极端情况的影响"""
            suggestions = f"""基于您选择了"{user_choice}"，我建议您：
- 建立"不确定性地图"，明确标注自己不知道的部分
- 设置"模型失效预警机制"，当现实偏离预期时立即重新评估"""
        else:  # madoff 或默认
            bias_type = "光环效应"
            framework = "四维独立验证矩阵"
            tools = """- **工具一：** 权威分离验证法——将个人魅力与专业能力严格区分
- **工具二：** 透明度压力测试——任何不透明的投资策略都是红旗信号"""
            suggestions = f"""基于您选择了"{user_choice}"，我建议您：
- 在面对权威人物时，先问自己："他的专业能力是否与投资决策直接相关？"
- 建立一个"48小时冷静期"规则，任何重大投资决策都要经过这个时间缓冲"""
        
        return f"""# 🛡️ 为 {user_name} 定制的【{bias_type}】免疫系统

> 核心原则整合："{user_principle}"——这正是您对抗{bias_type}的第一道防线。为了将它从'信念'变为'本能'，请在下次遇到类似情况时，将这句话大声朗读出来。

## 💡 基于您本次决策模式的专属建议

{suggestions}

## ⚙️ 通用反制工具箱 - {framework}

{tools}"""
