import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Rectangle, Polygon
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MiddleSchoolGeometry:
    def __init__(self, root):
        self.root = root
        self.root.title("几何图形可视化")
        self.root.geometry("1000x650")
        
        # 定义颜色
        self.bg_dark_blue = "#1A3665"    # 深蓝色背景
        self.bg_navy = "#223C6A"         # 海军蓝用于控件
        self.accent_green = "#2ECC71"    # 绿色强调色
        self.text_white = "#FFFFFF"      # 白色文本
        self.text_light = "#D0D0D0"      # 浅灰色文本
        
        # 设置背景颜色
        self.root.config(bg=self.bg_dark_blue)
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg=self.bg_dark_blue)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_frame = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="几何图形可视化",
            font=("SimHei", 24, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(side=tk.LEFT)
        
        # 创建左侧面板
        self.left_panel = tk.Frame(self.main_frame, bg=self.bg_navy, width=280)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=0)
        self.left_panel.pack_propagate(False)
        
        # 创建右侧可视化区域
        self.right_panel = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置左侧面板内容
        self.setup_left_panel()
        
        # 设置右侧面板内容
        self.setup_visualization()
    
    def setup_left_panel(self):
        """设置左侧面板内容"""
        # 添加面板标题
        panel_title = tk.Label(
            self.left_panel,
            text="图形信息",
            font=("SimHei", 16, "bold"),
            bg=self.bg_navy,
            fg=self.text_white,
            pady=10
        )
        panel_title.pack(fill=tk.X)
        
        # 添加分隔线
        separator = tk.Frame(self.left_panel, height=2, bg=self.accent_green)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加各个几何图形的信息框架
        self.create_shape_info("三角形", "三条边和三个内角的封闭多边形", "三角形的内角和为180°", "三边满足：任意两边之和大于第三边", "特殊三角形：等边三角形、等腰三角形、直角三角形")
        
        self.create_shape_info("矩形", "四边都是直角的四边形", "对边平行且相等", "对角线相等且互相平分", "特殊矩形：正方形（四边相等）")
        
        self.create_shape_info("圆形", "到定点（圆心）距离相等的点的集合", "圆的周长 = 2πr", "圆的面积 = πr²", "r是圆的半径")
        
        # 添加提示窗口
        tip_frame = tk.LabelFrame(
            self.left_panel,
            text="学习提示",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        tip_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tip_text = """
几何图形是研究空间形状、大小和位置的基础。

通过观察几何图形的特性，我们可以发现规律，解决现实生活中的问题。

尝试思考：如何利用这些图形的性质来设计建筑物？
        """
        
        tip_label = tk.Label(
            tip_frame,
            text=tip_text,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.accent_green,
            justify=tk.LEFT,
            wraplength=250
        )
        tip_label.pack(fill=tk.BOTH)
    
    def create_shape_info(self, title, desc1, desc2, desc3=None, desc4=None):
        """创建几何图形信息框"""
        info_frame = tk.LabelFrame(
            self.left_panel,
            text=title,
            font=("SimHei", 12, "bold"),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加描述文本
        desc_label1 = tk.Label(
            info_frame,
            text="• " + desc1,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white,
            justify=tk.LEFT,
            wraplength=250,
            anchor="w"
        )
        desc_label1.pack(fill=tk.X, pady=2, anchor="w")
        
        desc_label2 = tk.Label(
            info_frame,
            text="• " + desc2,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white,
            justify=tk.LEFT,
            wraplength=250,
            anchor="w"
        )
        desc_label2.pack(fill=tk.X, pady=2, anchor="w")
        
        if desc3:
            desc_label3 = tk.Label(
                info_frame,
                text="• " + desc3,
                font=("SimHei", 11),
                bg=self.bg_navy,
                fg=self.text_white,
                justify=tk.LEFT,
                wraplength=250,
                anchor="w"
            )
            desc_label3.pack(fill=tk.X, pady=2, anchor="w")
        
        if desc4:
            desc_label4 = tk.Label(
                info_frame,
                text="• " + desc4,
                font=("SimHei", 11),
                bg=self.bg_navy,
                fg=self.text_white,
                justify=tk.LEFT,
                wraplength=250,
                anchor="w"
            )
            desc_label4.pack(fill=tk.X, pady=2, anchor="w")
    
    def setup_visualization(self):
        """设置右侧可视化区域"""
        # 创建 2x2 网格的框架
        self.grid_frame = tk.Frame(self.right_panel, bg=self.bg_dark_blue)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置网格权重
        for i in range(2):
            self.grid_frame.columnconfigure(i, weight=1)
            self.grid_frame.rowconfigure(i, weight=1)
        
        # 创建四个图形区域
        self.create_triangle_plot(0, 0)
        self.create_rectangle_plot(0, 1)
        self.create_circle_plot(1, 0)
        self.create_complex_shapes_plot(1, 1)
    
    def create_triangle_plot(self, row, col):
        """创建三角形可视化"""
        # 创建框架
        frame = tk.Frame(self.grid_frame, bg=self.bg_dark_blue, padx=10, pady=10)
        frame.grid(row=row, column=col, sticky="nsew")
        
        # 创建标题
        title_label = tk.Label(
            frame,
            text="三角形",
            font=("SimHei", 14, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(pady=(0, 5))
        
        # 创建 Matplotlib 图形
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor(self.bg_dark_blue)
        ax.set_facecolor(self.bg_dark_blue)
        
        # 设置图形范围
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        
        # 绘制三种三角形
        # 等边三角形
        eq_triangle = Polygon([(2, 1), (4, 1), (3, 1+np.sqrt(3))], 
                              closed=True, fill=True, color='#3498DB', alpha=0.7)
        ax.add_patch(eq_triangle)
        ax.text(3, 0.5, "等边三角形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 等腰三角形
        iso_triangle = Polygon([(6, 1), (8, 1), (7, 3.5)], 
                               closed=True, fill=True, color='#E74C3C', alpha=0.7)
        ax.add_patch(iso_triangle)
        ax.text(7, 0.5, "等腰三角形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 直角三角形
        right_triangle = Polygon([(3, 4), (3, 6), (7, 4)], 
                                 closed=True, fill=True, color=self.accent_green, alpha=0.7)
        ax.add_patch(right_triangle)
        # 直角符号
        ax.plot([3.3, 3.3], [4, 4.3], color='white', linewidth=1)
        ax.plot([3, 3.3], [4.3, 4.3], color='white', linewidth=1)
        ax.text(5, 4.7, "直角三角形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 去除坐标轴
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 设置图形边框颜色
        for spine in ax.spines.values():
            spine.set_color(self.text_white)
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def create_rectangle_plot(self, row, col):
        """创建矩形可视化"""
        # 创建框架
        frame = tk.Frame(self.grid_frame, bg=self.bg_dark_blue, padx=10, pady=10)
        frame.grid(row=row, column=col, sticky="nsew")
        
        # 创建标题
        title_label = tk.Label(
            frame,
            text="矩形",
            font=("SimHei", 14, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(pady=(0, 5))
        
        # 创建 Matplotlib 图形
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor(self.bg_dark_blue)
        ax.set_facecolor(self.bg_dark_blue)
        
        # 设置图形范围
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        
        # 绘制矩形
        rectangle = Rectangle((1.5, 1), 3, 2, fill=True, color='#3498DB', alpha=0.7)
        ax.add_patch(rectangle)
        ax.text(3, 0.5, "矩形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制正方形
        square = Rectangle((6, 1), 2, 2, fill=True, color='#E74C3C', alpha=0.7)
        ax.add_patch(square)
        ax.text(7, 0.5, "正方形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制平行四边形
        parallelogram = Polygon([(3, 4), (6, 4), (7, 6), (4, 6)], 
                               closed=True, fill=True, color=self.accent_green, alpha=0.7)
        ax.add_patch(parallelogram)
        ax.text(5, 6.5, "平行四边形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 去除坐标轴
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 设置图形边框颜色
        for spine in ax.spines.values():
            spine.set_color(self.text_white)
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def create_circle_plot(self, row, col):
        """创建圆形可视化"""
        # 创建框架
        frame = tk.Frame(self.grid_frame, bg=self.bg_dark_blue, padx=10, pady=10)
        frame.grid(row=row, column=col, sticky="nsew")
        
        # 创建标题
        title_label = tk.Label(
            frame,
            text="圆形",
            font=("SimHei", 14, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(pady=(0, 5))
        
        # 创建 Matplotlib 图形
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor(self.bg_dark_blue)
        ax.set_facecolor(self.bg_dark_blue)
        
        # 设置图形范围
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        
        # 绘制圆形
        circle = Circle((5, 4), 2.5, fill=True, color='#3498DB', alpha=0.5)
        ax.add_patch(circle)
        
        # 绘制半径
        ax.plot([5, 5], [4, 6.5], color='white', linestyle='--')
        ax.text(5.2, 5.3, "r", color=self.text_white, fontsize=10)
        
        # 绘制直径
        ax.plot([2.5, 7.5], [4, 4], color='white', linestyle='--')
        ax.text(5, 4.2, "d = 2r", color=self.text_white, fontsize=10)
        
        # 添加面积和周长公式
        ax.text(5, 2, "面积 = πr²", ha='center', color=self.text_white, fontsize=10, fontfamily='SimHei')
        ax.text(5, 1, "周长 = 2πr", ha='center', color=self.text_white, fontsize=10, fontfamily='SimHei')
        
        # 去除坐标轴
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 设置图形边框颜色
        for spine in ax.spines.values():
            spine.set_color(self.text_white)
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def create_complex_shapes_plot(self, row, col):
        """创建复合图形可视化"""
        # 创建框架
        frame = tk.Frame(self.grid_frame, bg=self.bg_dark_blue, padx=10, pady=10)
        frame.grid(row=row, column=col, sticky="nsew")
        
        # 创建标题
        title_label = tk.Label(
            frame,
            text="几何变换",
            font=("SimHei", 14, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(pady=(0, 5))
        
        # 创建 Matplotlib 图形
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor(self.bg_dark_blue)
        ax.set_facecolor(self.bg_dark_blue)
        
        # 设置图形范围
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        
        # 绘制原始三角形
        triangle1 = Polygon([(2, 3), (4, 3), (3, 5)], 
                          closed=True, fill=True, color='#3498DB', alpha=0.7)
        ax.add_patch(triangle1)
        ax.text(3, 2.5, "原图形", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制平移后的三角形
        triangle2 = Polygon([(5, 3), (7, 3), (6, 5)], 
                          closed=True, fill=True, color='#E74C3C', alpha=0.7)
        ax.add_patch(triangle2)
        ax.text(6, 2.5, "平移", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制旋转后的三角形
        triangle3 = Polygon([(2, 6), (2, 7), (4, 6.5)], 
                          closed=True, fill=True, color=self.accent_green, alpha=0.7)
        ax.add_patch(triangle3)
        ax.text(3, 7.5, "旋转", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制缩放后的三角形
        triangle4 = Polygon([(6, 6), (9, 6), (7.5, 7.5)], 
                          closed=True, fill=True, color='#9B59B6', alpha=0.7)
        ax.add_patch(triangle4)
        ax.text(7.5, 5.5, "缩放", ha='center', color=self.text_white, fontsize=9, fontfamily='SimHei')
        
        # 绘制变换箭头
        ax.annotate("", xy=(4.8, 4), xytext=(4.2, 4),
                   arrowprops=dict(arrowstyle="->", color=self.text_white))
        
        ax.annotate("", xy=(3, 5.8), xytext=(3, 5.2),
                   arrowprops=dict(arrowstyle="->", color=self.text_white))
        
        ax.annotate("", xy=(5.8, 6.5), xytext=(4.2, 5.5),
                   arrowprops=dict(arrowstyle="->", color=self.text_white))
        
        # 去除坐标轴
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 设置图形边框颜色
        for spine in ax.spines.values():
            spine.set_color(self.text_white)
        
        # 创建画布
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = MiddleSchoolGeometry(root)
    root.mainloop() 