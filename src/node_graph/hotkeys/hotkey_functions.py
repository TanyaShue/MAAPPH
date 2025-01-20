#!/usr/bin/python
from src.utils.task_node import TaskNode, TaskNodeManager


# ------------------------------------------------------------------------------
# menu command functions
# ------------------------------------------------------------------------------
def add_base_node(graph):
    """
    Add a base node to the node graph.
    """
    task_node=TaskNode()
    node=graph.create_node('io.github.jchanvfx.MyNode')
    node.node_id=task_node.id
    node.note_data=task_node.to_dict()
    TaskNodeManager().add_node(task_node)
    # graph.add_node('BaseNode')


def reset_pos(graph):
    """
    Reset node graph position using NetworkX's neato layout with proper spacing.

    Args:
        graph: The graph object containing nodes and their connections

    Note:
        Requires networkx and pygraphviz to be installed:
        pip install networkx pygraphviz
    """
    import networkx as nx

    # 创建 NetworkX 有向图
    nx_graph = nx.DiGraph()

    # 获取所有节点
    nodes = graph.all_nodes()

    # 添加边到 NetworkX 图中
    for node in nodes:
        # 获取输入和输出连接
        input_nodes = node.connected_input_nodes()
        output_nodes = node.connected_output_nodes()

        # 添加输入边
        for input_node in input_nodes:
            nx_graph.add_edge(input_node.name, node.name)

        # 添加输出边
        for output_node in output_nodes:
            nx_graph.add_edge(node.name, output_node.name)

    try:
        # 使用 neato 布局算法
        pos = nx.nx_agraph.graphviz_layout(nx_graph, prog="neato")

        # 缩放位置以确保适当的间距
        # 使用 10 作为缩放因子,可以根据需要调整
        scaled_pos = {
            node_name: (x * 10, -y * 10)  # 反转 y 轴以获得更好的可视化效果
            for node_name, (x, y) in pos.items()
        }

        # 将计算出的位置应用到图中的节点
        for node in nodes:
            if node.name in scaled_pos:
                x, y = scaled_pos[node.name]
                success = node.set_pos(x, y)
                if success:
                    print(f"Node {node.name} position set to ({x}, {y})")
                else:
                    print(f"Failed to set position for node {node.name}")

    except Exception as e:
        print(f"Error during layout calculation: {str(e)}")
        # 如果 graphviz 布局失败,回退到简单的圆形布局
        try:
            pos = nx.circular_layout(nx_graph)
            scaled_pos = {
                node_name: (x * 5, y * 5)  # 使用更大的缩放因子确保节点间距
                for node_name, (x, y) in pos.items()
            }

            for node in nodes:
                if node.name in scaled_pos:
                    x, y = scaled_pos[node.name]
                    node.set_pos(x, y)
                    print(f"Node {node.name} position set to ({x}, {y}) using fallback layout")

        except Exception as e:
            print(f"Fallback layout also failed: {str(e)}")
            return False

    return True


# Example usage with a hypothetical graph object:
# reset_pos(your_graph)


