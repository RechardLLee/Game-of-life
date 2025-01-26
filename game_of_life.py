from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QSpinBox, QLabel, 
                             QColorDialog, QGraphicsView, QGraphicsScene, QFileDialog)
from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
import numpy as np
import sys
from typing import Optional, Tuple

class Pattern:
    """预设图案类"""
    def __init__(self, name: str, pattern: np.ndarray, description: str = ""):
        self.name = name
        self.pattern = pattern
        self.description = description

class GameOfLife:
    """生命游戏核心逻辑类"""
    
    def __init__(self, width: int = 50, height: int = 50):
        """初始化游戏状态
        
        Args:
            width: 网格宽度
            height: 网格高度
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=np.int8)
        self.generation = 0  # 添加代数计数
        self.history = []   # 添加历史记录
        self.boundary_type = "fixed"  # 边界类型：fixed/wrap
        
    def update(self) -> None:
        """更新一次游戏状态"""
        self.history.append(self.grid.copy())  # 保存历史
        if len(self.history) > 50:  # 限制历史记录数量
            self.history.pop(0)
            
        new_grid = self.grid.copy()
        for i in range(self.height):
            for j in range(self.width):
                neighbors = self._count_neighbors(i, j)
                if self.grid[i, j]:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[i, j] = 0
                elif neighbors == 3:
                    new_grid[i, j] = 1
        self.grid = new_grid
        self.generation += 1
    
    def _count_neighbors(self, i: int, j: int) -> int:
        """计算指定位置周围的活细胞数量"""
        return np.sum(self.grid[max(0, i-1):min(self.height, i+2),
                               max(0, j-1):min(self.width, j+2)]) - self.grid[i, j]
    
    def toggle_cell(self, i: int, j: int) -> None:
        """切换指定位置的细胞状态"""
        if 0 <= i < self.height and 0 <= j < self.width:
            self.grid[i, j] = not self.grid[i, j]
            
    def clear(self) -> None:
        """清空网格"""
        self.grid.fill(0)
        
    def randomize(self) -> None:
        """随机填充网格"""
        self.grid = np.random.choice([0, 1], size=(self.height, self.width), p=[0.85, 0.15])

    def undo(self) -> bool:
        """撤销上一步"""
        if self.history:
            self.grid = self.history.pop()
            self.generation -= 1
            return True
        return False
        
    def get_statistics(self) -> dict:
        """获取游戏统计信息"""
        return {
            "generation": self.generation,
            "alive_cells": np.sum(self.grid),
            "total_cells": self.width * self.height,
            "density": np.sum(self.grid) / (self.width * self.height)
        }

class GameView(QGraphicsView):
    """游戏显示和交互控制类"""
    
    cell_clicked = Signal(int, int, bool)  # 发送单元格点击信号(行,列,是否为左键)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.cell_size = 20
        self.grid_color = QColor(50, 50, 50)
        self.cell_color = QColor(255, 255, 255)
        self.show_grid = True
        self._last_pan_pos = None
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # 启用拖拽
        
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        
    def draw_grid(self, game: GameOfLife) -> None:
        """绘制游戏网格"""
        self.scene().clear()
        
        for i in range(game.height):
            for j in range(game.width):
                if game.grid[i, j]:
                    self.scene().addRect(
                        j * self.cell_size,
                        i * self.cell_size,
                        self.cell_size - 1,
                        self.cell_size - 1,
                        QPen(Qt.NoPen),
                        QBrush(self.cell_color)
                    )
                    
        if self.show_grid:
            pen = QPen(self.grid_color)
            for i in range(game.height + 1):
                self.scene().addLine(
                    0, i * self.cell_size,
                    game.width * self.cell_size, i * self.cell_size,
                    pen
                )
            for j in range(game.width + 1):
                self.scene().addLine(
                    j * self.cell_size, 0,
                    j * self.cell_size, game.height * self.cell_size,
                    pen
                )
                
        self.setSceneRect(QRectF(0, 0,
                                game.width * self.cell_size,
                                game.height * self.cell_size))
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        pos = self.mapToScene(event.position().toPoint())
        i = int(pos.y() // self.cell_size)
        j = int(pos.x() // self.cell_size)
        self.cell_clicked.emit(i, j, event.button() == Qt.LeftButton)
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if event.buttons() & (Qt.LeftButton | Qt.RightButton):
            pos = self.mapToScene(event.position().toPoint())
            i = int(pos.y() // self.cell_size)
            j = int(pos.x() // self.cell_size)
            self.cell_clicked.emit(i, j, event.buttons() & Qt.LeftButton)
            
    def wheelEvent(self, event):
        """处理滚轮缩放事件"""
        if event.angleDelta().y() > 0:
            self.cell_size = min(50, self.cell_size + 2)
        else:
            self.cell_size = max(5, self.cell_size - 2)

    def draw_statistics(self, stats: dict) -> None:
        """绘制统计信息"""
        text = (f"代数: {stats['generation']}\n"
                f"存活: {stats['alive_cells']}\n"
                f"密度: {stats['density']:.2%}")
        
        self.scene().addText(text, QFont("Microsoft YaHei UI", 10))

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conway's Game of Life")
        self.game = GameOfLife()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.setup_ui()
        self.init_patterns()  # 初始化预设图案
        self.init_menubar()   # 添加菜单栏
        
    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 游戏视图
        self.view = GameView()
        self.view.cell_clicked.connect(self.handle_cell_click)
        layout.addWidget(self.view)
        
        # 控制面板
        control_panel = QHBoxLayout()
        
        # 开始/暂停按钮
        self.play_button = QPushButton("开始")
        self.play_button.clicked.connect(self.toggle_game)
        control_panel.addWidget(self.play_button)
        
        # 清空按钮
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_game)
        control_panel.addWidget(clear_button)
        
        # 随机填充按钮
        random_button = QPushButton("随机")
        random_button.clicked.connect(self.randomize_game)
        control_panel.addWidget(random_button)
        
        # 速度控制
        control_panel.addWidget(QLabel("速度:"))
        speed_spin = QSpinBox()
        speed_spin.setRange(50, 1000)
        speed_spin.setSingleStep(50)
        speed_spin.setValue(200)
        speed_spin.valueChanged.connect(lambda v: self.timer.setInterval(v))
        control_panel.addWidget(speed_spin)
        
        # 网格显示切换
        grid_button = QPushButton("网格")
        grid_button.setCheckable(True)
        grid_button.setChecked(True)
        grid_button.clicked.connect(self.toggle_grid)
        control_panel.addWidget(grid_button)
        
        # 颜色选择
        color_button = QPushButton("颜色")
        color_button.clicked.connect(self.choose_color)
        control_panel.addWidget(color_button)
        
        control_panel.addStretch()
        layout.addLayout(control_panel)
        
        # 初始化显示
        self.view.draw_grid(self.game)
        self.resize(800, 600)
        
    def init_patterns(self):
        """初始化预设图案"""
        self.patterns = {
            "滑翔机": Pattern("滑翔机", np.array([
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1]
            ]), "会在空间中移动的最小图案"),
            "方块": Pattern("方块", np.array([
                [1, 1],
                [1, 1]
            ]), "稳定的静态图案"),
            "信标": Pattern("信标", np.array([
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1]
            ]), "两个方块交替闪烁的图案"),
            "蜂巢": Pattern("蜂巢", np.array([
                [0, 1, 1, 0],
                [1, 0, 0, 1],
                [0, 1, 1, 0]
            ]), "稳定的静态图案")
        }
        
    def init_menubar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        new_action = file_menu.addAction("新游戏")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_game)
        file_menu.addSeparator()
        
        save_action = file_menu.addAction("保存状态")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_state)
        
        load_action = file_menu.addAction("加载状态")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_state)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        undo_action = edit_menu.addAction("撤销")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        stats_action = view_menu.addAction("显示统计")
        stats_action.setCheckable(True)
        stats_action.toggled.connect(self.toggle_statistics)
        
        # 图案菜单
        pattern_menu = menubar.addMenu("图案")
        for name, pattern in self.patterns.items():
            action = pattern_menu.addAction(name)
            action.triggered.connect(lambda checked, p=pattern: self.apply_pattern(p))
            
    def new_game(self):
        """开始新游戏"""
        self.game = GameOfLife()  # 创建新的游戏实例
        self.timer.stop()  # 停止当前计时器
        self.play_button.setText("开始")
        self.view.draw_grid(self.game)  # 重新绘制网格
        self.statusBar().showMessage("新游戏已开始")

    def save_state(self):
        """保存当前状态"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存游戏状态", "", "NumPy Files (*.npy)")
        if filename:
            np.save(filename, self.game.grid)
            
    def load_state(self):
        """加载状态"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载游戏状态", "", "NumPy Files (*.npy)")
        if filename:
            self.game.grid = np.load(filename)
            self.view.draw_grid(self.game)
            
    def apply_pattern(self, pattern: Pattern):
        """应用预设图案"""
        if not isinstance(pattern, Pattern):
            return
            
        # 获取视图中心位置
        center = self.view.mapToScene(self.view.viewport().rect().center())
        i = int(center.y() // self.view.cell_size)
        j = int(center.x() // self.view.cell_size)
        
        # 计算图案的偏移量，使其居中放置
        height, width = pattern.pattern.shape
        i -= height // 2
        j -= width // 2
        
        # 确保在网格范围内
        i = max(0, min(i, self.game.height - height))
        j = max(0, min(j, self.game.width - width))
        
        # 应用图案
        self.game.grid[i:i+height, j:j+width] = pattern.pattern
        self.view.draw_grid(self.game)
        
    def update_game(self):
        """更新游戏状态"""
        self.game.update()
        self.view.draw_grid(self.game)
        self.update_status_bar()
        
    def toggle_game(self):
        """切换游戏运行状态"""
        if self.timer.isActive():
            self.timer.stop()
            self.play_button.setText("开始")
        else:
            self.timer.start(200)
            self.play_button.setText("暂停")
            
    def handle_cell_click(self, i: int, j: int, is_left: bool):
        """处理单元格点击事件"""
        if is_left:
            self.game.grid[i, j] = 1
        else:
            self.game.grid[i, j] = 0
        self.view.draw_grid(self.game)
        
    def clear_game(self):
        """清空游戏"""
        self.game.clear()
        self.view.draw_grid(self.game)
        
    def randomize_game(self):
        """随机填充"""
        self.game.randomize()
        self.view.draw_grid(self.game)
        
    def toggle_grid(self, show: bool):
        """切换网格显示"""
        self.view.show_grid = show
        self.view.draw_grid(self.game)
        
    def choose_color(self):
        """选择细胞颜色"""
        color = QColorDialog.getColor(self.view.cell_color, self)
        if color.isValid():
            self.view.cell_color = color
            self.view.draw_grid(self.game)
            
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key_Space:
            self.toggle_game()
        elif event.key() == Qt.Key_R:
            self.clear_game()
        elif event.key() == Qt.Key_G:
            self.view.show_grid = not self.view.show_grid
            self.view.draw_grid(self.game)
        elif event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
            self.new_game()
        super().keyPressEvent(event)

    def toggle_statistics(self, show: bool):
        """切换统计信息显示"""
        self.view.draw_statistics(self.game.get_statistics())

    def undo_action(self):
        """执行撤销操作"""
        if self.game.undo():
            self.view.draw_grid(self.game)
            stats = self.game.get_statistics()
            self.statusBar().showMessage(
                f"代数: {stats['generation']} | "
                f"存活: {stats['alive_cells']} | "
                f"密度: {stats['density']:.2%}"
            )

    def update_status_bar(self):
        """更新状态栏信息"""
        stats = self.game.get_statistics()
        status_text = (
            f"代数: {stats['generation']} | "
            f"存活: {stats['alive_cells']} | "
            f"密度: {stats['density']:.2%} | "
            f"网格大小: {self.game.width}x{self.game.height}"
        )
        self.statusBar().showMessage(status_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 