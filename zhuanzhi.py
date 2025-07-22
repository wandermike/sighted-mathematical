import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# 自定义3D箭头类，更可靠的3D向量绘制
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)

class MatrixAnimationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("矩阵旋转动画可视化")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建左侧控制面板
        self.control_frame = tk.Frame(master, bg='#E6F3FF', width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            self.control_frame,
            text="矩阵旋转动画可视化",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        # 矩阵输入区域
        self.create_matrix_input_area()
        
        # 按钮区域
        self.create_buttons()
        
        # 添加说明文本区域
        self.create_info_text()
        
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
        self.matrix = None
        self.animation_running = False
        self.paused = False
        self.current_angle = 0
        self.arrows = []
        
        # 绑定窗口关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置默认矩阵
        self.set_default_matrix()
    
    def create_matrix_input_area(self):
        """创建矩阵输入区域"""
        matrix_frame = tk.LabelFrame(
            self.control_frame,
            text="输入矩阵",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        matrix_frame.pack(fill=tk.X, pady=10)
        
        # 矩阵大小选择
        size_frame = tk.Frame(matrix_frame, bg='#E6F3FF')
        size_frame.pack(pady=5)
        
        tk.Label(
            size_frame,
            text="矩阵大小：",
            bg='#E6F3FF',
            font=('SimHei', 10)
        ).pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar(value="3")
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["2", "3", "4"],
            state='readonly',
            width=5
        )
        size_combo.pack(side=tk.LEFT, padx=5)
        size_combo.bind('<<ComboboxSelected>>', self.update_matrix_size)
        
        # 创建矩阵输入文本框
        self.matrix_text = tk.Text(
            matrix_frame,
            height=6,
            width=30,
            font=('Consolas', 12),
            relief='solid',
            bg='white',
            fg='#2C3E50'
        )
        self.matrix_text.pack(padx=10, pady=10)
    
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

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="矩阵旋转理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    
    def create_info_text(self):
        """创建说明文本区域"""
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
        self.info_text.pack(pady=20)
        self.info_text.insert('1.0', '操作说明：\n1. 选择矩阵大小并输入矩阵\n2. 点击"开始动画"观看矩阵旋转过程\n3. 可以随时暂停/继续动画\n4. 左侧显示原始矩阵，右侧显示旋转过程')
        self.info_text.config(state='disabled')
    
    def create_subplots(self):
        """创建子图 - 只使用两个子图"""
        self.fig.clear()
        
        # 创建1x2网格的子图
        self.ax_original = self.fig.add_subplot(121, projection='3d')
        self.ax_original.set_title("原始矩阵", fontsize=12)
        
        self.ax_animation = self.fig.add_subplot(122, projection='3d')
        self.ax_animation.set_title("旋转动画", fontsize=12)
        
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
    
    def set_default_matrix(self):
        """设置默认矩阵"""
        size = int(self.size_var.get())
        default_matrix = np.eye(size)
        
        # 格式化矩阵文本
        matrix_text = f"{size} {size}\n"
        for i in range(size):
            row = " ".join([str(int(default_matrix[i, j])) for j in range(size)])
            matrix_text += row + "\n"
        
        # 设置到文本框
        self.matrix_text.delete('1.0', tk.END)
        self.matrix_text.insert('1.0', matrix_text)
    
    def update_matrix_size(self, event=None):
        """更新矩阵大小"""
        self.set_default_matrix()
        self.reset()
    
    def generate_random_matrix(self):
        """生成随机矩阵"""
        size = int(self.size_var.get())
        random_matrix = np.random.randint(-3, 4, (size, size))
        
        # 格式化矩阵文本
        matrix_text = f"{size} {size}\n"
        for i in range(size):
            row = " ".join([str(random_matrix[i, j]) for j in range(size)])
            matrix_text += row + "\n"
        
        # 设置到文本框
        self.matrix_text.delete('1.0', tk.END)
        self.matrix_text.insert('1.0', matrix_text)
    
    def get_matrix_from_text(self):
        """从文本框获取矩阵"""
        try:
            matrix_text = self.matrix_text.get("1.0", tk.END).strip().split('\n')
            rows, cols = map(int, matrix_text[0].split())
            matrix = []
            for i in range(rows):
                row = list(map(int, matrix_text[i + 1].split()))
                matrix.append(row)
            return np.array(matrix)
        except Exception as e:
            messagebox.showerror("错误", f"矩阵格式错误：{str(e)}")
            return None
    
    def get_rotation_matrix(self, angle):
        """获取旋转矩阵"""
        size = len(self.matrix)
        rotation = np.eye(size)
        # 在xy平面上旋转
        rotation[0:2, 0:2] = [
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ]
        return rotation
    
    def draw_matrix(self, ax, matrix, angle=0):
        """绘制矩阵"""
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
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        # 绘制矩阵的每一列作为向量
        size = len(matrix)
        arrows = []
        
        for i in range(size):
            if i < len(colors):
                color = colors[i]
                
                # 获取向量
                if size <= 3:
                    # 如果矩阵维度小于等于3，直接使用
                    vector = np.zeros(3)
                    vector[:size] = matrix[:, i]
                else:
                    # 如果矩阵维度大于3，只显示前3个维度
                    vector = matrix[:3, i]
                
                # 创建3D箭头
                arrow = Arrow3D(
                    [0, vector[0]], [0, vector[1]], [0, vector[2]],
                    mutation_scale=15,
                    lw=2,
                    arrowstyle="-|>",
                    color=color,
                    alpha=0.8
                )
                ax.add_artist(arrow)
                arrows.append(arrow)
                
                # 绘制投影到xy平面的虚线
                ax.plot([0, vector[0]], [0, vector[1]], [0, 0],
                        '--', color=color, alpha=0.3)
        
        # 添加旋转角度标签
        ax.text2D(0.02, 0.98, f'旋转角度: {angle/np.pi:.2f}π',
                  transform=ax.transAxes,
                  fontsize=10,
                  bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        # 设置视角
        ax.view_init(elev=30, azim=45)
        
        return arrows
    
    def start_animation(self):
        """开始动画 - 修改为只使用两个视图"""
        # 获取矩阵
        self.matrix = self.get_matrix_from_text()
        if self.matrix is None:
            return
        
        if self.matrix.shape[0] != self.matrix.shape[1]:
            messagebox.showerror("错误", "请输入方阵！")
            return
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # 重置子图
        self.create_subplots()
        
        # 绘制原始矩阵
        self.draw_matrix(self.ax_original, self.matrix)
        
        # 初始化动画参数
        self.animation_running = True
        self.paused = False
        self.current_angle = 0
        
        # 开始动画循环
        self.animate_step()
    
    def animate_step(self):
        """动画单步更新 - 只更新动画视图"""
        if not self.animation_running or self.paused:
            return
        
        # 计算旋转矩阵
        rotation = self.get_rotation_matrix(self.current_angle)
        rotated_matrix = self.matrix @ rotation
        
        # 绘制动画帧
        self.arrows = self.draw_matrix(self.ax_animation, rotated_matrix, self.current_angle)
        
        # 更新画布
        self.fig.tight_layout()
        self.canvas.draw()
        
        # 更新角度
        self.current_angle += 0.05
        if self.current_angle >= 2 * np.pi:
            self.current_angle = 0
        
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
        """显示矩阵旋转理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 矩阵旋转知识点内容
            sections = {
                "基本概念": """
旋转矩阵是特殊的正交矩阵，用于表示欧几里得空间中的旋转变换。

特性：
- 旋转矩阵是正交矩阵，满足R·Rᵀ = I
- 旋转矩阵的行列式为1（保持方向）
- 旋转保持距离和角度不变（等距变换）

二维旋转矩阵：
R(θ) = [cos(θ) -sin(θ); sin(θ) cos(θ)]

三维旋转需要指定轴和角度，或使用其他表示方法。
""",
            "旋转表示方法": """
表示三维旋转的主要方法：

1. 欧拉角：
   - 使用三个角度分别表示绕三个坐标轴的旋转
   - 常见的顺序有XYZ, ZYX, ZXZ等
   - 优点是直观，缺点是存在万向节锁问题

2. 旋转矩阵：
   - 3×3矩阵直接表示旋转变换
   - 9个元素但只有3个自由度
   - 优点是计算简单，缺点是参数冗余

3. 四元数：
   - 使用四个参数q = [w, x, y, z]表示旋转
   - 避免了万向节锁问题
   - 计算高效且数值稳定，广泛应用于计算机图形学

4. 轴角表示：
   - 指定旋转轴和旋转角度
   - 与四元数密切相关
""",
            "旋转组合": """
旋转的组合与性质：

1. 连续旋转：
   - 两个旋转的组合仍是旋转
   - 旋转矩阵的乘积表示依次执行旋转
   - 注意：矩阵乘法不满足交换律，旋转顺序很重要

2. 插值问题：
   - 在两个旋转之间平滑过渡的问题
   - 线性插值不适用于旋转
   - 球面线性插值(SLERP)可以在四元数之间平滑插值

3. 旋转中心：
   - 二维平面上任何旋转都有一个不动点（旋转中心）
   - 三维空间中，任何旋转都有一个不变的轴（旋转轴）
""",
            "应用": """
1. 计算机图形学：
   - 3D模型的姿态控制
   - 相机视角变换
   - 角色动画中的关节运动

2. 机器人学：
   - 机械臂的运动学和动力学
   - 移动机器人的姿态控制
   - 通过旋转矩阵描述机器人配置

3. 航空航天：
   - 飞行器的姿态控制
   - 导航系统
   - 卫星姿态确定

4. 分子动力学：
   - 分子构型变化的表示
   - 蛋白质折叠模拟

5. 计算机视觉：
   - 相机位姿估计
   - 三维重建
   - 目标跟踪与姿态识别
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "矩阵旋转理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建矩阵旋转理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("矩阵旋转理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="矩阵旋转理论知识", 
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
        notebook.add(geometric_frame, text="旋转表示方法")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="旋转组合")
        
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
    app = MatrixAnimationApp(root)
    root.mainloop()