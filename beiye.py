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

class BayesianApp:
    def __init__(self, master):
        self.master = master
        master.title("贝叶斯统计可视化工具")
        self.master.geometry("1200x800")

        # 创建主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标题
        title_label = ttk.Label(main_frame, text="贝叶斯推断可视化", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # --- 创建布局 ---
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(main_frame, text="模型与参数设置")
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
        result_frame = ttk.LabelFrame(right_frame, text="推断结果")
        result_frame.pack(fill=tk.X, pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- 控制面板内容 ---
        # 1. 选择模型类型
        ttk.Label(self.control_frame, text="选择模型:").pack(anchor=tk.W, pady=(10, 2))
        self.model_type_var = tk.StringVar(value="二项分布 - Beta先验 (Beta-Binomial)")
        model_combobox = ttk.Combobox(self.control_frame, textvariable=self.model_type_var,
                                     values=[
                                         "二项分布 - Beta先验 (Beta-Binomial)",
                                         "正态均值 (方差已知) - 正态先验 (Normal-Normal)",
                                         # "泊松分布 - Gamma先验 (Gamma-Poisson)" # 待添加
                                     ], width=40)
        model_combobox.pack(anchor=tk.W, pady=2, fill=tk.X)
        model_combobox.bind("<<ComboboxSelected>>", self.on_model_type_change)

        # 2. 参数框架 (动态生成)
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 3. 锁定视图按钮
        self.lock_view_var = tk.BooleanVar(value=False)
        lock_button = ttk.Checkbutton(self.control_frame, text="锁定视图 (仅更新结果)",
                                      variable=self.lock_view_var, command=self.update_model)
        lock_button.pack(anchor=tk.W, pady=(10, 5))


        # --- 初始化 ---
        self.current_params = {} # 用于存储当前所需的参数控件变量
        self._after_id = None # For debouncing entry updates
        self.create_params_ui() # 创建初始参数控件
        self.update_model()     # 执行初始计算和绘图

    def on_model_type_change(self, event):
        """切换模型类型时，重新创建参数输入控件并计算"""
        self.create_params_ui()
        self.update_model()

    def create_params_ui(self):
        """根据选择的模型类型动态创建参数输入控件"""
        # 清除旧控件和参数
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.current_params = {}

        model_type = self.model_type_var.get()

        if model_type == "二项分布 - Beta先验 (Beta-Binomial)":
            # 先验参数 (Beta 分布: α₀, β₀)
            prior_frame = ttk.LabelFrame(self.param_frame, text="先验分布 (Beta)")
            prior_frame.pack(fill=tk.X, pady=5)
            self.add_param(prior_frame, "先验 Alpha (α₀):", tk.DoubleVar(value=1.0), 0.1, 20.0)
            self.add_param(prior_frame, "先验 Beta (β₀):", tk.DoubleVar(value=1.0), 0.1, 20.0)

            # 似然参数/数据 (二项分布: n, k)
            likelihood_frame = ttk.LabelFrame(self.param_frame, text="数据 (二项分布)")
            likelihood_frame.pack(fill=tk.X, pady=5)
            self.add_param(likelihood_frame, "试验次数 (n):", tk.IntVar(value=10), 0, 100, is_int=True)
            self.add_param(likelihood_frame, "成功次数 (k):", tk.IntVar(value=5), 0, 100, is_int=True) 

        elif model_type == "正态均值 (方差已知) - 正态先验 (Normal-Normal)":
             # 先验参数 (正态分布 for μ: μ₀, σ₀²)
            prior_frame = ttk.LabelFrame(self.param_frame, text="先验分布 (μ ~ Normal)")
            prior_frame.pack(fill=tk.X, pady=5)
            self.add_param(prior_frame, "先验均值 (μ₀):", tk.DoubleVar(value=0.0), -10.0, 10.0)
            self.add_param(prior_frame, "先验方差 (σ₀²):", tk.DoubleVar(value=1.0), 0.1, 10.0)

            # 似然参数/数据 (正态分布 data: σ², n, x̄)
            likelihood_frame = ttk.LabelFrame(self.param_frame, text="数据 (来自 Normal(μ, σ²))")
            likelihood_frame.pack(fill=tk.X, pady=5)
            self.add_param(likelihood_frame, "数据方差 (σ²):", tk.DoubleVar(value=1.0), 0.1, 10.0) # Known variance
            self.add_param(likelihood_frame, "样本量 (n):", tk.IntVar(value=10), 1, 100, is_int=True)
            self.add_param(likelihood_frame, "样本均值 (x̄):", tk.DoubleVar(value=0.0), -10.0, 10.0)

        else:
            ttk.Label(self.param_frame, text="该模型尚未实现").pack()

        # Special handling for Beta-Binomial k <= n constraint
        if model_type == "二项分布 - Beta先验 (Beta-Binomial)":
            n_var = self.current_params.get("试验次数 (n)")
            k_var = self.current_params.get("成功次数 (k)")
            if n_var and k_var:
                # Find the scale and entry for k
                k_scale = None
                k_entry = None
                for child in likelihood_frame.winfo_children():
                    if isinstance(child, ttk.Frame): # Find the inner frame for k
                         scale_found = False
                         entry_found = False
                         for grandchild in child.winfo_children():
                             if isinstance(grandchild, ttk.Scale) and grandchild.cget("variable") == str(k_var):
                                 k_scale = grandchild
                                 scale_found = True
                             if isinstance(grandchild, ttk.Entry) and grandchild.cget("textvariable") == str(k_var):
                                 k_entry = grandchild
                                 entry_found = True
                         if scale_found and entry_found:
                             break

                if k_scale and k_entry:
                    # Function to update k's scale range and value
                    def update_k_range(*args):
                        try:
                            n_val = n_var.get()
                            k_val = k_var.get()
                            k_scale.config(to=n_val) # Update scale's upper limit
                            if k_val > n_val:
                                k_var.set(n_val) # Adjust k if it exceeds n
                                self.update_entry_from_scale(k_var, k_entry, n_val) # Update entry too
                            self.update_model() # Recalculate when n changes
                        except tk.TclError: # Handle potential errors during widget destruction/creation
                            pass

                    # Trace changes in n_var to update k's range
                    n_var.trace_add("write", update_k_range)
                    # Initial update in case n is not default
                    update_k_range()

    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 添加理论知识按钮
        theory_button = ttk.Button(
            button_frame, 
            text="贝叶斯统计理论知识", 
            command=self.show_theory
        )
        theory_button.pack(fill=tk.X, pady=5)

    def add_param(self, parent_frame, label_text, var, from_, to):
        """辅助函数：添加标签、滑块和输入框"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)

        entry = ttk.Entry(frame, width=8, textvariable=var)
        entry.pack(side=tk.RIGHT, padx=5)
        # Update variable from entry using debouncing
        entry.bind("<KeyRelease>", lambda event, v=var, e=entry: self.debounce_entry_update(v, e))

        scale = ttk.Scale(frame, from_=from_, to=to, variable=var,
                          orient=tk.HORIZONTAL,
                          command=lambda val, v=var, e=entry: self.update_entry_from_scale(v, e, val)) # Update entry during drag
        # Bind plot update to mouse release for scales
        scale.bind("<ButtonRelease-1>", lambda event: self.update_model())
        scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Store variable for easy access using the label as key (simplified)
        param_key = label_text.split(':')[0].strip() # Extract key like "先验 Alpha (α₀)"
        self.current_params[param_key] = var


    def update_entry_from_scale(self, var, entry_widget, value_str):
        """当滑块移动时，更新对应的输入框内容"""
        try:
            value = float(value_str)
            # Check if the variable is an IntVar or DoubleVar
            if isinstance(var, tk.IntVar):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(int(value)))
            else: # DoubleVar
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, f"{value:.2f}") # Format float
        except (ValueError, tk.TclError): # Catch potential errors during update/widget access
            pass

    def debounce_entry_update(self, var, entry_widget):
        """延迟更新，避免在输入过程中频繁触发计算"""
        if self._after_id:
            self.master.after_cancel(self._after_id)
        # Schedule the update
        self._after_id = self.master.after(500, lambda v=var, e=entry_widget: self.update_var_from_entry_and_plot(v, e))

    def update_var_from_entry_and_plot(self, var, entry_widget):
        """从输入框更新变量并触发重新计算和绘图"""
        try:
            value_str = entry_widget.get()
            # Check if the variable is an IntVar or DoubleVar
            if isinstance(var, tk.IntVar):
                value = int(value_str)
            else: # DoubleVar
                value = float(value_str)

            # Special check for Beta-Binomial k <= n
            model_type = self.model_type_var.get()
            if model_type == "二项分布 - Beta先验 (Beta-Binomial)":
                 if var == self.current_params.get("成功次数 (k)"):
                     n_val = self.current_params.get("试验次数 (n)").get()
                     if value > n_val:
                         value = n_val # Cap k at n
                         entry_widget.delete(0, tk.END)
                         entry_widget.insert(0, str(value)) # Update entry visually

            var.set(value) # Update the tk.Variable
            self.update_model() # Trigger recalculation
        except (ValueError, tk.TclError):
            # Optional: Add visual feedback for invalid input
            print(f"Invalid input: {value_str}")
            pass # Don't update if input is not a valid number
        except Exception as e:
             print(f"Error updating variable: {e}")


    def update_model(self):
        """根据当前参数计算后验分布并更新图表和结果"""
        is_locked = self.lock_view_var.get()
        model_type = self.model_type_var.get()

        try:
            params = {key: var.get() for key, var in self.current_params.items()}

            prior_dist = None
            posterior_dist = None
            likelihood_func = None # Function p(data|param)
            plot_range = None
            param_name = ""
            results_info = {}

            if model_type == "二项分布 - Beta先验 (Beta-Binomial)":
                alpha0 = params.get("先验 Alpha (α₀)")
                beta0 = params.get("先验 Beta (β₀)")
                n = params.get("试验次数 (n)")
                k = params.get("成功次数 (k)")

                if any(v is None for v in [alpha0, beta0, n, k]) or alpha0 <= 0 or beta0 <= 0 or n < 0 or k < 0 or k > n:
                    if not is_locked: self.clear_plot()
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "请输入有效的参数：α₀ > 0, β₀ > 0, n ≥ 0, 0 ≤ k ≤ n")
                    return

                param_name = "θ (成功概率)"
                prior_dist = stats.beta(alpha0, beta0)
                # Posterior parameters
                alpha_post = alpha0 + k
                beta_post = beta0 + n - k
                posterior_dist = stats.beta(alpha_post, beta_post)
                plot_range = (0, 1)

                # Likelihood function P(k|n, theta) = C(n,k) * theta^k * (1-theta)^(n-k)
                # We plot the shape proportional to theta^k * (1-theta)^(n-k)
                likelihood_func = lambda theta: (theta**k) * ((1-theta)**(n-k)) if 0 < theta < 1 else 0

                results_info = {
                    "先验分布": f"Beta(α₀={alpha0:.2f}, β₀={beta0:.2f})",
                    "数据": f"n={n}, k={k}",
                    "后验分布": f"Beta(α₁={alpha_post:.2f}, β₁={beta_post:.2f})",
                    "后验均值 E[θ|data]": posterior_dist.mean(),
                    "后验众数 Mode[θ|data]": (alpha_post - 1) / (alpha_post + beta_post - 2) if alpha_post > 1 and beta_post > 1 else "N/A",
                    "后验95%可信区间": posterior_dist.interval(0.95)
                }


            elif model_type == "正态均值 (方差已知) - 正态先验 (Normal-Normal)":
                mu0 = params.get("先验均值 (μ₀)")
                var0 = params.get("先验方差 (σ₀²)")
                var_data = params.get("数据方差 (σ²)") # Likelihood variance (known)
                n = params.get("样本量 (n)")
                x_bar = params.get("样本均值 (x̄)")

                if any(v is None for v in [mu0, var0, var_data, n, x_bar]) or var0 <= 0 or var_data <= 0 or n < 1:
                    if not is_locked: self.clear_plot()
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "请输入有效的参数：σ₀² > 0, σ² > 0, n ≥ 1")
                    return

                param_name = "μ (总体均值)"
                prior_dist = stats.norm(loc=mu0, scale=math.sqrt(var0))

                # Posterior parameters
                precision0 = 1 / var0
                precision_data = n / var_data
                var_post = 1 / (precision0 + precision_data)
                mu_post = var_post * (precision0 * mu0 + precision_data * x_bar)
                posterior_dist = stats.norm(loc=mu_post, scale=math.sqrt(var_post))

                # Determine a reasonable plot range based on prior and posterior
                m1, s1 = prior_dist.mean(), prior_dist.std()
                m2, s2 = posterior_dist.mean(), posterior_dist.std()
                plot_min = min(m1 - 4*s1, m2 - 4*s2)
                plot_max = max(m1 + 4*s1, m2 + 4*s2)
                plot_range = (plot_min, plot_max)

                # Likelihood function P(x_bar|n, sigma^2, mu) ∝ exp(-n/(2*sigma^2) * (x_bar - mu)^2)
                # This is a normal distribution shape centered at x_bar with variance sigma^2/n
                likelihood_scale = math.sqrt(var_data / n)
                likelihood_func = lambda mu: stats.norm.pdf(mu, loc=x_bar, scale=likelihood_scale)


                results_info = {
                    "先验分布": f"Normal(μ₀={mu0:.2f}, σ₀²={var0:.2f})",
                    "数据": f"n={n}, x̄={x_bar:.2f}, σ²={var_data:.2f}",
                    "后验分布": f"Normal(μ₁={mu_post:.2f}, σ₁²={var_post:.2f})",
                    "后验均值 E[μ|data]": posterior_dist.mean(),
                    "后验95%可信区间": posterior_dist.interval(0.95)
                }

            # --- Plotting ---
            if not is_locked and prior_dist and posterior_dist and plot_range:
                self.plot_distributions(prior_dist, posterior_dist, likelihood_func, plot_range, param_name, model_type)

            # --- Display Results ---
            self.display_results(results_info, model_type)

        except Exception as e:
            messagebox.showerror("计算错误", f"发生错误: {e}")
            if not is_locked: self.clear_plot()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"计算时发生错误: {e}")

    def plot_distributions(self, prior, posterior, likelihood_func, plot_range, param_name, model_title):
        """绘制先验、似然（形状）和后验分布"""
        if self.lock_view_var.get():
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        x = np.linspace(plot_range[0], plot_range[1], 500)

        # Plot Prior
        prior_pdf = prior.pdf(x)
        ax.plot(x, prior_pdf, label=f'先验 P({param_name})', color='blue', linestyle='--')
        ax.fill_between(x, prior_pdf, color='blue', alpha=0.1)

        # Plot Posterior
        posterior_pdf = posterior.pdf(x)
        ax.plot(x, posterior_pdf, label=f'后验 P({param_name}|Data)', color='red', linewidth=2)
        ax.fill_between(x, posterior_pdf, color='red', alpha=0.2)

        # Plot Likelihood Shape (scaled to fit)
        if likelihood_func:
            likelihood_vals = np.array([likelihood_func(val) for val in x])
            # Scale likelihood to roughly match the height of prior/posterior for visibility
            max_pdf = max(np.max(prior_pdf), np.max(posterior_pdf))
            max_like = np.max(likelihood_vals)
            if max_like > 1e-6: # Avoid division by zero or tiny numbers
                 likelihood_scaled = likelihood_vals * (max_pdf / max_like) * 0.7 # Scale factor
                 ax.plot(x, likelihood_scaled, label='似然函数形状 P(Data|{})'.format(param_name), color='green', linestyle=':')


        ax.set_xlabel(param_name)
        ax.set_ylabel("概率密度 / 似然度 (标准化)")
        ax.set_title(f"{model_title} 推断", fontsize=14)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        # Set xlim explicitly for Beta distribution
        if plot_range == (0, 1):
            ax.set_xlim(0, 1)
        ax.set_ylim(bottom=0) # Ensure y-axis starts at 0

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def display_results(self, results_info, model_type):
        """在文本框中显示推断结果"""
        self.result_text.delete(1.0, tk.END)
        result_text = f"模型类型: {model_type}\n"
        result_text += "------------------------------------\n"
        for key, value in results_info.items():
            if isinstance(value, (float, np.float64)):
                result_text += f"{key}: {value:.4f}\n"
            elif isinstance(value, tuple) and len(value) == 2: # Credible interval
                 result_text += f"{key}: [{value[0]:.4f}, {value[1]:.4f}]\n"
            else:
                result_text += f"{key}: {value}\n"
        result_text += "------------------------------------\n"

        # Add interpretation based on model
        if "Beta-Binomial" in model_type:
             post_mean = results_info.get("后验均值 E[θ|data]", "N/A")
             ci = results_info.get("后验95%可信区间", ["N/A", "N/A"])
             if post_mean != "N/A":
                 result_text += f"解释: 基于先验知识和观察到的数据({results_info.get('数据')}), "
                 result_text += f"我们估计成功概率 θ 的后验均值为 {post_mean:.4f}。\n"
                 result_text += f"我们有95%的信心认为真实的 θ 落在区间 [{ci[0]:.4f}, {ci[1]:.4f}] 之内。\n"
        elif "Normal-Normal" in model_type:
             post_mean = results_info.get("后验均值 E[μ|data]", "N/A")
             ci = results_info.get("后验95%可信区间", ["N/A", "N/A"])
             if post_mean != "N/A":
                 result_text += f"解释: 基于先验知识和观察到的数据({results_info.get('数据')}), "
                 result_text += f"我们估计总体均值 μ 的后验均值为 {post_mean:.4f}。\n"
                 result_text += f"我们有95%的信心认为真实的 μ 落在区间 [{ci[0]:.4f}, {ci[1]:.4f}] 之内。\n"


        self.result_text.insert(tk.END, result_text)

    def clear_plot(self):
        """清除图像 (if view is not locked)"""
        if self.lock_view_var.get():
            return
        self.fig.clear()
        try:
            self.fig.add_subplot(111) # Re-add subplot
        except ValueError: # Already exists
            pass
        self.canvas.draw_idle()

    def show_theory(self):
        """显示贝叶斯统计理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 贝叶斯统计知识点内容
            sections = {
                "基本概念": """
1.先验概率：
在进行试验或观察之前，根据以往的经验或知识对事件发生的概率所做的估计。通常用P(A)表示事件A的先验概率。例如，在抛一枚均匀硬币之前，我们根据经验认为正面朝上的概率是0.5，这就是先验概率。

2.后验概率：
在得到新的观测数据或信息之后，对事件发生概率的重新估计。用P(A∣B)表示在事件B发生的条件下，事件A发生的后验概率。例如，已知某个袋子里有红、白两种颜色的球，先验概率是随机摸出一个红球的概率为0.6，但当我们摸出一个球观察到是白色后，此时根据这个新信息，摸出红球的后验概率就会发生变化。

3.似然函数：
给定参数θ时，观测数据x出现的概率，记为P(x∣θ)。它描述了在不同参数值下，观察到现有数据的可能性。例如，在一个抛硬币的实验中，假设硬币正面朝上的概率为θ，如果我们抛了10次硬币，观察到6次正面朝上，那么似然函数P(x∣θ)就表示在参数θ下，出现这种观测结果的概率。

4.贝叶斯定理：
是贝叶斯统计的核心公式，它提供了一种根据先验概率、似然函数和观测数据来计算后验概率的方法。公式为P(θ∣x)=P(x∣θ)P(θ)/P(x)​，其中P(θ)是先验概率，P(x∣θ)是似然函数，P(x)是观测数据x的边缘概率，P(θ∣x)是后验概率。
""",
                "应用": """
1.医疗诊断：
用于根据患者的症状、检查结果等信息来判断患者患有某种疾病的概率。例如，已知某种疾病在人群中的发病率（先验概率），以及某项检查对于该疾病的检测准确率（似然函数），当患者进行该项检查后，可通过贝叶斯定理计算出患者患病的后验概率，帮助医生做出更准确的诊断。

2.机器学习：
在分类算法中，如朴素贝叶斯分类器，利用贝叶斯定理来计算给定特征下属于不同类别的概率，从而对数据进行分类。例如，在文本分类中，根据单词在不同类别文本中出现的频率（似然函数）以及各类别文本的先验概率，计算出一篇新文本属于某个类别的后验概率，进而将文本分类到相应的类别中。

3.风险评估：
在金融领域，用于评估投资项目的风险。根据历史数据和市场信息确定先验概率，再结合新的经济指标、公司财务状况等观测数据，通过贝叶斯统计方法更新对投资项目成功或失败概率的估计，帮助投资者做出决策。

4.质量控制：
在生产过程中，通过对产品样本的检测来推断整批产品的质量状况。根据以往的生产数据确定产品合格的先验概率，再结合对当前样本的检测结果（似然函数），利用贝叶斯统计计算出整批产品合格的后验概率，决定是否需要对生产过程进行调整。
"""
        
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "贝叶斯统计理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建贝叶斯统计理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("贝叶斯统计理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="贝叶斯统计理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
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
    app = BayesianApp(root)
    root.mainloop()
