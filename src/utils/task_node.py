from PySide2.QtCore import QObject, Signal
from typing import Optional, List, Union, Dict
from dataclasses import dataclass, field
import uuid
import json
from pathlib import Path


class TaskNodeSignals(QObject):
    property_changed = Signal(str, object)  # Signal for property change


@dataclass
class TaskNode:
    NODE_NAME: Optional[str] = None
    recognition: Optional[str] = None
    action: Optional[str] = None
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

    signals: TaskNodeSignals = field(default_factory=TaskNodeSignals)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue

            private_field = f"_{field_name}"
            setattr(self, private_field, getattr(self, field_name))

            def getter(self, field=field_name):
                return getattr(self, f"_{field}")

            def setter(self, value, field=field_name):
                setattr(self, f"_{field}", value)
                self.signals.property_changed.emit(field, value)

            setattr(self.__class__, field_name, property(getter, setter))

    def to_dict(self) -> dict:
        """Convert TaskNode to dictionary for serialization"""
        result = {}
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue
            value = getattr(self, field_name)
            if value is not None:  # Only include non-None values
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'TaskNode':
        """Create TaskNode from dictionary"""
        # Create a copy of the data to avoid modifying the input
        node_data = data.copy()
        # Set the NODE_NAME from the dictionary key
        node_data['NODE_NAME'] = name
        # Filter out unknown fields
        valid_fields = {k: v for k, v in node_data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)

class TaskNodeManager:
    def __init__(self):
        self._nodes: Dict[str, TaskNode] = {}
        self._current_file_path: Optional[Path] = None

    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """
        Load nodes from a JSON file. Clears existing nodes before loading.
        Returns True if successful, False otherwise.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Invalid file format: expected dictionary")

            # Clear existing nodes
            self.clear_nodes()

            # Load new nodes
            for node_name, node_data in data.items():
                node = TaskNode.from_dict(node_name, node_data)
                self.add_node(node)

            # Save the current file path
            self._current_file_path = file_path
            return True

        except Exception as e:
            print(f"Error loading nodes from file: {e}")
            return False

    def save_to_file(self, file_path: Union[str, Path] = None) -> bool:
        """
        Save current nodes to a JSON file.
        If file_path is None, saves to the last loaded/saved file path.
        Returns True if successful, False otherwise.
        """
        try:
            # Use provided path or current path
            if file_path is None:
                if self._current_file_path is None:
                    raise ValueError("No file path specified and no previous file path exists")
                file_path = self._current_file_path
            else:
                file_path = Path(file_path)
                self._current_file_path = file_path  # Update current path when saving to new location

            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert nodes to dictionary format
            data = {}
            for node in self._nodes.values():
                if node.NODE_NAME:  # Only save nodes with a name
                    data[node.NODE_NAME] = node.to_dict()
                    # Remove NODE_NAME from the node data since it's now the key
                    data[node.NODE_NAME].pop('NODE_NAME', None)

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