from PySide2.QtCore import QObject, Signal
from typing import Optional, List, Union
from dataclasses import dataclass


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

    signals: TaskNodeSignals = TaskNodeSignals()  # 延迟初始化
    #
    # def __init__(self):
    #     self.__dataclass_fields__ = None

    def __post_init__(self):
        for field in self.__dataclass_fields__:
            if field == "signals":
                continue  # 跳过 signals 属性

            private_field = f"_{field}"
            setattr(self, private_field, getattr(self, field))  # 初始化私有属性

            # 动态添加 getter
            def getter(self, field=field):
                return getattr(self, f"_{field}")

            # 动态添加 setter
            def setter(self, value, field=field):
                setattr(self, f"_{field}", value)
                self.signals.property_changed.emit(field, value)

            setattr(self.__class__, field, property(getter, setter))

