# core/models.py
from dataclasses import dataclass, field
from typing import List, Dict

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
