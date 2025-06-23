# config/settings.py
from dataclasses import dataclass

@dataclass
class AppConfig:
    PAGE_TITLE: str = "认知黑匣子"
    PAGE_ICON: str = "🧠"
