import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.integrate import solve_ivp
from matplotlib.figure import Figure
import matplotlib
from knowledge import KnowledgeLearningClass

# 配置 Matplotlib 以支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False  # 确保负号正确显示
matplotlib.rcParams['font.family'] = 'sans-serif'

class DirectionFieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("方向场与积分曲线可视化")
        self.root.geometry("1000x700")
        self.knowledge_learner = KnowledgeLearningClass()

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TLabel", font=("SimHei", 10), background="#f0f0f0")
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建UI
        self.create_ui()
        
        # 设置默认值
        self.equation_entry.insert(0, "y")
        self.initial_condition_entry.insert(0, "0,1")
        self.x_range_entry.insert(0, "-5,5")
        self.y_range_entry.insert(0, "-5,5")
        
        # 初始化绘图
        self.setup_plot()
        
        # 绘制默认图形
        self.plot_direction_field_and_curves()

        
    def create_ui(self):
        # 创建控制面板
        control_frame = ttk.Frame(self.main_frame, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 标题
        title_label = ttk.Label(control_frame, text="方向场与积分曲线可视化", 
                               font=("SimHei", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 输入微分方程的标签和输入框
        ttk.Label(control_frame, text="输入微分方程 dy/dx = ").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.equation_entry = ttk.Entry(control_frame, width=25)
        self.equation_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 输入初始条件的标签和输入框
        ttk.Label(control_frame, text="初始条件 (x0, y0):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.initial_condition_entry = ttk.Entry(control_frame, width=25)
        self.initial_condition_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 添加范围输入
        ttk.Label(control_frame, text="X范围 (min,max):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.x_range_entry = ttk.Entry(control_frame, width=25)
        self.x_range_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="Y范围 (min,max):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.y_range_entry = ttk.Entry(control_frame, width=25)
        self.y_range_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 添加方向场密度控制
        ttk.Label(control_frame, text="方向场密度:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.density_var = tk.IntVar(value=20)
        self.density_scale = ttk.Scale(control_frame, from_=10, to=50, 
                                     orient=tk.HORIZONTAL, variable=self.density_var)
        self.density_scale.grid(row=5, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 添加积分曲线数量控制
        ttk.Label(control_frame, text="积分曲线数量:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.curves_var = tk.IntVar(value=1)
        self.curves_scale = ttk.Scale(control_frame, from_=1, to=10, 
                                    orient=tk.HORIZONTAL, variable=self.curves_var)
        self.curves_scale.grid(row=6, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 添加颜色选择
        ttk.Label(control_frame, text="方向场颜色:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.field_color_var = tk.StringVar(value="#1f77b4")
        field_color_btn = ttk.Button(control_frame, text="选择颜色", 
                                   command=lambda: self.choose_color(self.field_color_var))
        field_color_btn.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="积分曲线颜色:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.curve_color_var = tk.StringVar(value="#d62728")
        curve_color_btn = ttk.Button(control_frame, text="选择颜色", 
                                   command=lambda: self.choose_color(self.curve_color_var))
        curve_color_btn.grid(row=8, column=1, sticky=tk.W, pady=5)
        
        # 添加显示选项
        self.show_field_var = tk.BooleanVar(value=True)
        show_field_check = ttk.Checkbutton(control_frame, text="显示方向场", 
                                         variable=self.show_field_var)
        show_field_check.grid(row=9, column=0, sticky=tk.W, pady=5)
        
        self.show_curves_var = tk.BooleanVar(value=True)
        show_curves_check = ttk.Checkbutton(control_frame, text="显示积分曲线", 
                                          variable=self.show_curves_var)
        show_curves_check.grid(row=9, column=1, sticky=tk.W, pady=5)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        show_grid_check = ttk.Checkbutton(control_frame, text="显示网格", 
                                        variable=self.show_grid_var)
        show_grid_check.grid(row=10, column=0, sticky=tk.W, pady=5)
        
        # 添加动画选项
        self.animate_var = tk.BooleanVar(value=False)
        animate_check = ttk.Checkbutton(control_frame, text="动画显示积分曲线", 
                                      variable=self.animate_var)
        animate_check.grid(row=10, column=1, sticky=tk.W, pady=5)
        
        # 绘制按钮
        plot_button = ttk.Button(control_frame, text="绘制", command=self.plot_direction_field_and_curves)
        plot_button.grid(row=11, column=0, columnspan=2, pady=10)
        
        # 添加保存按钮
        save_button = ttk.Button(control_frame, text="保存图像", command=self.save_figure)
        save_button.grid(row=12, column=0, columnspan=2, pady=5)

        knowledge_learning = ttk.Button(control_frame, text="知识介绍", command=self.knowledge_learner.knowledge_learning_6_function)
        knowledge_learning.grid(row=13, column=3, columnspan=2, pady=5)
        
        # 添加信息显示区域
        info_frame = ttk.LabelFrame(control_frame, text="信息", padding=5)
        info_frame.grid(row=13, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, wrap=tk.WORD, 
                               font=("SimHei", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, "欢迎使用方向场与积分曲线可视化工具！\n\n")
        self.info_text.insert(tk.END, "使用说明:\n")
        self.info_text.insert(tk.END, "1. 输入微分方程 dy/dx 的右侧表达式\n")
        self.info_text.insert(tk.END, "2. 设置初始条件和范围\n")
        self.info_text.insert(tk.END, "3. 调整显示选项\n")
        self.info_text.insert(tk.END, "4. 点击'绘制'按钮\n")
        self.info_text.config(state=tk.DISABLED)

    def setup_plot(self):
        # 创建绘图区域
        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建图形和轴
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # 设置图形样式
        self.fig.set_facecolor("#f8f8f8")
        self.ax.set_facecolor("#f8f8f8")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # 绑定鼠标事件
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)

    def choose_color(self, color_var):
        color = colorchooser.askcolor(initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
            self.plot_direction_field_and_curves()

    def plot_direction_field_and_curves(self):
        equation_str = self.equation_entry.get()
        initial_condition_str = self.initial_condition_entry.get()
        x_range_str = self.x_range_entry.get()
        y_range_str = self.y_range_entry.get()

        if not equation_str:
            messagebox.showerror("错误", "请输入有效的微分方程")
            return

        try:
            # 解析范围
            x_min, x_max = map(float, x_range_str.split(','))
            y_min, y_max = map(float, y_range_str.split(','))
            
            # 解析初始条件
            initial_conditions = []
            if initial_condition_str:
                # 支持多个初始条件
                if ';' in initial_condition_str:
                    for ic in initial_condition_str.split(';'):
                        x0, y0 = map(float, ic.split(','))
                        initial_conditions.append((x0, y0))
                else:
                    x0, y0 = map(float, initial_condition_str.split(','))
                    initial_conditions.append((x0, y0))
            
            # 如果设置了多条积分曲线，自动生成初始条件
            num_curves = self.curves_var.get()
            if len(initial_conditions) == 1 and num_curves > 1:
                x0, y0 = initial_conditions[0]
                initial_conditions = []
                for i in range(num_curves):
                    # 在初始点周围生成点
                    offset = (i - num_curves/2) * (y_max - y_min) / 10
                    initial_conditions.append((x0, y0 + offset))
            
            # 定义微分方程
            def dydx(x, y):
                # 安全地评估表达式
                try:
                    return eval(equation_str, {"__builtins__": {}}, 
                              {"x": x, "y": y, "sin": np.sin, "cos": np.cos, 
                               "tan": np.tan, "exp": np.exp, "log": np.log, 
                               "sqrt": np.sqrt, "pi": np.pi})
                except Exception as e:
                    print(f"计算错误: {e}")
                    return 0

            # 清除旧图
            self.ax.clear()
            
            # 设置坐标轴范围
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            
            # 设置标题和标签
            self.ax.set_title(f"方向场与积分曲线: dy/dx = {equation_str}", fontsize=12)
            self.ax.set_xlabel("x", fontsize=10)
            self.ax.set_ylabel("y", fontsize=10)
            
            # 显示网格
            if self.show_grid_var.get():
                self.ax.grid(True, linestyle='--', alpha=0.7)
            else:
                self.ax.grid(False)
            
            # 绘制方向场
            if self.show_field_var.get():
                density = self.density_var.get()
                x = np.linspace(x_min, x_max, density)
                y = np.linspace(y_min, y_max, density)
                X, Y = np.meshgrid(x, y)
                
                # 计算斜率
                U = np.ones_like(X)
                V = np.zeros_like(Y)
                
                # 安全计算每个点的斜率
                for i in range(len(x)):
                    for j in range(len(y)):
                        try:
                            slope = dydx(X[j, i], Y[j, i])
                            if np.isfinite(slope):
                                # 归一化向量
                                norm = np.sqrt(1 + slope**2)
                                U[j, i] = 1 / norm
                                V[j, i] = slope / norm
                            else:
                                U[j, i] = 0
                                V[j, i] = 1  # 垂直向量表示无穷斜率
                        except:
                            U[j, i] = 0
                            V[j, i] = 0
                
                # 使用自定义颜色绘制方向场
                field_color = self.field_color_var.get()
                self.ax.quiver(X, Y, U, V, color=field_color, 
                             angles='xy', scale_units='xy', scale=25,
                             alpha=0.8, width=0.003, headwidth=5, headlength=7)
            
            # 绘制积分曲线
            if self.show_curves_var.get() and initial_conditions:
                curve_color = self.curve_color_var.get()
                
                for idx, (x0, y0) in enumerate(initial_conditions):
                    # 确保初始点在范围内
                    if x_min <= x0 <= x_max and y_min <= y0 <= y_max:
                        # 向前积分
                        sol_forward = solve_ivp(
                            dydx, 
                            [x0, x_max], 
                            [y0], 
                            method='RK45',
                            dense_output=True,
                            events=lambda x, y: self._out_of_bounds(x, y, y_min, y_max),
                            rtol=1e-5
                        )
                        
                        # 向后积分
                        sol_backward = solve_ivp(
                            dydx, 
                            [x0, x_min], 
                            [y0], 
                            method='RK45',
                            dense_output=True,
                            events=lambda x, y: self._out_of_bounds(x, y, y_min, y_max),
                            rtol=1e-5
                        )
                        
                        # 生成密集的点
                        t_forward = np.linspace(x0, sol_forward.t[-1], 100)
                        y_forward = sol_forward.sol(t_forward)[0]
                        
                        t_backward = np.linspace(x0, sol_backward.t[-1], 100)
                        y_backward = sol_backward.sol(t_backward)[0]
                        
                        # 过滤超出范围的点
                        valid_forward = (y_forward >= y_min) & (y_forward <= y_max)
                        valid_backward = (y_backward >= y_min) & (y_backward <= y_max)
                        
                        # 如果启用动画，分段绘制
                        if self.animate_var.get():
                            # 先绘制初始点
                            self.ax.plot(x0, y0, 'o', color=curve_color, markersize=6)
                            self.canvas.draw_idle()
                            self.root.update()
                            
                            # 分段绘制向前曲线
                            segments = 20
                            for i in range(1, segments+1):
                                end_idx = min(len(t_forward), int(i * len(t_forward) / segments))
                                if end_idx > 0:
                                    segment_t = t_forward[:end_idx]
                                    segment_y = y_forward[:end_idx]
                                    segment_valid = valid_forward[:end_idx]
                                    
                                    if np.any(segment_valid):
                                        self.ax.plot(segment_t[segment_valid], segment_y[segment_valid], 
                                                  '-', color=curve_color, linewidth=2, alpha=0.8)
                                        self.canvas.draw_idle()
                                        self.root.update()
                                        self.root.after(50)  # 短暂延迟
                            
                            # 分段绘制向后曲线
                            for i in range(1, segments+1):
                                end_idx = min(len(t_backward), int(i * len(t_backward) / segments))
                                if end_idx > 0:
                                    segment_t = t_backward[:end_idx]
                                    segment_y = y_backward[:end_idx]
                                    segment_valid = valid_backward[:end_idx]
                                    
                                    if np.any(segment_valid):
                                        self.ax.plot(segment_t[segment_valid], segment_y[segment_valid], 
                                                  '-', color=curve_color, linewidth=2, alpha=0.8)
                                        self.canvas.draw_idle()
                                        self.root.update()
                                        self.root.after(50)  # 短暂延迟
                        else:
                            # 一次性绘制所有曲线
                            if np.any(valid_forward):
                                self.ax.plot(t_forward[valid_forward], y_forward[valid_forward], 
                                          '-', color=curve_color, linewidth=2, alpha=0.8)
                            
                            if np.any(valid_backward):
                                self.ax.plot(t_backward[valid_backward], y_backward[valid_backward], 
                                          '-', color=curve_color, linewidth=2, alpha=0.8)
                            
                            # 绘制初始点
                            self.ax.plot(x0, y0, 'o', color=curve_color, markersize=6)
                
                # 添加图例
                self.ax.legend(['积分曲线'], loc='best')
            
            # 更新画布
            self.canvas.draw()
            
            # 更新信息文本
            self.update_info_text(equation_str)
            
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def _out_of_bounds(self, x, y, y_min, y_max):
        """检查积分是否超出边界"""
        return 1 if y[0] < y_min or y[0] > y_max else -1

    def update_info_text(self, equation_str):
        """更新信息文本区域"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        self.info_text.insert(tk.END, f"当前方程: dy/dx = {equation_str}\n\n")
        
        # 添加方程分析
        try:
            # 尝试找到平衡点
            import sympy as sp
            x, y = sp.symbols('x y')
            expr = sp.sympify(equation_str.replace('np.', '').replace('math.', ''))
            
            # 求解平衡点 (dy/dx = 0)
            equilibria = sp.solve(expr, y)
            
            if equilibria:
                self.info_text.insert(tk.END, "平衡点分析:\n")
                for eq in equilibria:
                    self.info_text.insert(tk.END, f"  y = {eq}\n")
            else:
                self.info_text.insert(tk.END, "未找到简单平衡点\n")
                
        except Exception as e:
            self.info_text.insert(tk.END, f"方程分析错误: {str(e)}\n")
        
        self.info_text.insert(tk.END, "\n使用提示:\n")
        self.info_text.insert(tk.END, "- 点击图中任意位置添加新的初始条件\n")
        self.info_text.insert(tk.END, "- 鼠标悬停可查看坐标和斜率\n")
        self.info_text.insert(tk.END, "- 使用工具栏可以缩放和平移图像\n")
        
        self.info_text.config(state=tk.DISABLED)

    def on_click(self, event):
        """处理鼠标点击事件"""
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            
            # 添加新的初始条件
            current = self.initial_condition_entry.get()
            if current and ';' not in current:
                # 如果已有一个初始条件，添加分号
                self.initial_condition_entry.delete(0, tk.END)
                self.initial_condition_entry.insert(0, f"{current};{x:.2f},{y:.2f}")
            else:
                # 替换为新的初始条件
                self.initial_condition_entry.delete(0, tk.END)
                self.initial_condition_entry.insert(0, f"{x:.2f},{y:.2f}")
            
            # 重新绘制
            self.plot_direction_field_and_curves()

    def on_hover(self, event):
        """处理鼠标悬停事件"""
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            
            # 计算当前点的斜率
            equation_str = self.equation_entry.get()
            try:
                slope = eval(equation_str, {"__builtins__": {}}, 
                           {"x": x, "y": y, "sin": np.sin, "cos": np.cos, 
                            "tan": np.tan, "exp": np.exp, "log": np.log, 
                            "sqrt": np.sqrt, "pi": np.pi})
                
                # 更新状态栏
                self.ax.set_title(f"方向场与积分曲线: dy/dx = {equation_str} | 坐标: ({x:.2f}, {y:.2f}), 斜率: {slope:.2f}", 
                                fontsize=10)
                self.canvas.draw_idle()
            except:
                pass

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


if __name__ == '__main__':
    root = tk.Tk()
    app = DirectionFieldApp(root)
    root.mainloop()
    