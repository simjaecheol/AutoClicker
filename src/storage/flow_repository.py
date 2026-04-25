import os
import json
from typing import List, Optional
from models.flow import Flow

class FlowRepository:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_path(self, flow_id: str) -> str:
        return os.path.join(self.base_dir, f"{flow_id}.json")

    def save(self, flow: Flow):
        path = self._get_path(flow.id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(flow.to_dict(), f, indent=2, ensure_ascii=False)

    def load(self, flow_id: str) -> Optional[Flow]:
        path = self._get_path(flow_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Flow.from_dict(data)

    def load_all(self) -> List[Flow]:
        flows = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                flow_id = filename[:-5]
                flow = self.load(flow_id)
                if flow:
                    flows.append(flow)
        return flows

    def delete(self, flow_id: str):
        path = self._get_path(flow_id)
        if os.path.exists(path):
            os.remove(path)

    def export_to_file(self, flow: Flow, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(flow.to_dict(), f, indent=2, ensure_ascii=False)

    def import_from_file(self, path: str) -> Flow:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Flow.from_dict(data)
