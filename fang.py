import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import warnings
from matplotlib import colors
from knowledge import KnowledgeLearningClass

# 配置 Matplotlib 以支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False  # 确保负号正确显示
matplotlib.rcParams['font.family'] = 'sans-serif'

# 忽略特定警告
warnings.filterwarnings("ignore", category=UserWarning, module='sympy')

class EquationVisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("方程可视化工具")
        self.root.geometry("1200x800")
        self.knowledge_learner = KnowledgeLearningClass()
        # 创建自定义颜色映射
        self.create_custom_colormaps()
        
        # 初始化变量
        self.equations = []  # 存储方程列表
        self.equation_lines = []  # 存储方程对应的线条
        self.equation_colors = []  # 存储方程对应的颜色
        self.current_mode = tk.StringVar(value="显式方程")
        self.x_range = tk.StringVar(value="-10,10")
        self.y_range = tk.StringVar(value="-10,10")
        self.resolution = tk.IntVar(value=500)
        self.show_grid = tk.BooleanVar(value=True)
        self.show_legend = tk.BooleanVar(value=True)
        self.line_width = tk.DoubleVar(value=2.0)
        self.colormap = tk.StringVar(value="viridis")
        self.alpha = tk.DoubleVar(value=0.8)
        self.animation_speed = tk.DoubleVar(value=1.0)
        
        # 创建UI
        self.create_ui()
        
        # 设置默认方程
        self.equation_entry.insert(0, "x**2")
        
        # 初始化绘图
        self.setup_plot()
        
        # 绑定事件
        self.bind_events()

        self.knowledge_learner = KnowledgeLearningClass()
        
    def create_custom_colormaps(self):
        """创建自定义颜色映射"""
        # 创建蓝红渐变色映射
        self.custom_cmap1 = colors.LinearSegmentedColormap.from_list(
            "BlueRed", [(0, "#1E88E5"), (0.5, "#FFFFFF"), (1, "#E53935")]
        )
        
        # 创建彩虹色映射
        self.custom_cmap2 = colors.LinearSegmentedColormap.from_list(
            "Rainbow", [(0, "#9C27B0"), (0.2, "#3F51B5"), (0.4, "#03A9F4"), 
                       (0.6, "#4CAF50"), (0.8, "#FFEB3B"), (1, "#FF5722")]
        )
        
        # 注册自定义颜色映射（兼容不同matplotlib版本）
        try:
            # 适用于 matplotlib >= 3.5
            from matplotlib import colormaps
            colormaps.register(cmap=self.custom_cmap1, name="BlueRed")
            colormaps.register(cmap=self.custom_cmap2, name="Rainbow")
        except AttributeError:
            # 回退到旧版注册方式
            plt.register_cmap(cmap=self.custom_cmap1)
            plt.register_cmap(cmap=self.custom_cmap2)
        
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 创建方程输入区域
        equation_frame = ttk.LabelFrame(control_frame, text="方程输入", padding=10)
        equation_frame.pack(fill=tk.X, pady=5)
        
        # 方程类型选择
        ttk.Label(equation_frame, text="方程类型:").grid(row=0, column=0, sticky=tk.W, pady=5)
        equation_types = ["显式方程", "隐式方程", "参数方程", "极坐标方程"]
        equation_type_combo = ttk.Combobox(equation_frame, textvariable=self.current_mode, values=equation_types)
        equation_type_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        equation_type_combo.bind("<<ComboboxSelected>>", self.on_equation_type_change)
        
        # 方程输入
        ttk.Label(equation_frame, text="输入方程:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.equation_entry = ttk.Entry(equation_frame, width=30)
        self.equation_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 添加方程按钮
        add_button = ttk.Button(equation_frame, text="添加方程", command=self.add_equation)
        add_button.grid(row=1, column=2, padx=5, pady=5)
        
        # 方程列表
        ttk.Label(equation_frame, text="方程列表:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.equation_listbox = tk.Listbox(equation_frame, height=5, width=40)
        self.equation_listbox.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # 删除方程按钮
        delete_button = ttk.Button(equation_frame, text="删除选中方程", command=self.delete_equation)
        delete_button.grid(row=3, column=1, pady=5)
        
        # 清空方程按钮
        clear_button = ttk.Button(equation_frame, text="清空所有方程", command=self.clear_equations)
        clear_button.grid(row=3, column=2, pady=5)
        
        # 创建显示设置区域
        display_frame = ttk.LabelFrame(control_frame, text="显示设置", padding=10)
        display_frame.pack(fill=tk.X, pady=10)
        
        # X范围设置
        ttk.Label(display_frame, text="X范围 (min,max):").grid(row=0, column=0, sticky=tk.W, pady=5)
        x_range_entry = ttk.Entry(display_frame, textvariable=self.x_range, width=15)
        x_range_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Y范围设置
        ttk.Label(display_frame, text="Y范围 (min,max):").grid(row=1, column=0, sticky=tk.W, pady=5)
        y_range_entry = ttk.Entry(display_frame, textvariable=self.y_range, width=15)
        y_range_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 分辨率设置
        ttk.Label(display_frame, text="分辨率:").grid(row=2, column=0, sticky=tk.W, pady=5)
        resolution_scale = ttk.Scale(display_frame, from_=100, to=1000, variable=self.resolution, orient=tk.HORIZONTAL)
        resolution_scale.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 线宽设置
        ttk.Label(display_frame, text="线宽:").grid(row=3, column=0, sticky=tk.W, pady=5)
        line_width_scale = ttk.Scale(display_frame, from_=0.5, to=5.0, variable=self.line_width, orient=tk.HORIZONTAL)
        line_width_scale.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 颜色映射选择
        ttk.Label(display_frame, text="颜色映射:").grid(row=4, column=0, sticky=tk.W, pady=5)
        colormap_values = ["viridis", "plasma", "inferno", "magma", "cividis", "BlueRed", "Rainbow"]
        colormap_combo = ttk.Combobox(display_frame, textvariable=self.colormap, values=colormap_values)
        colormap_combo.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 显示网格选项
        grid_check = ttk.Checkbutton(display_frame, text="显示网格", variable=self.show_grid)
        grid_check.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        # 显示图例选项
        legend_check = ttk.Checkbutton(display_frame, text="显示图例", variable=self.show_legend)
        legend_check.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 创建按钮区域
        button_frame = ttk.Frame(control_frame, padding=10)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 绘制按钮
        plot_button = ttk.Button(button_frame, text="绘制方程", command=self.plot_equations)
        plot_button.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        reset_button = ttk.Button(button_frame, text="重置视图", command=self.reset_view)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # 保存图像按钮
        save_button = ttk.Button(button_frame, text="保存图像", command=self.save_figure)
        save_button.pack(side=tk.LEFT, padx=5)

        knowledge_learning = ttk.Button(button_frame, text="知识介绍", command=self.knowledge_learner.knowledge_learning_7_function)
        knowledge_learning.pack(side=tk.LEFT,padx=5)
        
        # 创建右侧绘图区域
        self.plot_frame = ttk.LabelFrame(main_frame, text="方程可视化", padding=10)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建信息显示区域
        info_frame = ttk.LabelFrame(control_frame, text="方程信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
    def setup_plot(self):
        """设置绘图区域"""
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # 设置坐标轴标签
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('方程可视化')
        
        # 显示网格
        if self.show_grid.get():
            self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
    def bind_events(self):
        """绑定事件处理函数"""
        self.equation_listbox.bind('<<ListboxSelect>>', self.on_equation_select)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.current_mode.trace_add('write', self.on_equation_type_change)
        
    def on_equation_select(self, event):
        """处理方程列表选择事件"""
        selection = self.equation_listbox.curselection()
        if selection:
            index = selection[0]
            mode, equation, color = self.equations[index]
            self.current_mode.set(mode)
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, equation)
            self.status_var.set(f"已选择方程: {equation}")
    
    def on_equation_type_change(self, event=None):
        """处理方程类型变化"""
        mode = self.current_mode.get()
        if mode == "显式方程":
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, "x**2")
            self.update_info("显式方程形式: y = f(x)\n例如: x**2, sin(x), x**3-2*x")
        elif mode == "隐式方程":
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, "x**2 + y**2 - 4")
            self.update_info("隐式方程形式: f(x,y) = 0\n例如: x**2 + y**2 - 4, x*y - 1")
        elif mode == "参数方程":
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, "t*cos(t), t*sin(t), 0, 10")
            self.update_info("参数方程形式: x(t), y(t), t_min, t_max\n例如: cos(t), sin(t), 0, 2*pi")
        elif mode == "极坐标方程":
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, "1 + cos(theta)")
            self.update_info("极坐标方程形式: r = f(theta)\n例如: 1 + cos(theta), 2*sin(3*theta)")
    
    def add_equation(self):
        """添加方程到列表"""
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("输入错误", "请输入有效的方程")
            return
        
        # 生成随机颜色
        color = "#{:02x}{:02x}{:02x}".format(
            np.random.randint(0, 200), 
            np.random.randint(0, 200), 
            np.random.randint(0, 200)
        )
        
        # 添加方程和颜色
        mode = self.current_mode.get()
        equation_display = f"{mode}: {equation}"
        self.equations.append((mode, equation))
        self.equation_colors.append(color)
        
        # 更新列表框
        self.equation_listbox.insert(tk.END, equation_display)
        self.equation_listbox.itemconfig(tk.END, {'bg': color, 'fg': 'white'})
        
        # 清空输入框
        self.equation_entry.delete(0, tk.END)
        
        # 更新状态
        self.status_var.set(f"已添加方程: {equation_display}")
        
        # 自动绘制
        self.plot_equations()
    
    def delete_equation(self):
        """删除选中的方程"""
        selected = self.equation_listbox.curselection()
        if not selected:
            messagebox.showwarning("选择错误", "请先选择要删除的方程")
            return
        
        # 删除选中的方程
        index = selected[0]
        self.equation_listbox.delete(index)
        self.equations.pop(index)
        self.equation_colors.pop(index)
        
        # 更新状态
        self.status_var.set("已删除选中的方程")
        
        # 重新绘制
        self.plot_equations()
    
    def clear_equations(self):
        """清空所有方程"""
        if not self.equations:
            return
            
        if messagebox.askyesno("确认", "确定要清空所有方程吗?"):
            self.equation_listbox.delete(0, tk.END)
            self.equations.clear()
            self.equation_colors.clear()
            
            # 清除图形
            self.ax.clear()
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_title('方程可视化')
            if self.show_grid.get():
                self.ax.grid(True, linestyle='--', alpha=0.7)
            self.canvas.draw()
            
            # 更新状态
            self.status_var.set("已清空所有方程")
    
    def plot_equations(self):
        """绘制所有方程"""
        if not self.equations:
            messagebox.showinfo("提示", "请先添加方程")
            return
        
        try:
            # 解析范围
            x_min, x_max = map(float, self.x_range.get().split(','))
            y_min, y_max = map(float, self.y_range.get().split(','))
            
            # 清除当前图形
            self.ax.clear()
            self.equation_lines = []
            
            # 设置坐标轴范围
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            
            # 设置坐标轴标签
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_title('方程可视化')
            
            # 显示网格
            if self.show_grid.get():
                self.ax.grid(True, linestyle='--', alpha=0.7)
            
            # 绘制每个方程
            for i, ((mode, equation), color) in enumerate(zip(self.equations, self.equation_colors)):
                if mode == "显式方程":
                    self.plot_explicit(equation, color, i)
                elif mode == "隐式方程":
                    self.plot_implicit(equation, color, i)
                elif mode == "参数方程":
                    self.plot_parametric(equation, color, i)
                elif mode == "极坐标方程":
                    self.plot_polar(equation, color, i)
            
            # 显示图例
            if self.show_legend.get() and self.equation_lines:
                self.ax.legend()
            
            # 更新画布
            self.canvas.draw()
            
            # 更新状态
            self.status_var.set(f"已绘制 {len(self.equations)} 个方程")
            
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制方程时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def plot_explicit(self, equation, color, index):
        """绘制显式方程 y = f(x)"""
        try:
            x_min, x_max = map(float, self.x_range.get().split(','))
            resolution = self.resolution.get()
            
            # 创建x值数组
            x = np.linspace(x_min, x_max, resolution)
            
            # 计算y值
            y = np.zeros_like(x)
            for i, xi in enumerate(x):
                try:
                    y[i] = eval(equation, {"__builtins__": {}}, 
                              {"x": xi, "sin": np.sin, "cos": np.cos, "tan": np.tan, 
                               "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi})
                except:
                    y[i] = np.nan
            
            # 绘制曲线
            line, = self.ax.plot(x, y, color=color, linewidth=self.line_width.get(), 
                               label=f"y = {equation}")
            self.equation_lines.append(line)
            
            return True
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制显式方程时出错: {str(e)}")
            return False
    
    def plot_implicit(self, equation, color, index):
        """绘制隐式方程 f(x,y) = 0"""
        try:
            x_min, x_max = map(float, self.x_range.get().split(','))
            y_min, y_max = map(float, self.y_range.get().split(','))
            resolution = self.resolution.get()
            
            # 创建网格
            x = np.linspace(x_min, x_max, resolution)
            y = np.linspace(y_min, y_max, resolution)
            X, Y = np.meshgrid(x, y)
            
            # 计算函数值
            Z = np.zeros_like(X)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    try:
                        Z[i, j] = eval(equation, {"__builtins__": {}}, 
                                     {"x": X[i, j], "y": Y[i, j], "sin": np.sin, "cos": np.cos, 
                                      "tan": np.tan, "exp": np.exp, "log": np.log, 
                                      "sqrt": np.sqrt, "pi": np.pi})
                    except:
                        Z[i, j] = np.nan
            
            # 绘制等高线
            contour = self.ax.contour(X, Y, Z, [0], colors=[color], linewidths=self.line_width.get())
            
            # 添加到图例 - 安全地访问 collections
            # 创建一个代理艺术家对象用于图例
            from matplotlib.lines import Line2D
            legend_artist = Line2D([0], [0], color=color, lw=self.line_width.get())
            legend_artist.set_label(f"{equation} = 0")
            self.equation_lines.append(legend_artist)
            
            return True
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制隐式方程时出错: {str(e)}")
            return False
    
    def plot_parametric(self, equation, color, index):
        """绘制参数方程 x(t), y(t)"""
        try:
            # 解析参数方程
            parts = equation.split(',')
            if len(parts) < 4:
                messagebox.showerror("输入错误", "参数方程格式应为: x(t), y(t), t_min, t_max")
                return False
            
            x_expr = parts[0].strip()
            y_expr = parts[1].strip()
            t_min = float(parts[2].strip())
            t_max = float(parts[3].strip())
            
            resolution = self.resolution.get()
            
            # 创建参数值数组
            t = np.linspace(t_min, t_max, resolution)
            
            # 计算x和y值
            x = np.zeros_like(t)
            y = np.zeros_like(t)
            
            for i, ti in enumerate(t):
                try:
                    x[i] = eval(x_expr, {"__builtins__": {}}, 
                              {"t": ti, "sin": np.sin, "cos": np.cos, "tan": np.tan, 
                               "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi})
                    y[i] = eval(y_expr, {"__builtins__": {}}, 
                              {"t": ti, "sin": np.sin, "cos": np.cos, "tan": np.tan, 
                               "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi})
                except:
                    x[i] = np.nan
                    y[i] = np.nan
            
            # 绘制曲线
            line, = self.ax.plot(x, y, color=color, linewidth=self.line_width.get(), 
                               label=f"x = {x_expr}, y = {y_expr}")
            self.equation_lines.append(line)
            
            return True
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制参数方程时出错: {str(e)}")
            return False
    
    def plot_polar(self, equation, color, index):
        """绘制极坐标方程 r = f(theta)"""
        try:
            resolution = self.resolution.get()
            
            # 创建角度值数组
            theta = np.linspace(0, 2*np.pi, resolution)
            
            # 计算半径值
            r = np.zeros_like(theta)
            for i, th in enumerate(theta):
                try:
                    r[i] = eval(equation, {"__builtins__": {}}, 
                              {"theta": th, "sin": np.sin, "cos": np.cos, "tan": np.tan, 
                               "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi})
                except:
                    r[i] = np.nan
            
            # 转换为笛卡尔坐标
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # 绘制曲线
            line, = self.ax.plot(x, y, color=color, linewidth=self.line_width.get(), 
                               label=f"r = {equation}")
            self.equation_lines.append(line)
            
            return True
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制极坐标方程时出错: {str(e)}")
            return False
    
    def reset_view(self):
        """重置视图"""
        try:
            x_min, x_max = map(float, self.x_range.get().split(','))
            y_min, y_max = map(float, self.y_range.get().split(','))
            
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.canvas.draw()
            
            self.status_var.set("已重置视图")
        except Exception as e:
            messagebox.showerror("错误", f"重置视图时出错: {str(e)}")
    
    def save_figure(self):
        """保存图像到文件"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("JPEG图像", "*.jpg"), ("PDF文档", "*.pdf"), ("SVG图像", "*.svg")]
        )
        
        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("保存成功", f"图像已保存到: {file_path}")
            self.status_var.set(f"图像已保存到: {file_path}")
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.status_var.set(f"坐标: ({x:.4f}, {y:.4f})")
    def on_mouse_click(self, event):
        """处理鼠标点击事件"""
        if event.inaxes == self.ax and event.button == 1:  # 左键点击
            x, y = event.xdata, event.ydata
            
            # 在当前模式下添加点击位置的方程
            mode = self.current_mode.get()
            if mode == "显式方程":
                # 添加过点(x,y)的二次函数
                a = 1.0
                b = -2 * x
                c = y + x**2
                equation = f"{a}*x**2 + {b}*x + {c}"
                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, equation)
                self.status_var.set(f"已创建过点({x:.2f}, {y:.2f})的二次函数")
            
            elif mode == "隐式方程":
                # 添加以点(x,y)为中心的圆
                r = 2.0  # 默认半径
                equation = f"(x-{x})**2 + (y-{y})**2 - {r**2}"
                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, equation)
                self.status_var.set(f"已创建以点({x:.2f}, {y:.2f})为中心的圆")
            
            elif mode == "参数方程":
                # 添加以点(x,y)为中心的参数圆
                r = 2.0  # 默认半径
                equation = f"{x} + {r}*cos(t), {y} + {r}*sin(t), 0, 2*pi"
                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, equation)
                self.status_var.set(f"已创建以点({x:.2f}, {y:.2f})为中心的参数圆")
            
            elif mode == "极坐标方程":
                # 添加以原点为中心，过点(x,y)的极坐标圆
                r = np.sqrt(x**2 + y**2)
                equation = f"{r}"
                self.equation_entry.delete(0, tk.END)
                self.equation_entry.insert(0, equation)
                self.status_var.set(f"已创建过点({x:.2f}, {y:.2f})的极坐标圆")
    
    def on_key_press(self, event):
        """处理键盘事件"""
        if event.key == 'r':
            self.reset_view()
        elif event.key == 's':
            self.save_figure()
        elif event.key == 'g':
            self.show_grid.set(not self.show_grid.get())
            self.update_plot()
        elif event.key == 'l':
            self.show_legend.set(not self.show_legend.get())
            self.update_plot()
        elif event.key == 'c':
            self.clear_equations()
        elif event.key == 'a':
            self.add_equation()
        elif event.key == 'delete':
            self.delete_equation()
    
    def add_help_text(self):
        """添加帮助文本"""
        help_text = """
方程可视化工具使用指南：

1. 方程类型：
   - 显式方程：y = f(x)，例如 x**2 + 2*x + 1
   - 隐式方程：f(x,y) = 0，例如 x**2 + y**2 - 4
   - 参数方程：x(t), y(t), t_min, t_max，例如 cos(t), sin(t), 0, 2*pi
   - 极坐标方程：r = f(theta)，例如 2 + cos(theta)

2. 支持的函数：
   - 基本运算：+, -, *, /, **
   - 三角函数：sin, cos, tan
   - 指数和对数：exp, log
   - 其他：sqrt, pi

3. 快捷键：
   - r：重置视图
   - s：保存图像
   - g：显示/隐藏网格
   - l：显示/隐藏图例
   - c：清空所有方程
   - a：添加当前方程
   - Delete：删除选中方程

4. 鼠标操作：
   - 左键点击：在点击位置创建方程
   - 右键拖动：平移视图
   - 滚轮：缩放视图
"""
        return help_text
    
    def show_help(self):
        """显示帮助对话框"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("SimHei", 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text.insert(tk.END, self.add_help_text())
        help_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", "方程可视化工具\n版本 1.0\n\n一个用于可视化各种类型方程的工具。")
    
    def animate_equation(self):
        """动画展示方程变化"""
        if not self.equations:
            messagebox.showinfo("提示", "请先添加至少一个方程")
            return
        
        import matplotlib.animation as animation
        
        # 获取当前选中的方程
        selection = self.equation_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请选择一个方程进行动画展示")
            return
        
        index = selection[0]
        equation_type, equation, _ = self.equations[index]
        
        # 创建动画窗口
        anim_window = tk.Toplevel(self.root)
        anim_window.title("方程动画")
        anim_window.geometry("800x600")
        
        # 创建动画图形
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=anim_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 设置坐标轴范围
        x_min, x_max = map(float, self.x_range.get().split(','))
        y_min, y_max = map(float, self.y_range.get().split(','))
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        
        # 创建动画函数
        def animate(i):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.grid(True)
            
            # 根据方程类型创建动画
            if equation_type == "显式方程":
                x = np.linspace(x_min, x_max, self.resolution.get())
                try:
                    # 添加时间变量t
                    t = i / 50.0  # 动画参数
                    y = np.zeros_like(x)
                    for j, xj in enumerate(x):
                        y[j] = eval(equation, {"__builtins__": {}}, 
                                  {"x": xj, "t": t, "sin": np.sin, "cos": np.cos, 
                                   "tan": np.tan, "exp": np.exp, "log": np.log, 
                                   "sqrt": np.sqrt, "pi": np.pi})
                    ax.plot(x, y, 'b-', linewidth=2)
                    ax.set_title(f"y = {equation} (t = {t:.2f})")
                except:
                    pass
            
            elif equation_type == "参数方程":
                try:
                    parts = equation.split(',')
                    x_expr = parts[0].strip()
                    y_expr = parts[1].strip()
                    t_min = float(parts[2].strip())
                    t_max = float(parts[3].strip())
                    
                    # 添加动画参数
                    phase = i / 50.0 * 2 * np.pi  # 动画相位
                    
                    t = np.linspace(t_min, t_max, self.resolution.get())
                    x = np.zeros_like(t)
                    y = np.zeros_like(t)
                    
                    for j, tj in enumerate(t):
                        x[j] = eval(x_expr, {"__builtins__": {}}, 
                                  {"t": tj, "phase": phase, "sin": np.sin, "cos": np.cos, 
                                   "tan": np.tan, "exp": np.exp, "log": np.log, 
                                   "sqrt": np.sqrt, "pi": np.pi})
                        y[j] = eval(y_expr, {"__builtins__": {}}, 
                                  {"t": tj, "phase": phase, "sin": np.sin, "cos": np.cos, 
                                   "tan": np.tan, "exp": np.exp, "log": np.log, 
                                   "sqrt": np.sqrt, "pi": np.pi})
                    
                    ax.plot(x, y, 'g-', linewidth=2)
                    ax.set_title(f"参数方程 (phase = {phase:.2f})")
                except:
                    pass
            
            elif equation_type == "极坐标方程":
                try:
                    # 添加动画参数
                    scale = 1.0 + 0.5 * np.sin(i / 25.0)  # 动态缩放
                    
                    theta = np.linspace(0, 2*np.pi, self.resolution.get())
                    r = np.zeros_like(theta)
                    
                    for j, th in enumerate(theta):
                        r[j] = scale * eval(equation, {"__builtins__": {}}, 
                                          {"theta": th, "sin": np.sin, "cos": np.cos, 
                                           "tan": np.tan, "exp": np.exp, "log": np.log, 
                                           "sqrt": np.sqrt, "pi": np.pi})
                    
                    x = r * np.cos(theta)
                    y = r * np.sin(theta)
                    
                    ax.plot(x, y, 'r-', linewidth=2)
                    ax.set_title(f"极坐标方程 (scale = {scale:.2f})")
                except:
                    pass
            
            return []
        
        # 创建动画
        anim = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
        
        # 添加控制按钮
        control_frame = ttk.Frame(anim_window)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def close_animation():
            anim_window.destroy()
        
        close_button = ttk.Button(control_frame, text="关闭", command=close_animation)
        close_button.pack(side=tk.RIGHT)
        
        # 显示动画窗口
        anim_window.protocol("WM_DELETE_WINDOW", close_animation)
        anim_window.focus_set()

if __name__ == '__main__':
    root = tk.Tk()
    app = EquationVisualizationApp(root)
    root.mainloop()