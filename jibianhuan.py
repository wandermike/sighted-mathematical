import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# 检查系统中可用的中文字体
def get_available_chinese_font():
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STXihei', 'STHeiti', 'SimSun', 'NSimSun']
    available_font = None
    for font in chinese_fonts:
        if any(f.name == font for f in fm.fontManager.ttflist):
            available_font = font
            break
    return available_font or 'SimHei'

# 设置中文字体
chinese_font = get_available_chinese_font()
plt.rcParams["font.sans-serif"] = [chinese_font]
plt.rcParams["axes.unicode_minus"] = False

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        try:
            xs3d, ys3d, zs3d = self._verts3d
            if self.axes is None:  # 检查轴是否存在
                return
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            super().draw(renderer)
        except Exception as e:
            print(f"Arrow3D draw error: {str(e)}")

    def do_3d_projection(self, renderer=None):
        try:
            xs3d, ys3d, zs3d = self._verts3d
            if self.axes is None:  # 检查轴是否存在
                return np.inf
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            return np.min(zs)
        except Exception as e:
            print(f"Arrow3D projection error: {str(e)}")
            return np.inf

    def update(self, xs, ys, zs):
        self._verts3d = xs, ys, zs

class MatrixTransformationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("基变换可视化")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建左侧控制面板
        self.control_frame = tk.Frame(master, bg='#E6F3FF', width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            self.control_frame,
            text="基变换可视化",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        # 创建输入区域
        self.create_input_area()
        
        # 创建按钮区域
        self.create_buttons()
        
        # 添加结果显示区域
        self.create_result_area()
        
        # 创建右侧绘图区域
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建图形和画布
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # 创建子图
        self.create_subplots()
        
        # 初始化变量
        self.animation_running = False
        self.paused = False
        self.current_t = 0
        self.arrows = []
        
        # 绑定窗口关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置默认矩阵
        self.set_default_matrices()
    
    def create_input_area(self):
        """创建输入区域"""
        # 原始基矩阵输入
        base_a_frame = tk.LabelFrame(
            self.control_frame,
            text="原始基矩阵 A",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        base_a_frame.pack(fill=tk.X, pady=10)
        
        self.base_a_entries = []
        for i in range(3):
            row_frame = tk.Frame(base_a_frame, bg='#E6F3FF')
            row_frame.pack(pady=5)
            row_entries = []
            for j in range(3):
                entry = tk.Entry(
                    row_frame,
                    width=8,
                    font=('Consolas', 12),
                    justify='center',
                    relief='solid',
                    bg='white',
                    fg='#2C3E50'
                )
                entry.pack(side=tk.LEFT, padx=5)
                # 默认为单位矩阵
                entry.insert(0, '1' if i == j else '0')
                row_entries.append(entry)
            self.base_a_entries.append(row_entries)
        
        # 目标基矩阵输入
        base_b_frame = tk.LabelFrame(
            self.control_frame,
            text="目标基矩阵 B",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        base_b_frame.pack(fill=tk.X, pady=10)
        
        self.base_b_entries = []
        for i in range(3):
            row_frame = tk.Frame(base_b_frame, bg='#E6F3FF')
            row_frame.pack(pady=5)
            row_entries = []
            for j in range(3):
                entry = tk.Entry(
                    row_frame,
                    width=8,
                    font=('Consolas', 12),
                    justify='center',
                    relief='solid',
                    bg='white',
                    fg='#2C3E50'
                )
                entry.pack(side=tk.LEFT, padx=5)
                # 默认为旋转矩阵
                if i == 0 and j == 0:
                    entry.insert(0, '0.7')
                elif i == 0 and j == 1:
                    entry.insert(0, '-0.7')
                elif i == 1 and j == 0:
                    entry.insert(0, '0.7')
                elif i == 1 and j == 1:
                    entry.insert(0, '0.7')
                elif i == 2 and j == 2:
                    entry.insert(0, '1')
                else:
                    entry.insert(0, '0')
                row_entries.append(entry)
            self.base_b_entries.append(row_entries)
        
        # 向量输入
        vector_frame = tk.LabelFrame(
            self.control_frame,
            text="输入向量",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        vector_frame.pack(fill=tk.X, pady=10)
        
        vector_input_frame = tk.Frame(vector_frame, bg='#E6F3FF')
        vector_input_frame.pack(pady=5)
        
        self.vector_entries = []
        for i in range(3):
            entry = tk.Entry(
                vector_input_frame,
                width=8,
                font=('Consolas', 12),
                justify='center',
                relief='solid',
                bg='white',
                fg='#2C3E50'
            )
            entry.pack(side=tk.LEFT, padx=5)
            entry.insert(0, '1' if i == 0 else '0')
            self.vector_entries.append(entry)
    
    def create_buttons(self):
        """创建按钮区域"""
        button_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        button_frame.pack(pady=20)
        
        # 按钮样式
        button_style = {
            'font': ('SimHei', 11),
            'relief': 'raised',
            'bg': '#4A90E2',
            'fg': 'white',
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2',
            'width': 12,
            'borderwidth': 2
        }
        
        # 随机矩阵按钮
        self.random_button = tk.Button(
            button_frame,
            text="随机矩阵",
            command=self.generate_random_matrices,
            **button_style
        )
        self.random_button.pack(side=tk.LEFT, padx=5)
        
        # 开始动画按钮
        self.start_button = tk.Button(
            button_frame,
            text="开始动画",
            command=self.start_animation,
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 暂停按钮
        self.pause_button = tk.Button(
            button_frame,
            text="暂停动画",
            command=self.toggle_pause,
            state=tk.DISABLED,
            **button_style
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        self.reset_button = tk.Button(
            button_frame,
            text="重置",
            command=self.reset,
            **button_style
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="基变换理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    
    def create_result_area(self):
        """创建结果显示区域"""
        result_frame = tk.LabelFrame(
            self.control_frame,
            text="计算结果",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        result_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.result_text = tk.Text(
            result_frame,
            height=12,
            width=45,
            font=('Consolas', 11),
            relief='solid',
            bg='white',
            fg='#2C3E50'
        )
        self.result_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        result_scrollbar = tk.Scrollbar(self.result_text)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=result_scrollbar.set)
        result_scrollbar.config(command=self.result_text.yview)
    
    def create_subplots(self):
        """创建子图"""
        self.fig.clear()
        
        # 创建1x2网格的子图
        self.ax_original = self.fig.add_subplot(121, projection='3d')
        self.ax_original.set_title("原始基下的向量", fontsize=12)
        
        self.ax_animation = self.fig.add_subplot(122, projection='3d')
        self.ax_animation.set_title("基变换动画", fontsize=12)
        
        # 初始化绘图
        for ax in [self.ax_original, self.ax_animation]:
            ax.set_xlim([-5, 5])
            ax.set_ylim([-5, 5])
            ax.set_zlim([-5, 5])
            ax.set_xlabel("X", fontsize=10)
            ax.set_ylabel("Y", fontsize=10)
            ax.set_zlabel("Z", fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def set_default_matrices(self):
        """设置默认矩阵"""
        # 已经在创建输入区域时设置了默认值
    
    def generate_random_matrices(self):
        """生成随机矩阵"""
        # 生成1到6的随机整数矩阵
        base_a = np.random.randint(1, 7, (3, 3))
        base_b = np.random.randint(1, 7, (3, 3))
        vector = np.random.randint(1, 7, 3)
        
        # 确保矩阵可逆
        while np.linalg.det(base_a) == 0:
            base_a = np.random.randint(1, 7, (3, 3))
        
        while np.linalg.det(base_b) == 0:
            base_b = np.random.randint(1, 7, (3, 3))
        
        # 更新输入框
        for i in range(3):
            for j in range(3):
                self.base_a_entries[i][j].delete(0, tk.END)
                self.base_a_entries[i][j].insert(0, str(base_a[i, j]))
                
                self.base_b_entries[i][j].delete(0, tk.END)
                self.base_b_entries[i][j].insert(0, str(base_b[i, j]))
        
        # 更新向量输入框
        for i in range(3):
            self.vector_entries[i].delete(0, tk.END)
            self.vector_entries[i].insert(0, str(vector[i]))
        
        # 重置界面
        self.reset()
    
    def get_matrices(self):
        """从输入框获取矩阵"""
        try:
            # 获取原始基矩阵
            base_a = np.array([[float(self.base_a_entries[i][j].get())
                               for j in range(3)]
                              for i in range(3)])
            
            # 获取目标基矩阵
            base_b = np.array([[float(self.base_b_entries[i][j].get())
                               for j in range(3)]
                              for i in range(3)])
            
            # 获取向量
            vector = np.array([float(entry.get()) for entry in self.vector_entries])
            
            return base_a, base_b, vector
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
            return None, None, None
    
    def display_results(self, base_a, base_b, vector):
        """显示计算结果"""
        # 清空结果文本
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        
        # 计算变换矩阵
        change_matrix = np.linalg.inv(base_b) @ base_a
        
        # 计算向量在不同基下的表示
        vector_in_standard_basis = base_a @ vector
        vector_in_new_basis = np.linalg.inv(base_b) @ vector_in_standard_basis
        
        # 格式化原始基矩阵
        result_str = "原始基矩阵 A:\n"
        for row in base_a:
            result_str += "  ".join([f"{val:6.3f}" for val in row]) + "\n"
        
        # 格式化目标基矩阵
        result_str += "\n目标基矩阵 B:\n"
        for row in base_b:
            result_str += "  ".join([f"{val:6.3f}" for val in row]) + "\n"
        
        # 格式化变换矩阵
        result_str += "\n变换矩阵 P = B^(-1)A:\n"
        for row in change_matrix:
            result_str += "  ".join([f"{val:6.3f}" for val in row]) + "\n"
        
        # 格式化向量表示
        result_str += f"\n向量 v = [{vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f}]\n"
        result_str += "\n标准基下的向量表示:\n"
        result_str += "  ".join([f"{val:6.3f}" for val in vector_in_standard_basis]) + "\n"
        
        result_str += "\n新基下的向量表示:\n"
        result_str += "  ".join([f"{val:6.3f}" for val in vector_in_new_basis]) + "\n"
        
        # 添加到结果文本
        self.result_text.insert('1.0', result_str)
        
        # 禁用编辑
        self.result_text.config(state='disabled')
    
    def draw_basis(self, ax, basis_matrix, t=1.0, original=True):
        """绘制基向量"""
        ax.clear()
        
        # 设置坐标轴
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.set_zlim([-5, 5])
        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
        ax.set_zlabel("Z", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # 绘制坐标轴
        ax.plot([-5, 5], [0, 0], [0, 0], 'k--', alpha=0.2)
        ax.plot([0, 0], [-5, 5], [0, 0], 'k--', alpha=0.2)
        ax.plot([0, 0], [0, 0], [-5, 5], 'k--', alpha=0.2)
        
        # 颜色列表
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # 绘制基向量
        arrows = []
        for i in range(3):
            # 获取基向量
            vector = basis_matrix[:, i] * t
            
            # 创建3D箭头
            arrow = Arrow3D(
                [0, vector[0]], [0, vector[1]], [0, vector[2]],
                mutation_scale=15,
                lw=2,
                arrowstyle="-|>",
                color=colors[i],
                alpha=0.8
            )
            ax.add_artist(arrow)
            arrows.append(arrow)
            
            # 添加标签
            if original:
                label = f"e_{i+1}"
            else:
                label = f"e'_{i+1}"
            
            ax.text(vector[0]*1.1, vector[1]*1.1, vector[2]*1.1, 
                   label, color=colors[i], fontsize=10)
        
        # 设置视角
        ax.view_init(elev=30, azim=45)
        
        return arrows
    
    def draw_vector(self, ax, basis_matrix, vector, t=1.0, color='#FFD166'):
        """绘制向量"""
        # 计算向量在给定基下的表示
        vector_in_basis = basis_matrix @ vector
        vector_in_basis = vector_in_basis * t
        
        # 创建3D箭头
        arrow = Arrow3D(
            [0, vector_in_basis[0]], [0, vector_in_basis[1]], [0, vector_in_basis[2]],
            mutation_scale=15,
            lw=3,
            arrowstyle="-|>",
            color=color,
            alpha=1.0
        )
        ax.add_artist(arrow)
        
        # 添加标签
        ax.text(vector_in_basis[0]*1.1, vector_in_basis[1]*1.1, vector_in_basis[2]*1.1, 
               "v", color=color, fontsize=12)
        
        return arrow
    
    def start_animation(self):
        """开始动画"""
        # 获取矩阵
        base_a, base_b, vector = self.get_matrices()
        if base_a is None or base_b is None or vector is None:
            return
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # 显示计算结果
        self.display_results(base_a, base_b, vector)
        
        # 重置子图
        self.create_subplots()
        
        # 绘制原始基下的向量
        self.draw_basis(self.ax_original, base_a)
        self.draw_vector(self.ax_original, base_a, vector)
        
        # 初始化动画参数
        self.animation_running = True
        self.paused = False
        self.current_t = 0
        self.base_a = base_a
        self.base_b = base_b
        self.vector = vector
        
        # 开始动画循环
        self.animate_step()
    
    def animate_step(self):
        """动画单步更新"""
        if not self.animation_running or self.paused:
            return
        
        # 计算当前插值系数
        t = self.current_t / 100  # 0到1之间的值
        
        # 计算当前基矩阵（从A到B的线性插值）
        current_basis = self.base_a * (1-t) + self.base_b * t
        
        # 绘制当前基下的向量
        self.draw_basis(self.ax_animation, current_basis, original=False)
        self.draw_vector(self.ax_animation, current_basis, self.vector)
        
        # 添加进度标签
        self.ax_animation.text2D(0.02, 0.98, f'进度: {t:.2f}',
                  transform=self.ax_animation.transAxes,
                  fontsize=10,
                  bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        # 更新画布
        self.fig.tight_layout()
        self.canvas.draw()
        
        # 更新进度
        self.current_t += 1
        if self.current_t > 100:
            self.current_t = 0
        
        # 设置下一帧
        self.master.after(50, self.animate_step)
    
    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not self.animation_running:
            return
        
        self.paused = not self.paused
        
        if self.paused:
            self.pause_button.config(text="继续动画")
        else:
            self.pause_button.config(text="暂停动画")
            # 继续动画
            self.animate_step()
    
    def reset(self):
        """重置界面"""
        # 停止动画
        self.animation_running = False
        self.paused = False
        
        # 重置按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button.config(text="暂停动画")
        
        # 清空结果显示
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state='disabled')
        
        # 重置子图
        self.create_subplots()
    
    def on_closing(self):
        """处理窗口关闭事件"""
        # 停止动画
        self.animation_running = False
        
        # 清理资源
        plt.close(self.fig)
        
        # 关闭窗口
        self.master.destroy()

    def show_theory(self):
        """显示基变换理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 基变换知识点内容
            sections = {
                "基本概念": """
基：在线性空间中，基是一组线性无关的向量，它们可以张成整个线性空间。也就是说，线性空间中的任何向量都可以表示为这组基向量的线性组合。例如，在二维欧几里得空间R2中，常见的标准基是{(1,0),(0,1)}，平面上的任意向量(x,y)都可以表示为x(1,0)+y(0,1)。

基变换：是指从一个基到另一个基的转换过程。设{e1​,e2​,⋯,en​}和{f​1​,f​2​,⋯,f​n​}是线性空间V的两个基，那么对于V中的任意向量v，它在这两个基下分别有坐标表示X=(x1​,x2​,⋯,xn​)T和Y=(y1​,y2​,⋯,yn​)T，即v=x1​e1​+x2​e2​+⋯+xn​en​=y1​f​1​+y2​f​2​+⋯+yn​f​n​，基变换就是找到这两个坐标之间的关系，以及两个基向量组之间的转换关系。
""",
                "几何意义": """
在几何空间中，基变换可以看作是坐标系的变换。例如，在平面直角坐标系中，从标准直角坐标系变换到一个斜坐标系，就是一种基变换。原来在标准坐标系下的向量，在新的斜坐标系下有了不同的坐标表示，但向量本身的几何位置和长度、夹角等几何性质是不变的。基变换本质上是对空间中向量描述方式的改变，而不改变向量所代表的几何对象的本质特征。
""",
                "计算方法": """
1.过渡矩阵：设从基{e1​,e2​,⋯,en​}到基{f​1​,f​2​,⋯,f​n​}的过渡矩阵为P，则有(f​1​,f​2​,⋯,f​n​)=(e1​,e2​,⋯,en​)P。若已知向量v在基{e1​,e2​,⋯,en​}下的坐标为X，在基{f​1​,f​2​,⋯,f​n​}下的坐标为Y，那么有X=PY。

2.求过渡矩阵：通常是将新基向量用旧基向量线性表示，其系数矩阵就是过渡矩阵。
""",
                "应用": """
1.简化线性变换的表示：在不同的基下，线性变换的矩阵表示可能会有不同的形式。通过选择合适的基，使得线性变换在该基下的矩阵具有简单的形式，如对角矩阵，从而便于对线性变换进行分析和计算。例如，在研究矩阵的特征值和特征向量时，可通过基变换将矩阵相似对角化，进而更方便地求出矩阵的幂、判断矩阵的稳定性等。

2.数据处理与分析：在数据分析中，有时会对数据进行特征提取和降维处理。基变换可以将原始数据从一个高维空间的基表示转换到另一个更能反映数据本质特征的基表示下，例如主成分分析（PCA）就是利用基变换将原始数据投影到一组正交的主成分基上，实现数据的降维和去噪，以便更好地对数据进行分析和处理。

3.解决几何问题：在计算机图形学和几何计算中，基变换可用于实现图形的变换，如旋转、缩放、平移等。通过选择合适的基，可以将复杂的几何变换转化为简单的矩阵运算，提高计算效率和准确性。例如，将三维空间中的图形从世界坐标系转换到物体坐标系或相机坐标系，就需要用到基变换。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "基变换理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建基变换理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("基变换理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="基变换理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="几何意义")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="计算方法")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixTransformationApp(root)
    root.mainloop()
