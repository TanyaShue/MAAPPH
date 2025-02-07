import copy
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from PySide2.QtCore import QObject, Signal


class TaskNodeSignals(QObject):
    """信号类，用于 TaskNode 属性变更通知."""
    property_changed = Signal(str, object)


@dataclass
class TaskNode:
    """
    表示一个任务节点的数据类.
    """
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

    def __init__(self) -> None:
        """初始化 TaskNode 实例."""
        self.signals: TaskNodeSignals = TaskNodeSignals()
        self.id: str = str(uuid.uuid4())[:8]
        self._init_properties()

    def _init_properties(self) -> None:
        """初始化所有属性的 getter 和 setter 方法."""
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue

            private_field = f"_{field_name}"
            setattr(self, private_field, None)

            def getter(self, field=field_name):
                return getattr(self, f"_{field}")

            def setter(self, value, field=field_name):
                setattr(self, f"_{field}", value)
                if hasattr(self, 'signals'):  # 检查 signals 属性是否存在
                    self.signals.property_changed.emit(field, value)

            setattr(self.__class__, field_name, property(getter, setter))

    def copy_from(self, other: 'TaskNode') -> None:
        """从另一个 TaskNode 实例复制所有属性，同时保留信号处理."""
        self.id = other.id  # 复制 id
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals"]:  # 只排除 signals，允许复制 id
                continue
            value = getattr(other, field_name)
            if isinstance(value, (list, dict)):
                value = copy.deepcopy(value)  # 深拷贝列表和字典
            setattr(self, field_name, value)

    @classmethod
    def create_empty(cls) -> 'TaskNode':
        """创建一个空的 TaskNode 实例."""
        return cls()

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """从字典更新节点属性."""
        for field_name, value in data.items():
            if field_name in self.__dataclass_fields__ and field_name not in ["signals", "id"]:
                setattr(self, field_name, value)

    def to_dict(self) -> Dict[str, Any]:
        """将 TaskNode 转换为字典，用于序列化."""
        result: Dict[str, Any] = {}
        for field_name in self.__dataclass_fields__:
            if field_name in ["signals", "id"]:
                continue
            value = getattr(self, field_name)
            if value is not None:  # 如果值为 None 则不保存该属性
                # 检查和转换 'roi' 和 'roi_offset' 类型
                if field_name in ["roi", "roi_offset"] and isinstance(value, str) and value.strip() != "" and value is not None:
                    try:
                        parsed_value = json.loads(value) # 尝试将字符串解析为 JSON
                        if isinstance(parsed_value, list) and all(isinstance(x, int) for x in parsed_value):
                            value = parsed_value
                        else:
                            raise ValueError
                    except (json.JSONDecodeError, ValueError):
                        raise ValueError(
                            f"Invalid format for {field_name}: {value}. Expected a JSON-style list of integers.")
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'TaskNode':
        """从字典创建 TaskNode 实例."""
        node = cls.create_empty()
        node_data = data.copy()
        node_data['NODE_NAME'] = name
        node_data.pop('signals', None) # 移除 'signals' 字段

        valid_fields = {k: v for k, v in node_data.items() if k in cls.__dataclass_fields__} # 过滤未知字段
        node.update_from_dict(valid_fields)
        return node


class TaskNodeManager:
    """
    TaskNode 管理器单例类.

    负责 TaskNode 的创建、加载、保存和管理.
    使用单例模式确保全局只有一个管理器实例.
    """
    _instance: Optional['TaskNodeManager'] = None  # 类变量，存储单例实例

    def __new__(cls, *args, **kwargs):
        """实现单例模式."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化 TaskNodeManager 实例."""
        if not hasattr(self, "_initialized"):  # 避免重复初始化
            self._nodes: Dict[str, TaskNode] = {}
            self._current_file_path: Optional[Path] = None
            self.selected_node: Optional[TaskNode] = None
            self._initialized = True  # 标记已初始化

    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """从 JSON 文件加载节点.

        Args:
            file_path (Union[str, Path]): 文件路径.

        Returns:
            bool: 加载成功返回 True, 失败返回 False.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Invalid file format: expected dictionary")

            self.clear_nodes() # 清空现有节点

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

        except FileNotFoundError as e:
            print(f"File not found error: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"Error loading nodes from file: {e}")
            return False

    def save_to_file(self, file_path: Union[str, Path] = None) -> bool:
        """保存节点到 JSON 文件.

        Args:
            file_path (Union[str, Path], optional): 文件路径. 如果为 None, 则使用上次加载或保存的文件路径. Defaults to None.

        Returns:
            bool: 保存成功返回 True, 失败返回 False.
        """
        try:
            if file_path is None:
                if self._current_file_path is None:
                    raise ValueError("No file path specified and no previous file path exists")
                file_path = self._current_file_path
            else:
                file_path = Path(file_path)
                self._current_file_path = file_path

            file_path.parent.mkdir(parents=True, exist_ok=True) # 创建父目录

            data: Dict[str, Any] = {}
            for node in self._nodes.values():
                if node.NODE_NAME:
                    node_data = node.to_dict()
                    node_data.pop('NODE_NAME', None) # 移除 'NODE_NAME' 字段
                    data[node.NODE_NAME] = node_data

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False) # 保存为 JSON 文件

            return True

        except ValueError as e:
            print(f"Value error: {e}")
            return False
        except Exception as e:
            print(f"Error saving nodes to file: {e}")
            return False

    def get_current_file_path(self) -> Optional[Path]:
        """获取当前文件路径."""
        return self._current_file_path

    def add_node(self, node: TaskNode) -> None:
        """添加一个 TaskNode 到管理器."""
        self._nodes[node.id] = node

    def remove_node(self, node_id: str) -> Optional[TaskNode]:
        """从管理器移除一个 TaskNode 并返回它."""
        return self._nodes.pop(node_id, None)

    def get_node_by_id(self, node_id: str) -> Optional[TaskNode]:
        """通过 ID 获取 TaskNode."""
        return self._nodes.get(node_id)

    def get_node_by_name(self, node_name: str) -> Optional[TaskNode]:
        """通过 NODE_NAME 获取 TaskNode."""
        for node in self._nodes.values():
            if node.NODE_NAME == node_name:
                return node
        return None

    def get_all_nodes(self) -> List[TaskNode]:
        """获取所有 TaskNode."""
        return list(self._nodes.values())

    def clear_nodes(self) -> None:
        """移除所有 TaskNode."""
        self._nodes.clear()

    def get_node_count(self) -> int:
        """获取 TaskNode 总数."""
        return len(self._nodes)

    def get_nodes_by_property(self, property_name: str, value: Any) -> List[TaskNode]:
        """获取所有具有特定属性值的 TaskNode."""
        return [
            node for node in self._nodes.values()
            if hasattr(node, property_name) and getattr(node, property_name) == value
        ]

    def exists(self, node_id: str) -> bool:
        """检查 TaskNode 是否存在."""
        return node_id in self._nodes

