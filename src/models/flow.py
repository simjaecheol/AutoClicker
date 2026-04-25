from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import uuid
from models.action import Action

@dataclass
class Flow:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    steps: List[Action] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    repeat_count: int = 1         # 0 = infinite
    repeat_interval: float = 0.0  # delay between repeats (seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "repeat_count": self.repeat_count,
            "repeat_interval": self.repeat_interval
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flow':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            steps=[Action.from_dict(step) for step in data.get("steps", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            repeat_count=data.get("repeat_count", 1),
            repeat_interval=data.get("repeat_interval", 0.0)
        )
