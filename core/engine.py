# core/engine.py - 最终修复版本
# 解决Gemini API调用的所有已知问题

import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Tuple
import os
import logging

class AIEngine:
    def __init__(self):
        self.model = None
        self.is_initialized = False
        try:
            # 多重API密钥获取策略
            api_key = None
            
            # 方式1: 从Streamlit secrets获取
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
            
            # 方式2: 从环境变量获取
            elif 'GEMINI_API_KEY' in os.environ:
                api_key = os.environ['GEMINI_API_KEY']
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in secrets or environment")
            
            # 配置API
            genai.configure(api_key=api_key)
            
            # 使用最稳定的模型版本
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"AI Engine Init Error: {e}")
            self.is_initialized = False

    def _generate(self, prompt: str) -> Tuple[str, bool]:
        """
        核心AI生成函数 - 处理所有可能的API响应情况
        """
        if not self.is_initialized or not self.model:
            return "AI功能暂时不可用，请稍后重试。", False
        
        try:
            # 正确的安全设置格式
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
                'candidate_count': 1
            }
            
            # 执行API调用
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            # 关键修复：正确的响应解析逻辑
            return self._parse_response(response)
            
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            print(f"Gemini API Error: {e}")
            return error_msg, False

    def _parse_response(self, response) -> Tuple[str, bool]:
        """
        解析Gemini API响应的专用函数
        处理所有可能的响应格式和错误情况
        """
        try:
            # 方法1: 直接获取text（最常见）
            if hasattr(response, 'text') and response.text:
                return response.text.strip(), True
            
            # 方法2: 通过candidates获取
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        text = candidate.content.parts[0].text
                        if text and text.strip():
                            return text.strip(), True
            
            # 方法3: 检查是否被安全过滤阻拦
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    return f"内容被安全过滤拦截: {feedback.block_reason}", False
            
            # 方法4: 检查候选响应的finish_reason
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    if finish_reason == 'SAFETY':
                        return "内容因安全策略被阻拦", False
                    elif finish_reason == 'RECITATION':
                        return "内容因版权问题被阻拦", False
                    elif finish_reason == 'OTHER':
                        return "API返回了未知错误", False
            
            # 如果所有方法都失败，返回通用错误
            return "AI未返回有效内容，请重试", False
            
        except Exception as e:
            return f"响应解析失败: {str(e)}", False

    def generate_personalized_question(self, context: Dict[str, Any]) -> str:
        """生成个性化质疑问题"""
        if not self.is_initialized:
            # 静态后备问题
            fallback_questions = [
                "你确定这个决策是基于理性分析吗？",
                "你有没有考虑过最坏的情况？", 
                "这个'完美'的机会背后可能隐藏着什么？"
            ]
            import random
            return random.choice(fallback_questions)
        
        # 构建更简洁、更安全的Prompt
        user_choice = context.get('act1_choice', '未知选择')
        prompt = f"""你是一位资深的金融风险分析师。一位投资者对麦道夫投资机会选择了"{user_choice}"。

请用一句简短的话(不超过30字)质疑这个选择，让投资者重新思考。

要求:
- 专业且尖锐
- 直击要害
- 避免说教"""

        question, success = self._generate(prompt)
        
        if success:
            return question
        else:
            return "你真的确定这个判断是基于事实而非情感吗？"

    def generate_personalized_tool(self, context: Dict[str, Any]) -> str:
        """生成个性化决策工具"""
        if not self.is_initialized:
            return self._get_fallback_tool(context)
        
        user_name = context.get('user_name', '用户')
        user_principle = context.get('user_principle', '理性决策')
        user_choice = context.get('act1_choice', '未记录')
        
        # 构建结构化的Prompt
        prompt = f"""请为用户"{user_name}"创建一个光环效应免疫工具。

用户信息:
- 姓名: {user_name}
- 决策原则: {user_principle}  
- 麦道夫案例选择: {user_choice}

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
            return self._get_fallback_tool(context)
    
    def _get_fallback_tool(self, context: Dict[str, Any]) -> str:
        """静态后备工具"""
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
