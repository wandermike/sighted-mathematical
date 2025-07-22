import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class ProbabilityApp:
    def __init__(self, master):
        self.master = master
        master.title("概率分布可视化工具")
        self.master.geometry("1200x800")
        
        # 创建主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="概率分布可视化", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # 创建左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="参数设置")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 创建右侧绘图区域
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建绘图区域
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 创建分布类型选择下拉框
        ttk.Label(control_frame, text="选择分布类型:").pack(anchor=tk.W, pady=5)
        self.distribution_var = tk.StringVar()
        self.distribution_combobox = ttk.Combobox(control_frame, textvariable=self.distribution_var, 
                                                 values=["二项分布", "泊松分布", "正态分布"])
        self.distribution_combobox.current(0)
        self.distribution_combobox.pack(anchor=tk.W, pady=5)
        self.distribution_combobox.bind("<<ComboboxSelected>>", self.on_distribution_change)
        
        # 创建参数输入区域（改为滑块）
        self.param_frame = ttk.LabelFrame(control_frame, text="参数设置")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建滑块变量
        self.n_var = tk.IntVar(value=10)
        self.p_var = tk.DoubleVar(value=0.5)
        self.lambda_var = tk.DoubleVar(value=5)
        self.mu_var = tk.DoubleVar(value=0)
        self.sigma_var = tk.DoubleVar(value=1)
        
        # 创建按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.plot_button = ttk.Button(button_frame, text="绘制分布图", command=self.plot_distribution)
        self.plot_button.pack(side=tk.LEFT, padx=5)
         
        self.clear_button = ttk.Button(button_frame, text="清除图像", command=self.clear_plot)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            button_frame, 
            text="概率分布理论知识", 
            command=self.show_theory
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
        
        # 在控制面板添加
        self.lock_view = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="锁定视图", variable=self.lock_view).pack()
        
        # 在初始化时添加
        self.entries = []  # 初始化为空列表
        
        # 初始化参数滑块
        self.create_binomial_params()
        
        # 添加这两个属性初始化
        self.last_distribution = None  # 记录上次分布类型
        self.last_xlim = None         # 记录上次 x 轴范围
        self.last_ylim = None         # 记录上次 y 轴范围
        
    def create_binomial_params(self):
        # 清除之前的控件
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        # 试验次数滑块
        ttk.Label(self.param_frame, text="试验次数 (n):").pack(anchor=tk.W, pady=2)
        ttk.Scale(self.param_frame, from_=1, to=50, variable=self.n_var,
                  orient=tk.HORIZONTAL, 
                  command=lambda v: [self.update_entry(self.n_entry, v), self.plot_distribution()]).pack(fill=tk.X)
        self.n_entry = ttk.Entry(self.param_frame, width=10)
        self.n_entry.pack(anchor=tk.W)
        self.n_entry.insert(0, "10")
        
        # 成功概率滑块
        ttk.Label(self.param_frame, text="成功概率 (p):").pack(anchor=tk.W, pady=2)
        ttk.Scale(self.param_frame, from_=0, to=1, variable=self.p_var,
                  orient=tk.HORIZONTAL, 
                  command=lambda v: [self.update_entry(self.p_entry, v), self.plot_distribution()]).pack(fill=tk.X)
        self.p_entry = ttk.Entry(self.param_frame, width=10)
        self.p_entry.pack(anchor=tk.W)
        self.p_entry.insert(0, "0.5")
        
        self.entries.clear()
        self.entries.extend([self.n_entry, self.p_entry])
        # 绑定输入事件
        for entry in self.entries:
            entry.bind("<KeyRelease>", lambda e: self.master.after(500, self.plot_distribution))
    
    def create_poisson_params(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.param_frame, text="均值 (λ):").pack(anchor=tk.W, pady=2)
        ttk.Scale(self.param_frame, from_=0.1, to=20, variable=self.lambda_var,
                 orient=tk.HORIZONTAL, 
                 command=lambda v: [self.update_entry(self.lambda_entry, v), self.plot_distribution()]).pack(fill=tk.X)
        self.lambda_entry = ttk.Entry(self.param_frame, width=10)
        self.lambda_entry.pack(anchor=tk.W)
        self.lambda_entry.insert(0, "5")
        
        self.entries.clear()
        self.entries.append(self.lambda_entry)
        for entry in self.entries:
            entry.bind("<KeyRelease>", lambda e: self.master.after(500, self.plot_distribution))
    
    def create_normal_params(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.param_frame, text="均值 (μ):").pack(anchor=tk.W, pady=2)
        ttk.Scale(self.param_frame, from_=-5, to=5, variable=self.mu_var,
                 orient=tk.HORIZONTAL, 
                 command=lambda v: [self.update_entry(self.mu_entry, v), self.plot_distribution()]).pack(fill=tk.X)
        self.mu_entry = ttk.Entry(self.param_frame, width=10)
        self.mu_entry.pack(anchor=tk.W)
        self.mu_entry.insert(0, "0")
        
        ttk.Label(self.param_frame, text="标准差 (σ):").pack(anchor=tk.W, pady=2)
        ttk.Scale(self.param_frame, from_=0.1, to=5, variable=self.sigma_var,
                 orient=tk.HORIZONTAL, 
                 command=lambda v: [self.update_entry(self.sigma_entry, v), self.plot_distribution()]).pack(fill=tk.X)
        self.sigma_entry = ttk.Entry(self.param_frame, width=10)
        self.sigma_entry.pack(anchor=tk.W)
        self.sigma_entry.insert(0, "1")
        
        self.entries.clear()
        self.entries.extend([self.mu_entry, self.sigma_entry])
        for entry in self.entries:
            entry.bind("<KeyRelease>", lambda e: self.master.after(500, self.plot_distribution))
    
    def update_entry(self, entry_widget, value):
        """同步滑块和输入框的值"""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, f"{float(value):.2f}")
    
    def on_distribution_change(self, event):
        distribution = self.distribution_var.get()
        if distribution == "二项分布":
            self.create_binomial_params()
        elif distribution == "泊松分布":
            self.create_poisson_params()
        elif distribution == "正态分布":
            self.create_normal_params()
    
    def plot_distribution(self):
        distribution = self.distribution_var.get()
        
        # 如果锁定视图开启且分布类型未变，并且之前保存了轴范围，则恢复这些范围
        if self.lock_view.get() and (distribution == self.last_distribution) \
           and (self.last_xlim is not None) and (self.last_ylim is not None):
            locked_xlim = self.last_xlim
            locked_ylim = self.last_ylim
        else:
            locked_xlim, locked_ylim = None, None
        
        # 清除图像但保留坐标轴设置
        self.ax.cla()
        
        try:
            if distribution == "二项分布":
                n = self.n_var.get()
                p = self.p_var.get()
                
                # 设置固定坐标轴范围
                self.ax.set_xlim(-0.5, n+0.5)
                self.ax.set_ylim(0, 1)
                
                if n <= 0 or p < 0 or p > 1:
                    messagebox.showerror("输入错误", "试验次数必须大于0，成功概率必须在0到1之间！")
                    return
                
                # 生成二项分布数据
                x = np.arange(0, n+1)
                y = np.array([self.binomial_prob(k, n, p) for k in x])
                
                # 绘制柱状图
                self.ax.bar(x, y, color='skyblue', edgecolor='black')
                self.ax.set_title(f"二项分布 (n={n}, p={p})", fontsize=20)
                self.ax.set_xlabel("成功次数")
                self.ax.set_ylabel("概率")
            
            elif distribution == "泊松分布":
                lambd = self.lambda_var.get()
                
                # 设置固定坐标轴范围
                self.ax.set_xlim(-0.5, 3*lambd+0.5)
                self.ax.set_ylim(0, 0.4 if lambd < 5 else 0.3)
                
                if lambd <= 0:
                    messagebox.showerror("输入错误", "均值必须大于0！")
                    return
                
                # 生成泊松分布数据
                x = np.arange(0, int(lambd) * 3 + 1)
                y = np.array([self.poisson_prob(k, lambd) for k in x])
                
                # 绘制柱状图
                self.ax.bar(x, y, color='lightgreen', edgecolor='black')
                self.ax.set_title(f"泊松分布 (λ={lambd})", fontsize=20)
                self.ax.set_xlabel("事件发生次数")
                self.ax.set_ylabel("概率")
            
            elif distribution == "正态分布":
                mu = self.mu_var.get()
                sigma = self.sigma_var.get()
                
                # 设置固定坐标轴范围（4σ原则）
                self.ax.set_xlim(mu-4*sigma, mu+4*sigma)
                self.ax.set_ylim(0, 1/(sigma*np.sqrt(2*np.pi)) * 1.2)
                
                if sigma <= 0:
                    messagebox.showerror("输入错误", "标准差必须大于0！")
                    return
                
                # 生成正态分布数据
                x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
                y = self.normal_prob(x, mu, sigma)
                
                # 绘制曲线图
                self.ax.plot(x, y, color='blue')
                self.ax.fill_between(x, y, color='lightblue', alpha=0.3)
                self.ax.set_title(f"正态分布 (μ={mu}, σ={sigma})", fontsize=20)
                self.ax.set_xlabel("值")
                self.ax.set_ylabel("概率密度")
            
            # 如果之前有锁定的视图则恢复
            if locked_xlim is not None and locked_ylim is not None:
                self.ax.set_xlim(locked_xlim)
                self.ax.set_ylim(locked_ylim)
            else:
                # 否则更新记录当前的轴范围
                self.last_xlim = self.ax.get_xlim()
                self.last_ylim = self.ax.get_ylim()
            
            self.last_distribution = distribution
            self.canvas.draw()
        
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
    
    def clear_plot(self):
        self.ax.clear()
        self.canvas.draw()
        
    
    @staticmethod
    def binomial_prob(k, n, p):
        from math import comb
        return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    
    @staticmethod
    def poisson_prob(k, lambd):
        from math import factorial, exp
        return (lambd ** k) * exp(-lambd) / factorial(k)
    
    @staticmethod
    def normal_prob(x, mu, sigma):
        import numpy as np
        return np.exp(-(x - mu)**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))

    def debounced_plot(self, _):
        # 实时更新，不延迟
        self.plot_distribution()

    def show_theory(self):
        """显示概率分布理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 概率分布知识点内容
            sections = {
                "二项分布": """
