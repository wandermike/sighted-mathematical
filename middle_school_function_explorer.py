import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MiddleSchoolFunctionExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("二次函数探索器")
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
            text="函数可视化",
            font=("SimHei", 24, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(side=tk.LEFT)
        
        # 创建左侧控制面板
        self.left_panel = tk.Frame(self.main_frame, bg=self.bg_navy, width=350)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=0)
        self.left_panel.pack_propagate(False)
        
        # 创建右侧可视化区域
        self.right_panel = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置控制面板
        self.setup_control_panel()
        
        # 设置可视化区域
        self.setup_visualization()
        
        # 初始绘图
        self.update_plot()
    
    def setup_control_panel(self):
        """设置左侧控制面板"""
        # 添加面板标题
        panel_title = tk.Label(
            self.left_panel,
            text="函数设置",
            font=("SimHei", 16, "bold"),
            bg=self.bg_navy,
            fg=self.text_white,
            pady=10
        )
        panel_title.pack(fill=tk.X)
        
        # 添加分隔线
        separator = tk.Frame(self.left_panel, height=2, bg=self.accent_green)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # 函数类型选择
        function_frame = tk.LabelFrame(
            self.left_panel,
            text="选择函数类型",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        function_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 函数类型单选按钮
        self.function_type = tk.StringVar(value="quadratic")
        
        quadratic_radio = tk.Radiobutton(
            function_frame,
            text="二次函数 (y = ax² + bx + c)",
            variable=self.function_type,
            value="quadratic",
            command=self.update_plot,
            bg=self.bg_navy,
            fg=self.text_white,
            selectcolor=self.bg_navy,
            font=("SimHei", 11)
        )
        quadratic_radio.pack(anchor=tk.W, pady=2)
        
        linear_radio = tk.Radiobutton(
            function_frame,
            text="一次函数 (y = mx + b)",
            variable=self.function_type,
            value="linear",
            command=self.update_plot,
            bg=self.bg_navy,
            fg=self.text_white,
            selectcolor=self.bg_navy,
            font=("SimHei", 11)
        )
        linear_radio.pack(anchor=tk.W, pady=2)
        
        # 参数设置框架
        params_frame = tk.LabelFrame(
            self.left_panel,
            text="参数设置",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 参数 a（二次项系数）
        a_frame = tk.Frame(params_frame, bg=self.bg_navy)
        a_frame.pack(fill=tk.X, pady=5)
        
        a_label = tk.Label(
            a_frame,
            text="参数 a：",
            bg=self.bg_navy,
            fg=self.text_white,
            width=8,
            anchor=tk.W
        )
        a_label.pack(side=tk.LEFT)
        
        self.a_value = tk.DoubleVar(value=1.0)
        a_scale = ttk.Scale(
            a_frame,
            from_=-5.0,
            to=5.0,
            variable=self.a_value,
            command=lambda _: self.update_plot()
        )
        a_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        a_spinbox = tk.Spinbox(
            a_frame,
            from_=-5.0,
            to=5.0,
            increment=0.1,
            textvariable=self.a_value,
            command=self.update_plot,
            width=5
        )
        a_spinbox.pack(side=tk.LEFT)
        
        # 参数 b（一次项系数）
        b_frame = tk.Frame(params_frame, bg=self.bg_navy)
        b_frame.pack(fill=tk.X, pady=5)
        
        b_label = tk.Label(
            b_frame,
            text="参数 b：",
            bg=self.bg_navy,
            fg=self.text_white,
            width=8,
            anchor=tk.W
        )
        b_label.pack(side=tk.LEFT)
        
        self.b_value = tk.DoubleVar(value=0.0)
        b_scale = ttk.Scale(
            b_frame,
            from_=-5.0,
            to=5.0,
            variable=self.b_value,
            command=lambda _: self.update_plot()
        )
        b_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        b_spinbox = tk.Spinbox(
            b_frame,
            from_=-5.0,
            to=5.0,
            increment=0.1,
            textvariable=self.b_value,
            command=self.update_plot,
            width=5
        )
        b_spinbox.pack(side=tk.LEFT)
        
        # 参数 c（常数项）
        c_frame = tk.Frame(params_frame, bg=self.bg_navy)
        c_frame.pack(fill=tk.X, pady=5)
        
        c_label = tk.Label(
            c_frame,
            text="参数 c：",
            bg=self.bg_navy,
            fg=self.text_white,
            width=8,
            anchor=tk.W
        )
        c_label.pack(side=tk.LEFT)
        
        self.c_value = tk.DoubleVar(value=0.0)
        c_scale = ttk.Scale(
            c_frame,
            from_=-5.0,
            to=5.0,
            variable=self.c_value,
            command=lambda _: self.update_plot()
        )
        c_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        c_spinbox = tk.Spinbox(
            c_frame,
            from_=-5.0,
            to=5.0,
            increment=0.1,
            textvariable=self.c_value,
            command=self.update_plot,
            width=5
        )
        c_spinbox.pack(side=tk.LEFT)
        
        # 显示设置框架
        display_frame = tk.LabelFrame(
            self.left_panel,
            text="显示设置",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 显示网格
        self.show_grid = tk.BooleanVar(value=True)
        grid_check = tk.Checkbutton(
            display_frame,
            text="显示网格",
            variable=self.show_grid,
            command=self.update_plot,
            bg=self.bg_navy,
            fg=self.text_white,
            selectcolor=self.bg_navy,
            font=("SimHei", 11)
        )
        grid_check.pack(anchor=tk.W, pady=2)
        
        # 显示顶点
        self.show_vertex = tk.BooleanVar(value=True)
        vertex_check = tk.Checkbutton(
            display_frame,
            text="显示顶点",
            variable=self.show_vertex,
            command=self.update_plot,
            bg=self.bg_navy,
            fg=self.text_white,
            selectcolor=self.bg_navy,
            font=("SimHei", 11)
        )
        vertex_check.pack(anchor=tk.W, pady=2)
        
        # 显示零点
        self.show_roots = tk.BooleanVar(value=True)
        roots_check = tk.Checkbutton(
            display_frame,
            text="显示零点",
            variable=self.show_roots,
            command=self.update_plot,
            bg=self.bg_navy,
            fg=self.text_white,
            selectcolor=self.bg_navy,
            font=("SimHei", 11)
        )
        roots_check.pack(anchor=tk.W, pady=2)
        
        # 按钮框架
        button_frame = tk.Frame(self.left_panel, bg=self.bg_navy)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        # 重置按钮
        reset_button = tk.Button(
            button_frame,
            text="重置",
            command=self.reset_parameters,
            bg=self.accent_green,
            fg=self.text_white,
            font=("SimHei", 12),
            padx=15,
            pady=5
        )
        reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存按钮
        save_button = tk.Button(
            button_frame,
            text="保存图像",
            command=self.save_plot,
            bg=self.accent_green,
            fg=self.text_white,
            font=("SimHei", 12),
            padx=15,
            pady=5
        )
        save_button.pack(side=tk.LEFT)
        
        # 信息框架
        info_frame = tk.LabelFrame(
            self.left_panel,
            text="函数信息",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 函数表达式
        self.function_info = tk.Label(
            info_frame,
            text="函数: y = x²",
            bg=self.bg_navy,
            fg=self.text_white,
            font=("SimHei", 11),
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.function_info.pack(fill=tk.X, pady=(0, 10))
        
        # 顶点信息
        self.vertex_info = tk.Label(
            info_frame,
            text="顶点: (0, 0)",
            bg=self.bg_navy,
            fg=self.text_white,
            font=("SimHei", 11),
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.vertex_info.pack(fill=tk.X, pady=2)
        
        # 零点信息
        self.roots_info = tk.Label(
            info_frame,
            text="零点: x = 0",
            bg=self.bg_navy,
            fg=self.text_white,
            font=("SimHei", 11),
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.roots_info.pack(fill=tk.X, pady=2)
        
        # 对称轴信息
        self.axis_info = tk.Label(
            info_frame,
            text="对称轴: x = 0",
            bg=self.bg_navy,
            fg=self.text_white,
            font=("SimHei", 11),
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.axis_info.pack(fill=tk.X, pady=2)
    
    def setup_visualization(self):
        """设置右侧可视化区域"""
        # 创建 Matplotlib 图形
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.fig.patch.set_facecolor(self.bg_dark_blue)
        self.ax.set_facecolor(self.bg_dark_blue)
        
        # 设置标题和标签
        self.ax.set_title("函数图像", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.ax.set_xlabel("x", color=self.text_white, fontsize=12)
        self.ax.set_ylabel("y", color=self.text_white, fontsize=12)
        
        # 设置网格
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # 设置刻度标签颜色
        self.ax.tick_params(axis='x', colors=self.text_white)
        self.ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.ax.spines.values():
            spine.set_color(self.text_white)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 设置图形大小调整事件
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
    
    def update_plot(self):
        """更新函数图像"""
        # 清除当前图像
        self.ax.clear()
        
        # 获取参数值
        a = self.a_value.get()
        b = self.b_value.get()
        c = self.c_value.get()
        
        # 生成 x 值
        x = np.linspace(-5, 5, 1000)
        
        # 计算 y 值
        if self.function_type.get() == "quadratic":
            y = a * x**2 + b * x + c
            formula = f"y = {a:.1f}x² + {b:.1f}x + {c:.1f}"
            
            # 计算顶点
            x_vertex = -b / (2 * a) if a != 0 else 0
            y_vertex = a * x_vertex**2 + b * x_vertex + c
            
            # 计算零点
            if a == 0:
                if b == 0:
                    if c == 0:
                        roots_text = "零点: x 为任意实数"
                    else:
                        roots_text = "零点: 无"
                else:
                    x_root = -c / b
                    roots_text = f"零点: x = {x_root:.2f}"
            else:
                discriminant = b**2 - 4 * a * c
                if discriminant > 0:
                    x_root1 = (-b + np.sqrt(discriminant)) / (2 * a)
                    x_root2 = (-b - np.sqrt(discriminant)) / (2 * a)
                    roots_text = f"零点: x₁ = {x_root1:.2f}, x₂ = {x_root2:.2f}"
                elif discriminant == 0:
                    x_root = -b / (2 * a)
                    roots_text = f"零点: x = {x_root:.2f} (重根)"
                else:
                    roots_text = "零点: 无实数解"
            
            # 对称轴
            axis_text = f"对称轴: x = {x_vertex:.2f}"
            
        else:  # 一次函数
            y = b * x + c
            formula = f"y = {b:.1f}x + {c:.1f}"
            
            # 一次函数没有顶点
            x_vertex = None
            y_vertex = None
            
            # 零点
            if b == 0:
                if c == 0:
                    roots_text = "零点: x 为任意实数"
                else:
                    roots_text = "零点: 无"
            else:
                x_root = -c / b
                roots_text = f"零点: x = {x_root:.2f}"
            
            # 一次函数没有对称轴
            axis_text = "对称轴: 无"
        
        # 绘制函数
        self.ax.plot(x, y, color=self.accent_green, linewidth=2)
        
        # 绘制坐标轴
        self.ax.axhline(y=0, color=self.text_white, linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color=self.text_white, linestyle='-', alpha=0.3)
        
        # 设置显示范围
        self.ax.set_xlim(-5, 5)
        
        if self.function_type.get() == "quadratic":
            if a > 0:
                self.ax.set_ylim(min(-5, c - 1), max(10, a * 25 + b * 5 + c + 1))
            else:
                self.ax.set_ylim(min(-10, a * 25 - b * 5 + c - 1), max(5, c + 1))
        else:
            self.ax.set_ylim(min(-10, b * (-5) + c - 1), max(10, b * 5 + c + 1))
        
        # 设置网格
        self.ax.grid(self.show_grid.get(), linestyle='--', alpha=0.7)
        
        # 设置标题和标签
        self.ax.set_title("函数图像", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.ax.set_xlabel("x", color=self.text_white, fontsize=12)
        self.ax.set_ylabel("y", color=self.text_white, fontsize=12)
        
        # 设置刻度标签颜色
        self.ax.tick_params(axis='x', colors=self.text_white)
        self.ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.ax.spines.values():
            spine.set_color(self.text_white)
        
        # 显示顶点
        if self.show_vertex.get() and self.function_type.get() == "quadratic" and x_vertex is not None:
            self.ax.plot(x_vertex, y_vertex, 'ro', markersize=8)
            self.ax.annotate(f"({x_vertex:.2f}, {y_vertex:.2f})",
                            xy=(x_vertex, y_vertex),
                            xytext=(x_vertex + 0.5, y_vertex + 0.5),
                            color=self.text_white,
                            arrowprops=dict(facecolor=self.text_white, shrink=0.05))
        
        # 显示零点
        if self.show_roots.get() and "无" not in roots_text and "任意" not in roots_text:
            if self.function_type.get() == "quadratic":
                if "重根" in roots_text:
                    x_root = -b / (2 * a)
                    self.ax.plot(x_root, 0, 'bo', markersize=8)
                    self.ax.annotate(f"({x_root:.2f}, 0)",
                                    xy=(x_root, 0),
                                    xytext=(x_root + 0.5, 0.5),
                                    color=self.text_white,
                                    arrowprops=dict(facecolor=self.text_white, shrink=0.05))
                elif "x₁" in roots_text:
                    discriminant = b**2 - 4 * a * c
                    x_root1 = (-b + np.sqrt(discriminant)) / (2 * a)
                    x_root2 = (-b - np.sqrt(discriminant)) / (2 * a)
                    
                    self.ax.plot(x_root1, 0, 'bo', markersize=8)
                    self.ax.annotate(f"({x_root1:.2f}, 0)",
                                    xy=(x_root1, 0),
                                    xytext=(x_root1 + 0.5, 0.5),
                                    color=self.text_white,
                                    arrowprops=dict(facecolor=self.text_white, shrink=0.05))
                    
                    self.ax.plot(x_root2, 0, 'bo', markersize=8)
                    self.ax.annotate(f"({x_root2:.2f}, 0)",
                                    xy=(x_root2, 0),
                                    xytext=(x_root2 - 0.5, 0.5),
                                    color=self.text_white,
                                    arrowprops=dict(facecolor=self.text_white, shrink=0.05))
            else:  # 一次函数
                if b != 0:
                    x_root = -c / b
                    self.ax.plot(x_root, 0, 'bo', markersize=8)
                    self.ax.annotate(f"({x_root:.2f}, 0)",
                                    xy=(x_root, 0),
                                    xytext=(x_root + 0.5, 0.5),
                                    color=self.text_white,
                                    arrowprops=dict(facecolor=self.text_white, shrink=0.05))
        
        # 更新信息
        self.function_info.config(text=f"函数: {formula}")
        
        if self.function_type.get() == "quadratic" and x_vertex is not None:
            self.vertex_info.config(text=f"顶点: ({x_vertex:.2f}, {y_vertex:.2f})")
        else:
            self.vertex_info.config(text="顶点: 无")
            
        self.roots_info.config(text=roots_text)
        self.axis_info.config(text=axis_text)
        
        # 更新画布
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
    
    def reset_parameters(self):
        """重置所有参数到默认值"""
        self.function_type.set("quadratic")
        self.a_value.set(1.0)
        self.b_value.set(0.0)
        self.c_value.set(0.0)
        self.show_grid.set(True)
        self.show_vertex.set(True)
        self.show_roots.set(True)
        self.update_plot()
    
    def save_plot(self):
        """保存当前图像"""
        try:
            if not os.path.exists("images"):
                os.makedirs("images")
            
            # 生成文件名
            if self.function_type.get() == "quadratic":
                a = self.a_value.get()
                b = self.b_value.get()
                c = self.c_value.get()
                filename = f"images/quadratic_a{a:.1f}_b{b:.1f}_c{c:.1f}.png"
            else:
                b = self.b_value.get()
                c = self.c_value.get()
                filename = f"images/linear_m{b:.1f}_b{c:.1f}.png"
            
            # 保存图像
            self.fig.savefig(filename, facecolor=self.bg_dark_blue)
            messagebox.showinfo("保存成功", f"图像已保存为: {filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存图像时出错: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MiddleSchoolFunctionExplorer(root)
    root.mainloop() 