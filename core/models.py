# core/models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Act:
    act_id: int
    title: str
    role_id: str
    content: str

@dataclass
class Case:
    id: str
    title: str
    tagline: str
    bias: List[str]
    icon: str
    difficulty: str
    duration_min: int
    estimated_loss_usd: str
    acts: Dict[int, Act] = field(default_factory=dict)

@dataclass
class ViewState:
    """
    统一的视图状态管理模型
    封装所有与当前视图相关的状态，确保状态切换的原子性
    """
    # 核心视图状态
    view_name: str = "selection"  # "selection", "act"
    case_id: Optional[str] = None
    act_num: int = 1
    
    # 多步骤交互支持 (为第三幕DOUBT模型等复杂交互准备)
    sub_stage: int = 0
    
    # AI反馈系统状态 (v4.1新增)
    show_feedback: bool = False
    current_feedback: str = ""
    
    # 用户交互数据
    context: Dict[str, any] = field(default_factory=dict)
    
    # UI状态
    show_debug: bool = False
    show_challenge_modal: bool = False
    
    def reset_for_new_case(self, case_id: str):
        """为新案例重置状态 - 确保无残留数据"""
        self.view_name = "act"
        self.case_id = case_id
        self.act_num = 1
        self.sub_stage = 0
        self.show_feedback = False
        self.current_feedback = ""
        self.context = {'case_id': case_id}
        self.show_challenge_modal = False
        # 保留 show_debug 状态，因为这是用户的全局偏好
    
    def reset_to_selection(self):
        """返回案例选择页面 - 完全清理状态"""
        self.view_name = "selection"
        self.case_id = None
        self.act_num = 1
        self.sub_stage = 0
        self.show_feedback = False
        self.current_feedback = ""
        self.context = {}
        self.show_challenge_modal = False
        # 保留 show_debug 状态
    
    def advance_act(self):
        """进入下一幕 - 重置sub_stage和反馈状态"""
        self.act_num += 1
        self.sub_stage = 0
        self.show_feedback = False
        self.current_feedback = ""
    
    def previous_act(self):
        """返回上一幕 - 重置sub_stage和反馈状态"""
        if self.act_num > 1:
            self.act_num -= 1
            self.sub_stage = 0
            self.show_feedback = False
            self.current_feedback = ""
    
    def set_sub_stage(self, stage: int):
        """设置子阶段 - 用于多步骤交互"""
        self.sub_stage = stage
        # 切换子阶段时重置反馈状态
        self.show_feedback = False
        self.current_feedback = ""
    
    def set_feedback(self, feedback: str):
        """设置AI反馈内容"""
        self.current_feedback = feedback
        self.show_feedback = True
    
    def clear_feedback(self):
        """清除反馈状态"""
        self.show_feedback = False
        self.current_feedback = ""
    
    def update_context(self, key: str, value: any):
        """安全更新上下文数据"""
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """安全获取上下文数据"""
        return self.context.get(key, default)