基本概念：
二项分布是n重伯努利试验成功次数的离散概率分布。伯努利试验是指只有两种可能结果的单次随机试验，即“成功”和“失败”。若进行n次独立的伯努利试验，每次试验成功的概率为p，失败的概率为1−p，那么在n次试验中成功k次的概率分布就是二项分布，记为X∼B(n,p)。

特点：
  1.试验次数n是固定的。
  2.每次试验相互独立，即每次试验的结果不会影响其他试验的结果。
  3.每次试验只有两种结果：成功或失败。
  4.成功的概率p在每次试验中保持不变。

应用：
广泛应用于各种具有明确成功和失败定义的场景。例如，在产品质量检测中，已知产品的次品率，求抽检n个产品中出现k个次品的概率；在选举预测中，已知选民支持某候选人的比例，预测在n个选民中，有k个人支持该候选人的概率等。
""",
                "泊松分布": """
基本概念：
泊松分布是一种用于描述在固定时间或空间内，某事件发生的次数的离散概率分布。它通常用于描述稀有事件在一段时间或空间内发生的次数，即事件发生的概率p很小，而试验次数n很大的情况。记为X∼P(λ)，其中λ为单位时间或空间内事件发生的平均次数。

特点：
  1.事件是独立发生的，即一个事件的发生不会影响其他事件发生的概率。
  2.在短时间或小空间内，事件发生的概率与时间长度或空间大小成正比。
  3.事件发生的次数是可数的，且取值为非负整数。