def zoom_in(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    zoom = graph.get_zoom() + 0.1
    graph.set_zoom(zoom)


def zoom_out(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    zoom = graph.get_zoom() - 0.2
    graph.set_zoom(zoom)


def reset_zoom(graph):
    """
    Reset zoom level.
    """
    graph.reset_zoom()


def layout_h_mode(graph):
    """
    Set node graph layout direction to horizontal.
    """
    graph.set_layout_direction(0)


def layout_v_mode(graph):
    """
    Set node graph layout direction to vertical.
    """
    graph.set_layout_direction(1)


def open_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    current = graph.current_session()
    file_path = graph.load_dialog(current)
    if file_path:
        graph.load_session(file_path)


def import_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    current = graph.current_session()
    file_path = graph.load_dialog(current)
    if file_path:
        graph.import_session(file_path)


def save_session(graph):
    """
    Prompts a file save dialog to serialize a session if required.
    """
    current = graph.current_session()
    if current:
        graph.save_session(current)
        msg = 'Session layout saved:\n{}'.format(current)
        viewer = graph.viewer()
        viewer.message_dialog(msg, title='Session Saved')
    else:
        save_session_as(graph)


def save_session_as(graph):
    """
    Prompts a file save dialog to serialize a session.
    """
    current = graph.current_session()
    file_path = graph.save_dialog(current)
    if file_path:
        graph.save_session(file_path)


def clear_session(graph):
    """
    Prompts a warning dialog to new a node graph session.
    """
    if graph.question_dialog('Clear Current Session?', 'Clear Session'):
        graph.clear_session()

def quit_qt(graph):
    """
    Quit the Qt application.
    """
    from Qt import QtCore
    QtCore.QCoreApplication.quit()

def clear_undo(graph):
    """
    Prompts a warning dialog to clear undo.
    """
    viewer = graph.viewer()
    msg = 'Clear all undo history, Are you sure?'
    if viewer.question_dialog('Clear Undo History', msg):
        graph.clear_undo_stack()


def copy_nodes(graph):
    """
    Copy nodes to the clipboard.
    """
    graph.copy_nodes()


def cut_nodes(graph):
    """
    Cut nodes to the clip board.
    """
    graph.cut_nodes()


def paste_nodes(graph):
    """
    Pastes nodes copied from the clipboard.
    """
    graph.paste_nodes()


def delete_nodes(graph):
    """
    Delete selected node.
    """
    graph.delete_nodes(graph.selected_nodes())


def extract_nodes(graph):
    """
    Extract selected nodes.
    """
    graph.extract_nodes(graph.selected_nodes())


def clear_node_connections(graph):
    """
    Clear port connection on selected nodes.
    """
    graph.undo_stack().beginMacro('clear selected node connections')
    for node in graph.selected_nodes():
        for port in node.input_ports() + node.output_ports():
            port.clear_connections()
    graph.undo_stack().endMacro()


def select_all_nodes(graph):
    """
    Select all nodes.
    """
    graph.select_all()


def clear_node_selection(graph):
    """
    Clear node selection.
    """
    graph.clear_selection()


def invert_node_selection(graph):
    """
    Invert node selection.
    """
    graph.invert_selection()


def disable_nodes(graph):
    """
    Toggle disable on selected nodes.
    """
    graph.disable_nodes(graph.selected_nodes())


def duplicate_nodes(graph):
    """
    Duplicated selected nodes.
    """
    graph.duplicate_nodes(graph.selected_nodes())


def expand_group_node(graph):
    """
    Expand selected group node.
    """
    selected_nodes = graph.selected_nodes()
    if not selected_nodes:
        graph.message_dialog('Please select a "GroupNode" to expand.')
        return
    graph.expand_group_node(selected_nodes[0])


def fit_to_selection(graph):
    """
    Sets the zoom level to fit selected nodes.
    """
    graph.fit_to_selection()


def show_undo_view(graph):
    """
    Show the undo list widget.
    """
    graph.undo_view.show()


def curved_pipe(graph):
    """
    Set node graph pipes layout as curved.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.CURVED.value)


def straight_pipe(graph):
    """
    Set node graph pipes layout as straight.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.STRAIGHT.value)


def angle_pipe(graph):
    """
    Set node graph pipes layout as angled.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)


def bg_grid_none(graph):
    """
    Turn off the background patterns.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_NONE.value)


def bg_grid_dots(graph):
    """
    Set background node graph background with grid dots.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_DOTS.value)


def bg_grid_lines(graph):
    """
    Set background node graph background with grid lines.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_LINES.value)


def layout_graph_down(graph):
    """
    Auto layout the nodes down stream.
    """
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes=nodes, down_stream=True)


def layout_graph_up(graph):
    """
    Auto layout the nodes up stream.
    """
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes=nodes, down_stream=False)


def toggle_node_search(graph):
    """
    show/hide the node search widget.
    """
    graph.toggle_node_search()
