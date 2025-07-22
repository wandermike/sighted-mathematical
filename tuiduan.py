import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import stats
import math

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class HypothesisTestingApp:
    def __init__(self, master):
        self.master = master
        master.title("假设检验可视化工具")
        self.master.geometry("1200x800")

        # 创建主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标题
        title_label = ttk.Label(main_frame, text="假设检验可视化", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # --- 创建布局 ---
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(main_frame, text="检验设置")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 右侧绘图和结果区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 绘图区域
        plot_frame = ttk.Frame(right_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 结果显示区域
        result_frame = ttk.LabelFrame(right_frame, text="检验结果")
        result_frame.pack(fill=tk.X, pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=6, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- 控制面板内容 ---
        # 1. 选择检验类型
        ttk.Label(self.control_frame, text="选择检验类型:").pack(anchor=tk.W, pady=(10, 2))
        self.test_type_var = tk.StringVar(value="单样本Z检验 (总体方差已知)")
        test_combobox = ttk.Combobox(self.control_frame, textvariable=self.test_type_var,
                                     values=[
                                         "单样本Z检验 (总体方差已知)",
                                         "单样本t检验 (总体方差未知)",
                                         # "双样本t检验 (独立样本)", # 待添加
                                         # "配对样本t检验",       # 待添加
                                         # "卡方拟合优度检验",    # 待添加
                                         # "卡方独立性检验",    # 待添加
                                         # "单因素方差分析 (ANOVA)" # 待添加
                                     ], width=30)
        test_combobox.pack(anchor=tk.W, pady=2, fill=tk.X)
        test_combobox.bind("<<ComboboxSelected>>", self.on_test_type_change)

        # 2. 备择假设类型
        ttk.Label(self.control_frame, text="备择假设 (H1):").pack(anchor=tk.W, pady=(10, 2))
        self.alternative_var = tk.StringVar(value="双侧检验 (≠)")
        alt_combobox = ttk.Combobox(self.control_frame, textvariable=self.alternative_var,
                                    values=["双侧检验 (≠)", "左侧检验 (<)", "右侧检验 (>)"], width=30)
        alt_combobox.pack(anchor=tk.W, pady=2, fill=tk.X)
        alt_combobox.bind("<<ComboboxSelected>>", lambda e: self.perform_test()) # 实时更新

        # 3. 检验参数框架 (动态生成)
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.X, pady=10)

        # 4. 显著性水平 alpha
        ttk.Label(self.control_frame, text="显著性水平 (α):").pack(anchor=tk.W, pady=(10, 2))
        self.alpha_var = tk.DoubleVar(value=0.05)
        alpha_scale = ttk.Scale(self.control_frame, from_=0.01, to=0.2, variable=self.alpha_var,
                                orient=tk.HORIZONTAL, command=self.update_alpha_display)
        alpha_scale.pack(fill=tk.X)
        self.alpha_label = ttk.Label(self.control_frame, text=f"α = {self.alpha_var.get():.3f}")
        self.alpha_label.pack(anchor=tk.W)

        # 5. 执行按钮 (虽然很多是实时更新，但保留一个明确的按钮)
        # self.run_button = ttk.Button(self.control_frame, text="执行检验", command=self.perform_test)
        # self.run_button.pack(pady=20)

        # --- 初始化 ---
        self.current_params = {} # 用于存储当前检验所需的参数控件变量
        self.create_test_params() # 创建初始参数控件
        self.perform_test()       # 执行初始检验和绘图

    def update_alpha_display(self, value):
        """更新alpha显示标签并重新执行检验"""
        self.alpha_label.config(text=f"α = {self.alpha_var.get():.3f}")
        self.perform_test()

    def on_test_type_change(self, event):
        """切换检验类型时，重新创建参数输入控件并执行检验"""
        self.create_test_params()
        self.perform_test()

    def create_test_params(self):
        """根据选择的检验类型动态创建参数输入控件"""
        # 清除旧控件和参数
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.current_params.clear()

        test_type = self.test_type_var.get()

        if test_type == "单样本Z检验 (总体方差已知)":
            self.add_param("样本均值 (x̄):", tk.DoubleVar(value=10.5), -5, 25)
            self.add_param("总体均值 (μ₀):", tk.DoubleVar(value=10.0), -5, 25)
            self.add_param("总体标准差 (σ):", tk.DoubleVar(value=2.0), 0.1, 10)
            self.add_param("样本量 (n):", tk.IntVar(value=30), 2, 200, is_int=True)

        elif test_type == "单样本t检验 (总体方差未知)":
            self.add_param("样本均值 (x̄):", tk.DoubleVar(value=21.5), 0, 40)
            self.add_param("总体均值 (μ₀):", tk.DoubleVar(value=20.0), 0, 40)
            self.add_param("样本标准差 (s):", tk.DoubleVar(value=3.0), 0.1, 10)
            self.add_param("样本量 (n):", tk.IntVar(value=25), 2, 200, is_int=True)

        # --- 为其他检验类型添加参数 ---
        # elif test_type == "双样本t检验 (独立样本)":
        #     ...
        # elif test_type == "卡方拟合优度检验":
        #     ...

    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 添加理论知识按钮
        theory_button = ttk.Button(
            button_frame, 
            text="假设检验理论知识", 
            command=self.show_theory
        )
        theory_button.pack(fill=tk.X, pady=5)

    def add_param(self, label_text, var, from_, to, is_int=False):
        """辅助函数：添加一个参数控件（标签、滑块、输入框）"""
        frame = ttk.Frame(self.param_frame)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label_text, width=18).pack(side=tk.LEFT)

        # 使用 partial 传递参数给回调
        update_func = lambda v, v_var=var: self.perform_test()
        scale_update_func = lambda v, v_var=var, entry=None: [self.update_param_entry(entry, v_var.get()), self.perform_test()]

        scale = ttk.Scale(frame, from_=from_, to=to, variable=var,
                          orient=tk.HORIZONTAL, command=update_func)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        entry = ttk.Entry(frame, width=8, textvariable=var)
        entry.pack(side=tk.LEFT)
        # 绑定输入框更新事件 (防抖动)
        entry.bind("<KeyRelease>", lambda e: self.master.after(500, self.perform_test))

        # 更新滑块命令以包含输入框更新
        scale.config(command=lambda v, v_var=var, e=entry: [self.update_param_entry(e, v_var.get()), self.perform_test()])

        # 存储变量以便后续获取值
        param_key = label_text.split(" ")[0] # 使用标签的第一个词作为键
        self.current_params[param_key] = var

    def update_param_entry(self, entry, value):
        """更新参数输入框的值"""
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, f"{value:.2f}" if isinstance(value, float) else f"{int(value)}")


    def perform_test(self):
        """执行选定的假设检验并更新图表和结果"""
        test_type = self.test_type_var.get()
        alpha = self.alpha_var.get()
        alternative_map = {
            "双侧检验 (≠)": "two-sided",
            "左侧检验 (<)": "less",
            "右侧检验 (>)": "greater"
        }
        alternative = alternative_map[self.alternative_var.get()]

        params = {key: var.get() for key, var in self.current_params.items()}

        try:
            if test_type == "单样本Z检验 (总体方差已知)":
                x_bar = params["样本均值"]
                mu0 = params["总体均值"]
                sigma = params["总体标准差"]
                n = params["样本量"]
                if n < 2 or sigma <= 0:
                    raise ValueError("样本量需 >= 2, 总体标准差需 > 0")

                # 计算检验统计量 Z
                se = sigma / math.sqrt(n) # 标准误
                z_stat = (x_bar - mu0) / se

                # 计算 p 值
                if alternative == 'two-sided':
                    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                elif alternative == 'less':
                    p_value = stats.norm.cdf(z_stat)
                else: # 'greater'
                    p_value = 1 - stats.norm.cdf(z_stat)

                # 获取临界值
                if alternative == 'two-sided':
                    crit_val_lower = stats.norm.ppf(alpha / 2)
                    crit_val_upper = stats.norm.ppf(1 - alpha / 2)
                    crit_val = (crit_val_lower, crit_val_upper)
                elif alternative == 'less':
                    crit_val = stats.norm.ppf(alpha)
                else: # 'greater'
                    crit_val = stats.norm.ppf(1 - alpha)

                # 绘制标准正态分布
                self.plot_distribution(stats.norm, z_stat, crit_val, p_value, alpha, alternative, df=None)
                # 显示结果
                self.display_results(z_stat, p_value, crit_val, alpha, alternative, "Z")


            elif test_type == "单样本t检验 (总体方差未知)":
                x_bar = params["样本均值"]
                mu0 = params["总体均值"]
                s = params["样本标准差"]
                n = params["样本量"]
                if n < 2 or s <= 0:
                    raise ValueError("样本量需 >= 2, 样本标准差需 > 0")

                df = n - 1 # 自由度
                se = s / math.sqrt(n) # 标准误
                t_stat = (x_bar - mu0) / se

                # 计算 p 值
                if alternative == 'two-sided':
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
                elif alternative == 'less':
                    p_value = stats.t.cdf(t_stat, df)
                else: # 'greater'
                    p_value = 1 - stats.t.cdf(t_stat, df)

                # 获取临界值
                if alternative == 'two-sided':
                    crit_val_lower = stats.t.ppf(alpha / 2, df)
                    crit_val_upper = stats.t.ppf(1 - alpha / 2, df)
                    crit_val = (crit_val_lower, crit_val_upper)
                elif alternative == 'less':
                    crit_val = stats.t.ppf(alpha, df)
                else: # 'greater'
                    crit_val = stats.t.ppf(1 - alpha, df)

                # 绘制 t 分布
                self.plot_distribution(stats.t, t_stat, crit_val, p_value, alpha, alternative, df=df)
                # 显示结果
                self.display_results(t_stat, p_value, crit_val, alpha, alternative, "t", df)

            # --- 添加其他检验类型的逻辑 ---

        except ValueError as ve:
            messagebox.showerror("参数错误", str(ve))
            self.clear_plot()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"参数错误: {str(ve)}")
        except Exception as e:
            messagebox.showerror("计算错误", f"执行检验时发生错误: {str(e)}")
            self.clear_plot()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"计算错误: {str(e)}")


    def plot_distribution(self, dist, stat_val, crit_val, p_value, alpha, alternative, df=None):
        """绘制分布图，标记拒绝域、检验统计量和p值区域"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # 确定绘图范围
        if df is None: # 正态分布
            x_min, x_max = -4, 4
            if abs(stat_val) > 3.5: # 动态调整范围以包含统计量
                 x_min = min(x_min, stat_val - 0.5)
                 x_max = max(x_max, stat_val + 0.5)
            if isinstance(crit_val, tuple) and (abs(crit_val[0]) > 3.5 or abs(crit_val[1]) > 3.5):
                 x_min = min(x_min, crit_val[0] - 0.5)
                 x_max = max(x_max, crit_val[1] + 0.5)
            elif not isinstance(crit_val, tuple) and abs(crit_val) > 3.5:
                 x_min = min(x_min, crit_val - 0.5) if alternative=='less' else x_min
                 x_max = max(x_max, crit_val + 0.5) if alternative=='greater' else x_max

            x = np.linspace(x_min, x_max, 500)
            y = dist.pdf(x)
            dist_name = "标准正态分布"
        else: # t 分布
            x_min, x_max = stats.t.ppf(0.001, df), stats.t.ppf(0.999, df)
            # 动态调整范围
            x_min = min(x_min, stat_val - 0.5, -4)
            x_max = max(x_max, stat_val + 0.5, 4)
            if isinstance(crit_val, tuple):
                 x_min = min(x_min, crit_val[0] - 0.5)
                 x_max = max(x_max, crit_val[1] + 0.5)
            elif not isinstance(crit_val, tuple):
                 x_min = min(x_min, crit_val - 0.5) if alternative=='less' else x_min
                 x_max = max(x_max, crit_val + 0.5) if alternative=='greater' else x_max

            x = np.linspace(x_min, x_max, 500)
            y = dist.pdf(x, df)
            dist_name = f"t 分布 (df={df})"

        ax.plot(x, y, 'b-', label=f'{dist_name} PDF')

        # 绘制拒绝域
        if alternative == 'two-sided':
            crit_lower, crit_upper = crit_val
            x_fill_lower = np.linspace(x_min, crit_lower, 100)
            y_fill_lower = dist.pdf(x_fill_lower, df) if df else dist.pdf(x_fill_lower)
            ax.fill_between(x_fill_lower, y_fill_lower, color='red', alpha=0.5, label=f'拒绝域 (α/2={alpha/2:.3f})')

            x_fill_upper = np.linspace(crit_upper, x_max, 100)
            y_fill_upper = dist.pdf(x_fill_upper, df) if df else dist.pdf(x_fill_upper)
            ax.fill_between(x_fill_upper, y_fill_upper, color='red', alpha=0.5)
            ax.axvline(crit_lower, color='r', linestyle='--', lw=1)
            ax.axvline(crit_upper, color='r', linestyle='--', lw=1)
            ax.text(crit_lower, ax.get_ylim()[1]*0.05, f'{crit_lower:.2f}', ha='right', color='red')
            ax.text(crit_upper, ax.get_ylim()[1]*0.05, f'{crit_upper:.2f}', ha='left', color='red')

        elif alternative == 'less':
            x_fill = np.linspace(x_min, crit_val, 100)
            y_fill = dist.pdf(x_fill, df) if df else dist.pdf(x_fill)
            ax.fill_between(x_fill, y_fill, color='red', alpha=0.5, label=f'拒绝域 (α={alpha:.3f})')
            ax.axvline(crit_val, color='r', linestyle='--', lw=1)
            ax.text(crit_val, ax.get_ylim()[1]*0.05, f'{crit_val:.2f}', ha='right', color='red')

        else: # 'greater'
            x_fill = np.linspace(crit_val, x_max, 100)
            y_fill = dist.pdf(x_fill, df) if df else dist.pdf(x_fill)
            ax.fill_between(x_fill, y_fill, color='red', alpha=0.5, label=f'拒绝域 (α={alpha:.3f})')
            ax.axvline(crit_val, color='r', linestyle='--', lw=1)
            ax.text(crit_val, ax.get_ylim()[1]*0.05, f'{crit_val:.2f}', ha='left', color='red')

        # 标记检验统计量
        stat_y = dist.pdf(stat_val, df) if df else dist.pdf(stat_val)
        ax.plot(stat_val, stat_y, 'go', markersize=8, label=f'检验统计量 = {stat_val:.3f}')
        ax.vlines(stat_val, 0, stat_y, color='g', linestyle='-', lw=2)

        # 可选：标记p值区域 (可能与拒绝域重叠，用不同颜色或图案)
        # ... (这部分可以后续添加，需要根据p值和alternative类型填充对应区域)

        ax.set_title(f"{self.test_type_var.get()} - {self.alternative_var.get()}", fontsize=14)
        ax.set_xlabel("检验统计量值")
        ax.set_ylabel("概率密度")
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas.draw()

    def display_results(self, stat_val, p_value, crit_val, alpha, alternative, stat_name, df=None):
        """在文本框中显示检验结果"""
        self.result_text.delete(1.0, tk.END)
        result_text = f"检验类型: {self.test_type_var.get()}\n"
        result_text += f"备择假设: H₁ {self.alternative_var.get().split(' ')[1]}\n"
        result_text += f"显著性水平 α: {alpha:.3f}\n"
        if df:
            result_text += f"自由度 df: {df}\n"
        result_text += "------------------------------------\n"
        result_text += f"检验统计量 ({stat_name}): {stat_val:.4f}\n"
        result_text += f"P 值: {p_value:.4f}\n"

        if isinstance(crit_val, tuple):
            result_text += f"临界值: ({crit_val[0]:.4f}, {crit_val[1]:.4f})\n"
        else:
            result_text += f"临界值: {crit_val:.4f}\n"
        result_text += "------------------------------------\n"

        # 判断结论
        conclusion = ""
        reject = False
        if alternative == 'two-sided':
            if abs(stat_val) > abs(crit_val[1]): # 或 stat_val < crit_val[0] or stat_val > crit_val[1]
                reject = True
        elif alternative == 'less':
            if stat_val < crit_val:
                reject = True
        else: # 'greater'
            if stat_val > crit_val:
                reject = True

        # 也可以直接用 p 值判断
        # if p_value < alpha:
        #     reject = True

        if reject:
            conclusion = f"结论: 在 α = {alpha:.3f} 水平下，拒绝原假设 H₀。"
            if p_value < 0.001:
                 conclusion += f" (P值 < 0.001)"
            else:
                 conclusion += f" (P值 = {p_value:.4f})"
        else:
            conclusion = f"结论: 在 α = {alpha:.3f} 水平下，未能拒绝原假设 H₀。"
            if p_value < 0.001:
                 conclusion += f" (P值 < 0.001)"
            else:
                 conclusion += f" (P值 = {p_value:.4f})"


        result_text += conclusion + "\n"

        self.result_text.insert(tk.END, result_text)

    def clear_plot(self):
        """清除图像"""
        self.fig.clear()
        self.canvas.draw()

    def show_theory(self):
        """显示假设检验理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 假设检验知识点内容
            sections = {
                "基本概念": """
1.原假设与备择假设：
原假设（H0​）是研究者想收集证据予以反对的假设，通常是关于总体参数的一个特定陈述，比如总体均值等于某个特定值、两个总体均值相等之类。备择假设（H1​）是研究者想收集证据予以支持的假设，是与原假设相互对立的假设。

2.检验统计量：
根据样本数据计算出来的用于判断是否拒绝原假设的统计量。不同的假设检验问题有不同的检验统计量，如Z统计量、t统计量、χ2统计量等。其值的大小决定了是否拒绝原假设。

3.显著性水平：
用α表示，是事先设定的一个概率值，用于判断原假设是否成立。它表示当原假设为真时，拒绝原假设的概率，也就是犯第一类错误（弃真错误）的概率。常见的α取值有0.05、0.01等。

4.拒绝域与接受域：
根据检验统计量的分布和显著性水平，将样本空间划分为两个区域。拒绝域是使得原假设被拒绝的检验统计量的取值范围；接受域则是使得原假设不被拒绝的检验统计量的取值范围。
""",
                "计算步骤": """
1.提出原假设和备择假设：
根据研究问题和实际情况，明确需要检验的假设。

2.选择合适的检验统计量：
根据总体分布、样本量以及已知条件等因素，选择相应的检验统计量。

3.确定显著性水平：
根据问题的性质和要求，确定合适的显著性水平α。

4.计算检验统计量的值：
根据样本数据，计算出所选检验统计量的具体值。

5.做出决策：
将计算得到的检验统计量的值与拒绝域进行比较。如果检验统计量的值落在拒绝域内，则拒绝原假设，接受备择假设；否则，不拒绝原假设。
""",
                "应用": """
1.医学领域：
用于检验某种新药是否有效。例如，原假设是新药与安慰剂效果相同，备择假设是新药比安慰剂更有效。通过对患者进行分组试验，收集数据进行假设检验，来判断新药是否真的具有疗效。

2.工业生产：
在生产过程中，检验产品质量是否符合标准。如假设某批产品的次品率不超过5%为原假设，超过5%为备择假设。通过抽取一定数量的样本进行检测，利用假设检验判断该批产品是否合格。

3.社会科学研究：
比如研究不同教育方法对学生成绩的影响。原假设可以是两种教育方法对学生成绩没有显著差异，备择假设是两种教育方法对学生成绩有显著差异。通过对采用不同教育方法的学生进行成绩测试和假设检验，来分析教育方法的有效性。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "假设检验理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建假设检验理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("假设检验理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="假设检验理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")

        # 影响因素选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="计算步骤")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10) 


# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = HypothesisTestingApp(root)
    root.mainloop()
