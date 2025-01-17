import copy
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Union, Dict

from PySide2.QtCore import QObject, Signal


class TaskNodeSignals(QObject):
    property_changed = Signal(str, object)

@dataclass
class TaskNode:
    NODE_NAME: Optional[str] = None
    recognition: Optional[str] = None
    action: Optional[str] = None
    custom_action: Optional[str] = None
    custom_action_param: Optional[str] = None
    enabled: Optional[bool] = None
    focus: Optional[bool] = None
    inverse: Optional[bool] = None
    roi: Optional[List[int]] = None
    roi_offset: Optional[List[int]] = None
    threshold: Optional[float] = None
    expected: Optional[str] = None
    target: Optional[Union[str, List[int]]] = None
    template: Optional[Union[str, List[str]]] = None
    target_offset: Optional[List[int]] = None
    next: Optional[List[str]] = None
    interrupt: Optional[List[str]] = None
    on_error: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    pre_delay: Optional[int] = None
    post_delay: Optional[int] = None
    pre_wait_freezes: Optional[int] = None
    post_wait_freezes: Optional[int] = None
    key: Optional[int] = None
    InputText: Optional[str] = None
    StartApp: Optional[str] = None
    StopApp: Optional[str] = None
    Command: Optional[str] = None
    package: Optional[str] = None

    def __init__(self):
        self.signals = TaskNodeSignals()
        self.id = str(uuid.uuid4())[:8]
        self._init_properties()

    def _init_properties(self):
        """Initialize all properties with their getters and setters"""
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue

            private_field = f"_{field_name}"
            setattr(self, private_field, None)

            def getter(self, field=field_name):
                return getattr(self, f"_{field}")

            def setter(self, value, field=field_name):
                setattr(self, f"_{field}", value)
                if hasattr(self, 'signals'):  # Check if signals exists
                    self.signals.property_changed.emit(field, value)

            setattr(self.__class__, field_name, property(getter, setter))

    def copy_from(self, other: 'TaskNode'):
        """Copy all properties from another TaskNode instance while preserving signal handling"""
        # 复制id
        self.id = other.id

        for field_name in self.__dataclass_fields__:
            if field_name in ["signals"]:  # 只排除signals，允许复制id
                continue
            value = getattr(other, field_name)
            if isinstance(value, (list, dict)):
                value = copy.deepcopy(value)
            setattr(self, field_name, value)

    @classmethod
    def create_empty(cls) -> 'TaskNode':
        """Create an empty TaskNode instance"""
        return cls()

    def update_from_dict(self, data: dict):
        """Update node properties from dictionary"""
        for field_name, value in data.items():
            if field_name in self.__dataclass_fields__ and field_name not in ["signals", "id"]:
                setattr(self, field_name, value)

    def to_dict(self) -> dict:
        """Convert TaskNode to dictionary for serialization"""
        result = {}
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'TaskNode':
        """Create TaskNode from dictionary"""
        node = cls.create_empty()
        node_data = data.copy()
        node_data['NODE_NAME'] = name
        node_data.pop('signals', None)

        # Filter out unknown fields
        valid_fields = {k: v for k, v in node_data.items() if k in cls.__dataclass_fields__}
        node.update_from_dict(valid_fields)
        return node

class TaskNodeManager:
    _instance = None  # 类变量，存储单例实例

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # 避免重复初始化
            self._nodes: Dict[str, TaskNode] = {}
            self._current_file_path: Optional[Path] = None
            self.selected_node: Optional[TaskNode] = None
            self._initialized = True  # 标记已初始化

    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load nodes from a JSON file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Invalid file format: expected dictionary")

            self.clear_nodes()

            for node_name, node_data in data.items():
                try:
                    node = TaskNode.create_empty()
                    node_data['NODE_NAME'] = node_name
                    node.update_from_dict(node_data)
                    self.add_node(node)
                except Exception as e:
                    print(f"Error loading node {node_name}: {e}")
                    continue

            self._current_file_path = file_path
            return True

        except Exception as e:
            print(f"Error loading nodes from file: {e}")
            return False

    def save_to_file(self, file_path: Union[str, Path] = None) -> bool:
        """Save nodes to a JSON file"""
        try:
            if file_path is None:
                if self._current_file_path is None:
                    raise ValueError("No file path specified and no previous file path exists")
                file_path = self._current_file_path
            else:
                file_path = Path(file_path)
                self._current_file_path = file_path

            file_path.parent.mkdir(parents=True, exist_ok=True)

            data = {}
            for node in self._nodes.values():
                if node.NODE_NAME:
                    node_data = node.to_dict()
                    node_data.pop('NODE_NAME', None)
                    data[node.NODE_NAME] = node_data

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving nodes to file: {e}")
            return False

    def get_current_file_path(self) -> Optional[Path]:
        """Get the current file path"""
        return self._current_file_path

    def add_node(self, node: TaskNode) -> None:
        """Add a TaskNode to the manager"""
        self._nodes[node.id] = node

    def remove_node(self, node_id: str) -> Optional[TaskNode]:
        """Remove a TaskNode from the manager and return it"""
        return self._nodes.pop(node_id, None)

    def get_node_by_id(self, node_id: str) -> Optional[TaskNode]:
        """Get a TaskNode by its ID"""
        return self._nodes.get(node_id)

    def get_node_by_name(self, node_name: str) -> Optional[TaskNode]:
        """Get a TaskNode by its NODE_NAME"""
        for node in self._nodes.values():
            if node.NODE_NAME == node_name:
                return node
        return None

    def get_all_nodes(self) -> List[TaskNode]:
        """Get all TaskNodes"""
        return list(self._nodes.values())

    def clear_nodes(self) -> None:
        """Remove all TaskNodes"""
        self._nodes.clear()

    def get_node_count(self) -> int:
        """Get the total number of TaskNodes"""
        return len(self._nodes)

    def get_nodes_by_property(self, property_name: str, value: any) -> List[TaskNode]:
        """Get all TaskNodes that have a specific property value"""
        return [
            node for node in self._nodes.values()
            if hasattr(node, property_name) and getattr(node, property_name) == value
        ]

    def exists(self, node_id: str) -> bool:
        """Check if a TaskNode exists by ID"""
        return node_id in self._nodes