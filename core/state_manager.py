# core/state_manager.py
"""
健壮的状态管理系统 - v4.1重构版本
核心设计理念：单一状态源、原子化操作、防御性编程
"""

import streamlit as st
from typing import Optional, Dict
from core.models import ViewState, Case
from core.engine import AIEngine
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """
    统一状态管理器 - 认知黑匣子应用的状态管理核心
    
    设计原则：
    1. 单一状态源：只管理一个session_state.view_state
    2. 原子化操作：状态切换要么完全成功，要么完全回滚
    3. 防御性编程：所有状态访问都有边界检查
    """
    
    def __init__(self):
        """初始化状态管理器，确保核心状态存在"""
        self._ensure_state_initialized()
        self._ensure_ai_engine_initialized()
    
    def _ensure_state_initialized(self):
        """确保核心状态已初始化 - 防御性编程"""
        if 'view_state' not in st.session_state:
            st.session_state.view_state = ViewState()
            logger.info("StateManager: 初始化新的ViewState")
    
    def _ensure_ai_engine_initialized(self):
        """确保AI引擎已初始化 - 分离关注点"""
        if 'ai_engine' not in st.session_state:
            st.session_state.ai_engine = AIEngine()
            logger.info("StateManager: 初始化AI引擎")
    
    @property
    def current_state(self) -> ViewState:
        """获取当前状态 - 只读访问"""
        return st.session_state.view_state
    
    @property
    def ai_engine(self) -> AIEngine:
        """获取AI引擎实例"""
        return st.session_state.ai_engine
    
    @property
    def current_case_obj(self) -> Optional[Case]:
        """获取当前案例对象 - 缓存机制"""
        if 'case_obj' not in st.session_state:
            return None
        
        # 验证缓存的case_obj是否与当前case_id匹配
        cached_case = st.session_state.case_obj
        if cached_case and cached_case.id == self.current_state.case_id:
            return cached_case
        
        # 缓存不匹配，清除缓存
        if 'case_obj' in st.session_state:
            del st.session_state.case_obj
        return None
    
    def set_case_obj(self, case_obj: Case):
        """设置案例对象到缓存"""
        st.session_state.case_obj = case_obj
    
    # =====================================================
    # 核心状态切换操作 - 原子化且防御性
    # =====================================================
    
    def go_to_case(self, case_id: str):
        """
        切换到指定案例的第一幕
        原子化操作：要么完全成功，要么保持原状态
        """
        try:
            logger.info(f"StateManager: 切换到案例 {case_id}")
            
            # 原子化状态重置
            st.session_state.view_state.reset_for_new_case(case_id)
            
            # 清除可能的案例对象缓存
            if 'case_obj' in st.session_state:
                del st.session_state.case_obj
            
            # 强制重新渲染
            st.rerun()
            
        except Exception as e:
            logger.error(f"StateManager: 案例切换失败 {e}")
            # 在错误情况下，保持当前状态不变
            st.error("案例切换失败，请重试")
    
    def go_to_selection(self):
        """
        返回案例选择页面
        完全清理所有相关状态
        """
        try:
            logger.info("StateManager: 返回案例选择页面")
            
            # 原子化状态重置
            st.session_state.view_state.reset_to_selection()
            
            # 清除所有案例相关缓存
            for key in ['case_obj']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # 强制重新渲染
            st.rerun()
            
        except Exception as e:
            logger.error(f"StateManager: 返回选择页面失败 {e}")
            st.error("页面切换失败，请重试")
    
    def advance_to_next_act(self):
        """进入下一幕 - 带边界检查"""
        try:
            logger.info(f"StateManager: 从第{self.current_state.act_num}幕进入下一幕")
            self.current_state.advance_act()
            st.rerun()
        except Exception as e:
            logger.error(f"StateManager: 下一幕切换失败 {e}")
            st.error("无法进入下一幕，请重试")
    
    def go_to_previous_act(self):
        """返回上一幕 - 带边界检查"""
        if self.current_state.act_num <= 1:
            st.warning("已经是第一幕了")
            return
        
        try:
            logger.info(f"StateManager: 从第{self.current_state.act_num}幕返回上一幕")
            self.current_state.previous_act()
            st.rerun()
        except Exception as e:
            logger.error(f"StateManager: 上一幕切换失败 {e}")
            st.error("无法返回上一幕，请重试")
    
    # =====================================================
    # AI反馈系统管理 (v4.1新增)
    # =====================================================
    
    def set_feedback(self, feedback: str):
        """设置AI反馈内容"""
        self.current_state.set_feedback(feedback)
        logger.info(f"StateManager: 设置AI反馈")
    
    def get_current_feedback(self) -> str:
        """获取当前反馈内容"""
        return self.current_state.current_feedback
    
    def is_showing_feedback(self) -> bool:
        """检查是否正在显示反馈"""
        return self.current_state.show_feedback
    
    def clear_feedback(self):
        """清除反馈状态"""
        self.current_state.clear_feedback()
        logger.info(f"StateManager: 清除AI反馈")
    
    def advance_sub_stage_with_feedback_check(self):
        """进入下一个子阶段前检查反馈状态"""
        if self.current_state.show_feedback:
            # 如果正在显示反馈，清除反馈并进入下一阶段
            self.clear_feedback()
            self.advance_sub_stage()
        else:
            # 如果没有显示反馈，说明用户刚提交答案，需要生成反馈
            # 这个逻辑将在第三幕交互中处理
            pass
    
    # =====================================================
    # 多步骤交互支持 (为第三幕DOUBT模型准备)
    # =====================================================
    
    def set_sub_stage(self, stage: int):
        """
        设置子阶段 - 用于第三幕等多步骤交互
        不触发页面重新渲染，只更新状态
        """
        if stage < 0:
            logger.warning(f"StateManager: 尝试设置负数子阶段 {stage}")
            return
        
        logger.info(f"StateManager: 设置子阶段为 {stage}")
        self.current_state.set_sub_stage(stage)
    
    def advance_sub_stage(self):
        """进入下一个子阶段"""
        new_stage = self.current_state.sub_stage + 1
        self.set_sub_stage(new_stage)
    
    def get_sub_stage(self) -> int:
        """获取当前子阶段"""
        return self.current_state.sub_stage
    
    # =====================================================
    # 上下文数据管理 - 安全访问接口
    # =====================================================
    
    def update_context(self, key: str, value):
        """安全更新上下文数据"""
        try:
            self.current_state.update_context(key, value)
            logger.debug(f"StateManager: 更新上下文 {key} = {value}")
        except Exception as e:
            logger.error(f"StateManager: 上下文更新失败 {e}")
    
    def get_context(self, key: str, default=None):
        """安全获取上下文数据"""
        return self.current_state.get_context(key, default)
    
    def get_full_context(self) -> dict:
        """获取完整上下文 - 用于AI调用"""
        return self.current_state.context.copy()
    
    # =====================================================
    # UI状态管理
    # =====================================================
    
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.current_state.show_debug = not self.current_state.show_debug
        logger.info(f"StateManager: 调试模式 {'开启' if self.current_state.show_debug else '关闭'}")
    
    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self.current_state.show_debug = enabled
    
    def is_debug_mode(self) -> bool:
        """检查是否为调试模式"""
        return self.current_state.show_debug
    
    def show_challenge_modal(self):
        """显示AI质疑模态框"""
        self.current_state.show_challenge_modal = True
    
    def hide_challenge_modal(self):
        """隐藏AI质疑模态框"""
        self.current_state.show_challenge_modal = False
    
    def is_challenge_modal_visible(self) -> bool:
        """检查模态框是否可见"""
        return self.current_state.show_challenge_modal
    
    # =====================================================
    # 状态查询接口 - 只读访问
    # =====================================================
    
    def get_current_view(self) -> str:
        """获取当前视图名称"""
        return self.current_state.view_name
    
    def get_current_case_id(self) -> Optional[str]:
        """获取当前案例ID"""
        return self.current_state.case_id
    
    def get_current_act_num(self) -> int:
        """获取当前幕数"""
        return self.current_state.act_num
    
    def is_in_selection_view(self) -> bool:
        """检查是否在案例选择页面"""
        return self.current_state.view_name == "selection"
    
    def is_in_act_view(self) -> bool:
        """检查是否在幕场景页面"""
        return self.current_state.view_name == "act"
    
    # =====================================================
    # 调试和诊断接口
    # =====================================================
    
    def get_state_summary(self) -> dict:
        """获取状态摘要 - 用于调试"""
        return {
            'view_name': self.current_state.view_name,
            'case_id': self.current_state.case_id,
            'act_num': self.current_state.act_num,
            'sub_stage': self.current_state.sub_stage,
            'context_keys': list(self.current_state.context.keys()),
            'show_debug': self.current_state.show_debug,
            'show_challenge_modal': self.current_state.show_challenge_modal,
            'has_case_obj_cache': 'case_obj' in st.session_state,
            'ai_engine_initialized': 'ai_engine' in st.session_state
        }
    
    def reset_all(self):
        """完全重置所有状态 - 仅用于紧急情况"""
        logger.warning("StateManager: 执行完全状态重置")
        
        # 清除所有session_state
        keys_to_clear = ['view_state', 'case_obj', 'ai_engine']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 重新初始化
        self._ensure_state_initialized()
        self._ensure_ai_engine_initialized()
        
        st.rerun()
    
    # === CXO-04: 价值确认体验的状态管理 ===
    
    def is_tool_unlocked(self) -> bool:
        """检查用户是否已经解锁了工具"""
        return st.session_state.get('tool_unlocked', False)
    
    def unlock_tool(self):
        """解锁用户的专属工具"""
        st.session_state.tool_unlocked = True
        
    def reset_tool_unlock_status(self):
        """重置工具解锁状态（新案例开始时调用）"""
        if 'tool_unlocked' in st.session_state:
            del st.session_state.tool_unlocked
    
    def set_transition_active(self, is_active: bool):
        """设置转场动画是否正在播放"""
        st.session_state.transition_active = is_active
    
    def is_transition_active(self) -> bool:
        """检查是否正在播放转场动画"""
        return st.session_state.get('transition_active', False)
    
    # === CXO-03: 叙事转场的导航方法重构 ===
    
    def advance_to_next_act_with_transition(self, from_act: int, to_act: int):
        """带转场动画的幕间跳转"""
        # 设置转场状态
        self.set_transition_active(True)
        
        # 更新目标幕数
        self.current_state.act_num = to_act
        
        # 如果跳转到新案例，重置解锁状态
        if to_act == 1:
            self.reset_tool_unlock_status()
        
        # 触发页面重新渲染
        st.rerun()
    
    def complete_transition(self):
        """完成转场动画，进入正常渲染状态"""
        self.set_transition_active(False)
        st.rerun()
    
    # === 扩展的调试信息 ===
    
    def get_enhanced_debug_info(self) -> Dict[str, any]:
        """获取增强的调试信息，包含新的状态"""
        base_info = self.get_debug_info()
        
        # 添加新的状态信息
        enhanced_info = {
            **base_info,
            'tool_unlocked': self.is_tool_unlocked(),
            'transition_active': self.is_transition_active(),
            'unlock_feature_enabled': True,
            'transition_feature_enabled': True
        }
        
        return enhanced_info
