from NodeGraphQt import NodeGraph, BaseNode
from Qt import QtWidgets


class TaskNode(BaseNode):
    __identifier__ = 'node.task'
    NODE_NAME = 'My Task Node'

    def __init__(self):
        super().__init__()
        # 添加输入和输出端口
        self.add_input("", multi_input=True)
        self.add_output('output1', multi_output=True)
        self.add_output('output2', multi_output=True)


class TaskNodeGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建布局
        layout = QtWidgets.QVBoxLayout(self)

        # 初始化节点图
        self.node_graph = NodeGraph()
        self.node_graph.register_node(TaskNode)

        self.node_graph.set_acyclic(False)

        # 创建节点
        try:
            node1 = self.node_graph.create_node('node.task.TaskNode', name='Start Task')
            node2 = self.node_graph.create_node('node.task.TaskNode', name='Process Task')

            # 获取节点查看器
            viewer = self.node_graph.viewer()
            layout.addWidget(viewer)

        except Exception as e:
            print(f"节点创建错误: {e}")