应用：
常用于分析单位时间内电话呼叫次数、交通流量、放射性物质衰变次数、商场顾客到达人数等问题。例如，某医院急诊室在一天内接待的紧急病人数量，假设病人的到达是随机且独立的，就可以用泊松分布来分析不同病人数量出现的概率。
""",
                "正态分布": """
基本概念：
正态分布又称高斯分布，是一种连续型概率分布，其概率密度函数的图像呈钟形曲线，具有对称性。若随机变量X服从正态分布，记为X∼N(μ,σ^2)，其中μ为均值，决定了分布的中心位置；σ^2为方差，决定了分布的离散程度。

特点：
  1.概率密度函数关于x=μ对称，即P(X≤μ)=P(X≥μ)=0.5。
  2.曲线在x=μ处达到峰值​。
  3.当x离μ越远，概率密度函数的值越小，且以x轴为渐近线。
  4.正态分布的线性组合仍服从正态分布。

应用：
在自然科学、社会科学、工程技术等众多领域都有广泛应用。例如，人的身高、体重、智商等生理和心理特征的分布通常近似服从正态分布；在质量控制中，产品的尺寸、重量等指标也往往服从正态分布，通过对正态分布的分析可以设定质量控制的标准和范围；在金融领域，股票收益率、风险评估等方面也会用到正态分布。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "概率分布理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建概率分布理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("概率分布理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="概率分布理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="二项分布")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="泊松分布")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="正态分布")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)    

if __name__ == "__main__":
    root = tk.Tk()
    app = ProbabilityApp(root)
    root.mainloop()