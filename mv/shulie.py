import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import warnings
from knowledge import KnowledgeLearningClass

# 忽略sympy的警告
warnings.filterwarnings("ignore", category=UserWarning, module='sympy')

# 配置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']  # 优先使用的中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
matplotlib.rcParams['font.family'] = 'sans-serif'  # 使用无衬线字体

print("DEBUG: 成功加载shulie模块")

class SequenceModule:
    """数列功能模块 - 可以作为独立模块使用或集成到主应用程序"""
    
    def __init__(self, root=None, ax=None, canvas=None):
        """
        初始化数列模块
        
        参数:
            root: 父窗口，如果为None则创建新窗口
            ax: matplotlib轴对象，如果为None则创建新的
            canvas: matplotlib画布，如果为None则创建新的
        """
        print("DEBUG: 创建SequenceModule实例")
        self.parent = root
        self.knowledge_learner = KnowledgeLearningClass()
        # 如果没有提供父窗口，创建一个新窗口
        if root is None:
            self.root = tk.Tk()
            self.root.title("数列可视化工具")
            self.root.geometry("1000x700")
            self.is_standalone = True
        else:
            self.root = root
            self.is_standalone = False
        
        # 数列相关变量
        self.sequence_points = []  # 存储数列点
        self.draw_sequence = tk.BooleanVar(value=False)  # 控制是否绘制数列
        
        # 序列表达式及计算结果
        self.sequence_expr = None
        self.sequence_values = None
        self.sequence_sum = None
        
        # 如果没有提供ax和canvas，创建新的
        if ax is None or canvas is None:
            self.create_plot()
        else:
            self.ax = ax
            self.canvas = canvas
        
        # 创建UI，无论是否独立运行
        self.create_standalone_ui()

        
    
    def create_standalone_ui(self):
        """创建独立运行时的用户界面"""
        try:
            # 创建主框架
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 创建标题
            title_label = ttk.Label(main_frame, text="数列可视化工具", font=("SimHei", 18, "bold"))
            title_label.pack(pady=10)
            
            # 创建控制面板
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=10)
            
            # 添加数列控制面板
            sequence_controls = self.create_controls(control_frame)
            sequence_controls.pack(fill=tk.X, expand=True)
            
            # 添加绘图区域
            plot_frame = ttk.Frame(main_frame)
            plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # 将matplotlib画布添加到绘图区域
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # 添加matplotlib工具栏
            toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
            toolbar.update()
        except Exception as e:
            print(f"DEBUG: 创建UI时出错: {e}")
            messagebox.showerror("UI错误", f"创建界面时出错: {str(e)}")
    
    def create_plot(self):
        """创建matplotlib绘图区域"""
        # 创建Figure和Axes
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # 设置坐标轴标签和标题 - 使用中文字体
        self.ax.set_xlabel('n', fontproperties=FontProperties(family='SimHei', size=12))
        self.ax.set_ylabel('a_n', fontproperties=FontProperties(family='SimHei', size=12))
        self.ax.set_title('数列可视化', fontproperties=FontProperties(family='SimHei', size=14, weight='bold'))
        
        # 添加网格
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
    
    def create_controls(self, parent):
        """创建数列控制面板"""
        frame = ttk.LabelFrame(parent, text="数列控制", padding=10)
        
        # 数列通项输入区域
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="数列通项:").pack(side=tk.LEFT, padx=5)
        self.sequence_entry = ttk.Entry(input_frame, width=20)
        self.sequence_entry.pack(side=tk.LEFT, padx=5)
        self.sequence_entry.insert(0, "1/n")
        
        ttk.Label(input_frame, text="开始项:").pack(side=tk.LEFT, padx=(15, 5))
        self.sequence_start_entry = ttk.Entry(input_frame, width=5)
        self.sequence_start_entry.pack(side=tk.LEFT, padx=5)
        self.sequence_start_entry.insert(0, "1")
        
        ttk.Label(input_frame, text="结束项:").pack(side=tk.LEFT, padx=(15, 5))
        self.sequence_end_entry = ttk.Entry(input_frame, width=5)
        self.sequence_end_entry.pack(side=tk.LEFT, padx=5)
        self.sequence_end_entry.insert(0, "20")
        
        # 数列显示控制
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.sequence_check = ttk.Checkbutton(
            control_frame, 
            text="显示数列", 
            variable=self.draw_sequence,
            command=self.toggle_sequence
        )
        self.sequence_check.pack(side=tk.LEFT, padx=5)
        
        update_button = ttk.Button(
            control_frame,
            text="更新数列",
            command=self.update_sequence
        )
        update_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            control_frame,
            text="清除数列",
            command=self.clear_sequence
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 数列和计算区域
        sum_frame = ttk.Frame(frame)
        sum_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sum_frame, text="数列和:").pack(side=tk.LEFT, padx=5)
        self.sequence_sum_text = tk.Text(sum_frame, height=1, width=20, font=("SimHei", 10))
        self.sequence_sum_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.sequence_sum_text.insert(tk.END, "未计算")
        self.sequence_sum_text.config(state=tk.DISABLED)
        
        calc_sum_button = ttk.Button(
            sum_frame,
            text="计算数列和",
            command=self.calculate_sequence_sum
        )
        calc_sum_button.pack(side=tk.LEFT, padx=5)
        
        # 数列收敛性分析区域
        convergence_frame = ttk.Frame(frame)
        convergence_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(convergence_frame, text="收敛性分析:").pack(side=tk.LEFT, padx=5)
        self.convergence_text = tk.Text(convergence_frame, height=2, width=40, font=("SimHei", 10))
        self.convergence_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.convergence_text.insert(tk.END, "未分析")
        self.convergence_text.config(state=tk.DISABLED)
        
        analyze_button = ttk.Button(
            convergence_frame,
            text="分析收敛性",
            command=self.analyze_convergence
        )
        analyze_button.pack(side=tk.LEFT, padx=5)

        knowledge_learning_integral_frame = ttk.Frame(frame)
        knowledge_learning_integral_frame.pack(fill=tk.X, pady=5)

        knowledge_learning= ttk.Button(
            knowledge_learning_integral_frame,
            text="知识介绍", 
            command=self.knowledge_learner.knowledge_learning_5_function
        )
        knowledge_learning.pack(side=tk.LEFT, padx=10)
        
        return frame
    
    def toggle_sequence(self):
        """切换数列显示状态"""
        if self.draw_sequence.get():
            self.update_sequence()
        else:
            self.clear_sequence()
            self.canvas.draw()
    
    def update_sequence(self):
        """更新数列点"""
        try:
            # 获取数列表达式
            expression = self.sequence_entry.get()
            start = int(self.sequence_start_entry.get())
            end = int(self.sequence_end_entry.get())
            
            if end < start:
                messagebox.showerror("数列错误", "结束项必须大于等于开始项")
                return
            
            # 使用sympy解析表达式
            x = sp.Symbol('n')
            expr = parse_expr(expression, transformations=(standard_transformations + (implicit_multiplication_application,)))
            self.sequence_expr = expr
            
            # 计算数列值
            values = []
            for n in range(start, end + 1):
                try:
                    val = float(expr.subs(x, n))
                    values.append((n, val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    # 跳过无法计算的点
                    continue
            
            self.sequence_values = values
            self.draw_sequence_points(values)
            
        except Exception as e:
            messagebox.showerror("数列错误", f"计算数列时出错: {str(e)}")
            self.clear_sequence()
    
    def draw_sequence_points(self, values):
        """绘制数列点"""
        self.clear_sequence()
        
        if not values:
            messagebox.showinfo("提示", "没有有效的数列值可以绘制")
            return
        
        # 绘制数列点和连线
        x_vals = [val[0] for val in values]
        y_vals = [val[1] for val in values]
        
        # 绘制点
        sequence_line = Line2D(x_vals, y_vals, marker='o', color='purple', 
                              markersize=6, linestyle='-', linewidth=1)
        self.sequence_points.append(self.ax.add_line(sequence_line))
        
        # 调整坐标轴范围
        self.ax.set_xlim(min(x_vals) - 1, max(x_vals) + 1)
        
        # 计算y轴范围，避免极端值
        valid_y = [y for y in y_vals if not (np.isinf(y) or np.isnan(y))]
        if valid_y:
            y_min, y_max = min(valid_y), max(valid_y)
            y_range = y_max - y_min
            self.ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
        
        self.canvas.draw()
    
    def calculate_sequence_sum(self):
        """计算数列和"""
        if not self.sequence_values:
            messagebox.showinfo("提示", "请先显示数列")
            return
        
        try:
            # 计算数列和
            sum_value = sum(val[1] for val in self.sequence_values)
            
            # 更新显示
            self.sequence_sum_text.config(state=tk.NORMAL)
            self.sequence_sum_text.delete(1.0, tk.END)
            self.sequence_sum_text.insert(tk.END, f"{sum_value:.6f}")
            self.sequence_sum_text.config(state=tk.DISABLED)
            
            self.sequence_sum = sum_value
            
        except Exception as e:
            messagebox.showerror("计算错误", f"计算数列和时出错: {str(e)}")
    
    def analyze_convergence(self):
        """分析数列的收敛性"""
        if not self.sequence_expr:
            messagebox.showinfo("提示", "请先输入并显示数列")
            return
        
        try:
            # 使用sympy进行极限分析
            n = sp.Symbol('n')
            limit_value = sp.limit(self.sequence_expr, n, sp.oo)
            
            # 判断收敛性
            if limit_value.is_finite:
                if limit_value == 0:
                    result = f"数列收敛于0"
                else:
                    result = f"数列收敛于 {limit_value}"
            else:
                if limit_value.is_infinite:
                    if limit_value > 0:
                        result = "数列发散到正无穷"
                    else:
                        result = "数列发散到负无穷"
                else:
                    result = "数列不收敛"
            
            # 更新显示
            self.convergence_text.config(state=tk.NORMAL)
            self.convergence_text.delete(1.0, tk.END)
            self.convergence_text.insert(tk.END, result)
            self.convergence_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("分析错误", f"分析数列收敛性时出错: {str(e)}")
            self.convergence_text.config(state=tk.NORMAL)
            self.convergence_text.delete(1.0, tk.END)
            self.convergence_text.insert(tk.END, f"无法分析: {str(e)}")
            self.convergence_text.config(state=tk.DISABLED)
    
    def clear_sequence(self):
        """清除数列点"""
        for point in self.sequence_points:
            point.remove()
        self.sequence_points = []
        self.canvas.draw()
    
    def run(self):
        """运行独立应用程序"""
        if self.is_standalone:
            self.root.mainloop()


# 如果作为独立程序运行
if __name__ == "__main__":
    app = SequenceModule()
    app.run() 