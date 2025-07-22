"""tezheng.py"""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch

# 设置中文字体，确保汉字正确显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

class Arrow3D(FancyArrowPatch):
    """
    3D 箭头类，用于在 3D 坐标系中绘制向量箭头。
    """
    def __init__(self, xs, ys, zs, *args, **kwargs):
        # xs, ys, zs 为 [起点, 终点] 数据
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)

    def update(self, xs, ys, zs):
        self._verts3d = xs, ys, zs

class EigenvalueApp:
    def __init__(self, master):
        self.master = master
        self.master.title("特征值与特征向量可视化")
        # 设置窗口样式
        style = ttk.Style()
        style.configure('TLabel', background='#E6F3FF')
        style.configure('TCombobox', background='#E6F3FF')
        
        # 创建左侧控制面板
        self.control_frame = tk.Frame(master, bg='#E6F3FF', width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            self.control_frame,
            text="特征值与特征向量可视化",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        # 矩阵输入区域
        matrix_frame = tk.LabelFrame(
            self.control_frame,
            text="输入3×3矩阵",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        matrix_frame.pack(fill=tk.X, pady=10)
        
        # 创建矩阵输入框
        self.matrix_entries = []
        for i in range(3):
            row_frame = tk.Frame(matrix_frame, bg='#E6F3FF')
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
                entry.insert(0, '1' if i == j else '0')
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)
        
        # 按钮区域
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
        
        # 添加随机矩阵按钮
        self.random_button = tk.Button(
            button_frame,
            text="随机矩阵",
            command=self.generate_random_matrix,
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
        
        # 退出按钮
        self.quit_button = tk.Button(
            button_frame,
            text="退出",
            command=self.master.quit,
            **button_style
        )
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
        
        # 添加说明文本区域
        self.info_text = tk.Text(
            self.control_frame,
            height=6,
            width=40,
            font=('SimHei', 11),
            relief='solid',
            bg='white',
            fg='#2C3E50',
            wrap=tk.WORD
        )
        self.info_text.pack(pady=10)
        self.info_text.insert('1.0', '操作说明：\n1. 输入3×3矩阵或使用随机矩阵\n2. 点击"开始动画"观看特征值和特征向量的可视化过程\n3. 可以随时暂停/继续动画\n4. 观察特征向量的方向和特征值的大小')
        self.info_text.config(state='disabled')
        
        # 添加结果显示区域
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
            height=15,
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
        
        # 创建右侧绘图区域
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化动画状态
        self.animation = None
        self.paused = False
        
        # 初始化绘图
        self.reset_plot()

    def get_matrix(self):
        """从输入框获取矩阵"""
        try:
            matrix = []
            for i in range(3):
                row = []
                for j in range(3):
                    # 确保输入为整数
                    value = int(float(self.matrix_entries[i][j].get()))
                    row.append(value)
                matrix.append(row)
            return np.array(matrix)
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数！")
            return None

    def generate_random_matrix(self):
        """生成随机矩阵，元素为1到10的整数"""
        # 生成1到10的随机整数矩阵
        random_matrix = np.random.randint(1, 11, (3, 3))
        # 使矩阵对称以确保特征值为实数
        random_matrix = (random_matrix + random_matrix.T) // 2  # 使用整除确保结果为整数
        
        # 更新输入框
        for i in range(3):
            for j in range(3):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(random_matrix[i,j]))

    def start_animation(self):
        """开始动画"""
        # 获取矩阵
        matrix = self.get_matrix()
        if matrix is None:
            return
        
        try:
            # 计算特征值和特征向量
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            # 确保特征值是实数
            if np.any(np.iscomplex(eigenvalues)):
                messagebox.showerror("错误", "矩阵的特征值包含复数！请使用对称矩阵。")
                return
            
            # 更新按钮状态
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            
            # 显示计算结果
            self.display_results(matrix, eigenvalues, eigenvectors)
            
            # 创建动画
            frames = 60
            
            def update(frame):
                self.ax.clear()
                self.ax.set_xlim([-5, 5])
                self.ax.set_ylim([-5, 5])
                self.ax.set_zlim([-5, 5])
                
                # 设置标签
                self.ax.set_xlabel("X 轴", fontsize=10)
                self.ax.set_ylabel("Y 轴", fontsize=10)
                self.ax.set_zlabel("Z 轴", fontsize=10)
                self.ax.set_title("特征值与特征向量可视化", fontsize=14)
                
                # 绘制坐标轴
                self.ax.plot([-5, 5], [0, 0], [0, 0], 'k--', alpha=0.3)
                self.ax.plot([0, 0], [-5, 5], [0, 0], 'k--', alpha=0.3)
                self.ax.plot([0, 0], [0, 0], [-5, 5], 'k--', alpha=0.3)
                
                t = frame / frames
                
                # 绘制特征向量
                colors = ['r', 'g', 'b']
                for i, (eigenvalue, eigenvector) in enumerate(zip(eigenvalues, eigenvectors.T)):
                    # 计算当前帧的缩放比例
                    scale = t * eigenvalue
                    
                    # 绘制特征向量
                    vector = scale * eigenvector
                    self.ax.quiver(0, 0, 0, vector[0], vector[1], vector[2],
                                 color=colors[i], alpha=0.8, lw=2,
                                 arrow_length_ratio=0.15)
                    
                    # 添加标签
                    if t == 1:
                        self.ax.text(vector[0], vector[1], vector[2],
                                   f'λ{i+1}={eigenvalue:.2f}',
                                   color=colors[i])
                
                # 添加图例
                self.ax.plot([], [], 'r-', label='特征向量1')
                self.ax.plot([], [], 'g-', label='特征向量2')
                self.ax.plot([], [], 'b-', label='特征向量3')
                self.ax.legend()
                
                return []
            
            self.animation = animation.FuncAnimation(
                self.fig, update, frames=frames,
                interval=50, blit=True
            )
            self.canvas.draw()
            
        except np.linalg.LinAlgError:
            messagebox.showerror("错误", "矩阵计算出错！请检查输入。")
            self.reset()

    def toggle_pause(self):
        if self.animation:
            if self.paused:
                self.animation.event_source.start()
            else:
                self.animation.event_source.stop()
            self.paused = not self.paused
            self.pause_button.config(text="继续动画" if self.paused else "暂停动画")

    def show_theory(self):
        """显示特征值与特征向量理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 特征值与特征向量知识点内容
            sections = {
                "基本概念": """
设A是n阶方阵，如果存在数λ和非零n维列向量x，使得Ax=λx成立，则称λ是矩阵A的一个特征值，x是矩阵A属于特征值λ的特征向量。

从定义可以看出，特征向量在矩阵变换下具有特殊的性质，即变换后的向量与原向量共线，而特征值就是描述这种伸缩程度的量。
""",
                "几何意义": """
1.特征向量的方向不变性：矩阵A对特征向量x的作用仅仅是将其拉伸或压缩，而不改变其方向（当特征值为负时，方向相反）。例如，在二维平面中，若一个向量是某个矩阵的特征向量，那么该矩阵对这个向量的变换效果只是使其长度发生变化，向量仍然在原来的直线上。

2.特征值的伸缩比例：特征值λ表示特征向量在矩阵变换下的伸缩比例。∣λ∣>1时，特征向量被拉伸；∣λ∣<1时，特征向量被压缩；λ=1时，特征向量长度不变；λ=0时，特征向量被压缩为零向量；λ<0时，特征向量不仅被拉伸或压缩，而且方向相反。
""",
                "计算方法": """
特征方程法：
计算矩阵A的特征多项式f(λ)=∣λE−A∣，其中E为单位矩阵。然后令f(λ)=0，解这个方程得到的根就是矩阵A的特征值。对于每个特征值λi​，求解齐次线性方程组(λi​E−A)x=0，其非零解就是属于特征值λi​的特征向量。
""",
                "应用": """
1.矩阵对角化：如果矩阵A有n个线性无关的特征向量x1​,x2​,⋯,xn​，设P=(x1​,x2​,⋯,xn​)，则P−1AP=Λ，其中Λ是对角矩阵，其对角线上的元素就是矩阵A的特征值。矩阵对角化在计算矩阵的幂、行列式等方面有很大的便利。

2.线性变换的分析：在描述线性变换时，特征值和特征向量可以帮助我们理解变换的本质。例如，在图像处理中，通过分析图像变换矩阵的特征值和特征向量，可以了解图像在不同方向上的伸缩、旋转等变换特性，从而进行图像压缩、特征提取等操作。

3.动力系统和稳定性分析：在物理、工程等领域的动力系统中，特征值和特征向量可以用来分析系统的稳定性。如果系统矩阵的所有特征值的实部都小于零，那么系统是稳定的；如果存在特征值的实部大于零，系统则是不稳定的。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "特征值与特征向量理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建特征值与特征向量理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("特征值与特征向量理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="特征值与特征向量理论知识", 
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

    def reset(self):
        """重置界面"""
        if hasattr(self, 'animation') and self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
        
        # 重置按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button.config(text="暂停动画")
        self.paused = False
        
        # 重置绘图
        self.reset_plot()
        
        # 清空结果显示
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state='disabled')

    def reset_plot(self):
        # 重置绘图
        self.ax.clear()
        self.ax.set_xlim([-5, 5])
        self.ax.set_ylim([-5, 5])
        self.ax.set_zlim([-5, 5])
        
        # 设置标签
        self.ax.set_xlabel("X 轴", fontsize=10)
        self.ax.set_ylabel("Y 轴", fontsize=10)
        self.ax.set_zlabel("Z 轴", fontsize=10)
        self.ax.set_title("特征值与特征向量可视化", fontsize=14)
        
        # 绘制坐标轴
        self.ax.plot([-5, 5], [0, 0], [0, 0], 'k--', alpha=0.3)
        self.ax.plot([0, 0], [-5, 5], [0, 0], 'k--', alpha=0.3)
        self.ax.plot([0, 0], [0, 0], [-5, 5], 'k--', alpha=0.3)

    def display_results(self, matrix, eigenvalues, eigenvectors):
        """显示特征值和特征向量计算结果"""
        # 清空结果文本
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        
        # 格式化矩阵
        matrix_str = "原始矩阵:\n"
        for row in matrix:
            matrix_str += "  ".join([f"{val:5.2f}" for val in row]) + "\n"
        
        # 格式化特征值和特征向量
        result_str = "\n特征值和特征向量:\n"
        for i, (val, vec) in enumerate(zip(eigenvalues, eigenvectors.T)):
            result_str += f"λ{i+1} = {val:6.3f}\n"
            result_str += f"v{i+1} = ["
            result_str += ", ".join([f"{v:6.3f}" for v in vec])
            result_str += "]\n\n"
        
        # 添加到结果文本
        self.result_text.insert('1.0', matrix_str + result_str)
        
        # 添加特征多项式
        char_poly = np.poly(matrix)
        poly_str = "\n特征多项式:\n|λI - A| = "
        terms = []
        for i, coef in enumerate(char_poly):
            power = len(char_poly) - i - 1
            if coef == 0:
                continue
            if power == 0:
                terms.append(f"{coef:+.2f}")
            elif power == 1:
                terms.append(f"{coef:+.2f}λ")
            else:
                terms.append(f"{coef:+.2f}λ^{power}")
        poly_str += " ".join(terms)
        
        self.result_text.insert(tk.END, poly_str)
        
        # 禁用编辑
        self.result_text.config(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    app = EigenvalueApp(root)
    root.mainloop()
