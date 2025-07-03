import tkinter as tk
from tkinter import ttk

class KnowledgeFrame:
    """通用数学知识点展示框架"""
    
    def __init__(self, master, title, sections):
        """
        初始化知识点框架
        
        参数:
        master -- 父窗口
        title -- 知识框架标题
        sections -- 知识部分的字典，格式为 {"标签名": "内容文本"}
        """
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.geometry("750x600")
        self.window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text=title, 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 添加各部分内容
        for tab_name, content in sections.items():
            tab_frame = ttk.Frame(notebook, padding=10)
            notebook.add(tab_frame, text=tab_name)
            
            # 创建可滚动文本区域
            text_frame = ttk.Frame(tab_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SimHei", 12), 
                             padx=10, pady=10, bg="#ffffff")
            scrollbar = ttk.Scrollbar(text_frame, command=text_area.yview)
            text_area.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 添加内容
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)  # 设为只读
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=self.window.destroy)
        close_button.pack(pady=10) 

    def show_theory(self):
        """显示旋转矩阵理论知识"""
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
旋转矩阵在许多领域有广泛应用：

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
        KnowledgeFrame(self.master, "旋转矩阵理论知识", sections) 

    def show_theory(self):
        """显示过渡矩阵理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 过渡矩阵知识点内容
            sections = {
                "基本概念": """
过渡矩阵是在线性空间中，从一个基到另一个基的变换矩阵。设{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}是线性空间V的两个基，若存在矩阵P，使得(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，则称矩阵P为从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵。
""",
                "几何意义": """
过渡矩阵在几何上可以理解为对线性空间中坐标系的一种变换。它将向量在一个基下的坐标表示转换为在另一个基下的坐标表示，就如同在平面或空间中，从一个坐标系转换到另一个坐标系时，向量的坐标会发生相应的变化，而过渡矩阵描述了这种坐标变换的关系。例如，在二维平面中，从直角坐标系转换到一个斜坐标系，过渡矩阵就确定了向量在这两个不同坐标系下坐标的转换方式，保证向量的几何位置和长度、夹角等几何性质在坐标变换前后保持不变。
""",
                "计算方法": """
方法一：根据定义求解
已知两个基{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}，将每个β​i​用α1​,α2​,⋯,αn​线性表示，即β​i​=p1i​α1​+p2i​α2​+⋯+pni​αn​，其中i=1,2,⋯,n。那么过渡矩阵P=(pij​)n×n​，其中pij​为β​j​在αi​下的坐标分量。

方法二：利用可逆矩阵性质
如果已知基变换的表达式(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，且(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是线性无关的向量组，那么矩阵(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是可逆的。此时可以通过P=(α1​,α2​,⋯,αn​)−1(β​1​,β​2​,⋯,β​n​)来计算过渡矩阵P。
""",
                "应用": """
1.坐标变换：在不同基下向量的坐标通过过渡矩阵进行转换。若向量v在基{α1​,α2​,⋯,αn​}下的坐标为X=(x1​,x2​,⋯,xn​)T，在基{β​1​,β​2​,⋯,β​n​}下的坐标为Y=(y1​,y2​,⋯,yn​)T，且从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有X=PY。这在解决线性空间中向量的坐标表示问题时非常有用，方便在不同的基下对向量进行分析和计算。

2.线性变换的矩阵表示：设线性变换T在基{α1​,α2​,⋯,αn​}下的矩阵为A，在基{β​1​,β​2​,⋯,β​n​}下的矩阵为B，从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有B=P−1AP。通过选择合适的基，利用过渡矩阵可以将线性变换的矩阵化为相似标准形，如对角矩阵，从而简化线性变换的计算和性质研究，例如求线性变换的特征值、判断线性变换的可对角化等问题。

3.几何变换：在计算机图形学和几何计算中，过渡矩阵可用于实现图形的各种几何变换，如旋转、缩放、平移等。通过将图形的顶点坐标在不同的基下进行转换，利用过渡矩阵可以方便地实现图形在不同坐标系或不同表示方式下的变换，提高图形处理的效率和灵活性。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "过渡矩阵理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建过渡矩阵理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("过渡矩阵理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="过渡矩阵理论知识", 
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

        