# core/engine.py - 懒初始化版本
# 解决Streamlit Cloud初始化时序问题

import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple
import os

class AIEngine:
    def __init__(self):
        """
        构造函数中不进行任何API初始化
        采用懒初始化模式，确保在Streamlit完全启动后再获取secrets
        """
        self.model = None
        self.is_initialized = None  # None表示未尝试初始化
        self.initialization_error = None
    
    def _ensure_initialized(self) -> bool:
        """
        懒初始化：仅在真正需要时才初始化API客户端
        这确保了st.secrets在Streamlit完全启动后才被访问
        """
        # 如果已经成功初始化，直接返回
        if self.is_initialized is True:
            return True
        
        # 如果之前初始化失败过，不重复尝试（避免重复错误）
        if self.is_initialized is False:
            return False
        
        # 开始初始化过程
        try:
            # 多种方式获取API密钥
            api_key = None
            
            # 方式1: 从Streamlit secrets获取（主要方式）
            try:
                if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    print("✅ API密钥从st.secrets获取成功")
            except Exception as e:
                print(f"⚠️ 从st.secrets获取API密钥失败: {e}")
            
            # 方式2: 从环境变量获取（备用方式）
            if not api_key:
                api_key = os.environ.get('GEMINI_API_KEY')
                if api_key:
                    print("✅ API密钥从环境变量获取成功")
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY未找到：请检查Streamlit Secrets配置")
            
            # 配置Gemini API
            genai.configure(api_key=api_key)
            
            # 创建模型实例
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            
            # 标记初始化成功
            self.is_initialized = True
            print("✅ Gemini API客户端初始化成功")
            return True
            
        except Exception as e:
            # 记录初始化失败
            self.initialization_error = str(e)
            self.is_initialized = False
            print(f"❌ Gemini API初始化失败: {e}")
            return False

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        """
        核心生成函数 - 采用懒初始化确保API可用性
        """
        # 懒初始化：在真正需要时才初始化API
        if not self._ensure_initialized():
            error_msg = f"AI引擎初始化失败: {self.initialization_error or '未知错误'}"
            return error_msg, False
        
        try:
            # 正确的安全设置
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            # 生成配置
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1000,
            }
            
            print(f"🤖 发送请求到Gemini API...")
            
            # 执行API调用
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            print(f"📥 收到API响应")
            
            # 解析响应
            return self._parse_response(response)
            
        except Exception as e:
            error_msg = f"API调用失败: {str(e)}"
            print(f"❌ Gemini API调用异常: {e}")
            return error_msg, False

    def _parse_response(self, response) -> Tuple[str, bool]:
        """
        健壮的响应解析逻辑
        """
        try:
            # 方法1: 直接获取text
            if hasattr(response, 'text') and response.text:
                result = response.text.strip()
                print(f"✅ 成功获取响应内容: {len(result)}字符")
                return result, True
            
            # 方法2: 通过candidates获取
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        text = candidate.content.parts[0].text
                        if text and text.strip():
                            result = text.strip()
                            print(f"✅ 通过candidates获取响应: {len(result)}字符")
                            return result, True
            
            # 检查安全过滤
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    reason = feedback.block_reason
                    print(f"⚠️ 内容被安全过滤: {reason}")
                    return f"内容被安全过滤: {reason}", False
            
            # 检查生成失败原因
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    print(f"⚠️ 生成结束原因: {finish_reason}")
                    if finish_reason == 'SAFETY':
                        return "内容被安全策略阻拦", False
                    elif finish_reason == 'RECITATION':
                        return "内容涉及版权问题", False
                    elif finish_reason == 'OTHER':
                        return "API返回未知错误", False
            
            print("⚠️ API返回空响应")
            return "AI未返回有效内容，请重试", False
            
        except Exception as e:
            print(f"❌ 响应解析失败: {e}")
            return f"响应解析失败: {str(e)}", False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        """生成个性化质疑问题"""
        user_choice = context.get('act1_choice', '未知选择')
        
        prompt = f"""你是一位经验丰富的投资风险分析师。一位投资者对麦道夫投资机会选择了"{user_choice}"。

请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。

要求:
- 专业且尖锐
- 直击要害
- 避免说教"""

        question, success = self._generate(prompt)
        
        if success:
            return question
        else:
            # 静态后备问题
            fallback_questions = [
                "你确定这个决策是基于理性分析吗？",
                "你有没有考虑过最坏的情况？", 
                "这个'完美'机会背后可能隐藏着什么？"
            ]
            import random
            return random.choice(fallback_questions)

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        """生成个性化决策工具"""
        user_name = context.get('user_name', '用户')
        user_principle = context.get('user_principle', '理性决策')
        user_choice = context.get('act1_choice', '未记录')
        
        prompt = f"""请为用户"{user_name}"创建一个专属的光环效应免疫工具。

用户信息:
- 姓名: {user_name}
- 决策原则: {user_principle}  
- 第一幕选择: {user_choice}

请生成包含以下内容的Markdown格式工具:
1. 个人化欢迎语(包含姓名)
2. 3-4条决策检查清单
3. 光环效应预警信号
4. 紧急刹车机制

要求: 实用、简洁、200-300字。"""

        tool, success = self._generate(prompt)
        
        if success:
            return tool
        else:
            # 静态后备工具
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
