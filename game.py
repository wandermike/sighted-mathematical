import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
from collections import Counter

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# Roulette definitions (European)
ROULETTE_NUMBERS = list(range(37)) # 0-36
ROULETTE_RED = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
ROULETTE_BLACK = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
ROULETTE_GREEN = {0}

class GamePuzzleApp:
    def __init__(self, master):
        self.master = master
        master.title("概率游戏与谜题")
        self.master.geometry("1200x800")

        # --- State ---
        self.current_game_type = tk.StringVar(value="蒙提霍尔问题")

        # Monty Hall State
        self.monty_sim_results = {'switch_wins': 0, 'stay_wins': 0, 'total_sims': 0}
        self.monty_num_sims_var = tk.IntVar(value=1000)

        # Coin Toss State
        self.cointoss_num_flips_var = tk.IntVar(value=100)
        self.cointoss_bias_var = tk.DoubleVar(value=0.5) # Probability of Heads
        self.cointoss_results = {'heads': 0, 'tails': 0, 'total_flips': 0, 'bias': 0.5}

        # Dice Roll State
        self.dice_num_rolls_var = tk.IntVar(value=100)
        self.dice_num_dice_var = tk.IntVar(value=2)
        self.dice_results = {'counts': Counter(), 'total_rolls': 0, 'num_dice': 2}

        # Roulette State
        self.roulette_num_spins_var = tk.IntVar(value=100)
        self.roulette_results = {'counts': Counter(), 'red': 0, 'black': 0, 'green': 0, 'even': 0, 'odd': 0, 'total_spins': 0}


        # --- Main Layout ---
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="概率游戏与谜题", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Left Control Panel
        self.control_frame = ttk.LabelFrame(main_frame, text="游戏/谜题设置")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, ipadx=5)

        # Right Area (Plot + Results)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Plot Area (for simulation results)
        plot_frame = ttk.Frame(right_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Results Area (for text descriptions/results)
        result_frame = ttk.LabelFrame(right_frame, text="说明与结果")
        result_frame.pack(fill=tk.X, pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- Control Panel Widgets ---
        # 1. Game Type Selection
        ttk.Label(self.control_frame, text="选择游戏/谜题:").pack(anchor=tk.W, pady=(10, 5))
        game_combobox = ttk.Combobox(self.control_frame, textvariable=self.current_game_type,
                                     values=["蒙提霍尔问题", "抛硬币", "掷骰子", "轮盘赌"], # Updated list
                                     width=35, state="readonly")
        game_combobox.pack(fill=tk.X, pady=2)
        game_combobox.bind("<<ComboboxSelected>>", self.on_game_type_change)

        # 2. Dynamic Parameter Frame
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # --- Initial Setup ---
        self.create_ui_for_game() # Create UI for the default game
        self.update_display()     # Run initial simulation/calculation

    def on_game_type_change(self, event=None):
        """Handles switching between different games/puzzles."""
        self.clear_param_ui()
        self.create_ui_for_game()
        self.update_display() # Update with default parameters for the new game

    def clear_param_ui(self):
        """Removes all widgets from the parameter frame."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        # Also clear plot and results for clarity when switching
        self.ax.clear()
        self.canvas.draw_idle()
        self.result_text.delete(1.0, tk.END)


    def create_ui_for_game(self):
        """Creates the specific UI controls based on the selected game type."""
        game_type = self.current_game_type.get()
        self.control_frame.config(text=f"设置 ({game_type})") # Update frame label

        if game_type == "蒙提霍尔问题":
            self.create_monty_hall_ui()
        elif game_type == "抛硬币":
            self.create_cointoss_ui()
        elif game_type == "掷骰子":
            self.create_dice_ui()
        elif game_type == "轮盘赌":
            self.create_roulette_ui()
        else:
            ttk.Label(self.param_frame, text="未知类型").pack()

    # --- Monty Hall Specific ---

    def create_monty_hall_ui(self):
        """Creates UI elements for the Monty Hall Problem."""
        ttk.Label(self.param_frame, text="模拟次数:").pack(anchor=tk.W, pady=(10, 2))
        sims_scale = ttk.Scale(self.param_frame, from_=100, to=10000, variable=self.monty_num_sims_var,
                               orient=tk.HORIZONTAL, command=lambda v: self.monty_sims_label.config(text=f"{int(float(v))} 次"))
        sims_scale.pack(fill=tk.X)
        self.monty_sims_label = ttk.Label(self.param_frame, text=f"{self.monty_num_sims_var.get()} 次")
        self.monty_sims_label.pack(anchor=tk.W)

        run_button = ttk.Button(self.param_frame, text="运行模拟", command=self.run_monty_hall_simulation)
        run_button.pack(pady=20)

        # 添加理论知识按钮
        #theory_button = ttk.Button(
        #    self.param_frame, 
        #    text="概率游戏理论知识", 
        #   command=self.show_theory
        #)
        #theory_button.pack(pady=20)

    def run_monty_hall_simulation(self):
        """Runs the Monty Hall simulation for the specified number of trials."""
        num_simulations = self.monty_num_sims_var.get()
        if num_simulations <= 0:
            messagebox.showerror("错误", "模拟次数必须大于 0。")
            return

        switch_wins = 0
        stay_wins = 0
        doors = [1, 2, 3]

        for _ in range(num_simulations):
            # 1. Setup: Place prize, Player chooses
            prize_door = random.choice(doors)
            player_choice = random.choice(doors)

            # 2. Host opens a door
            possible_host_choices = [d for d in doors if d != player_choice and d != prize_door]
            host_opens = random.choice(possible_host_choices)

            # 3. Player decides (Simulate both strategies)
            # Strategy 1: Stay
            if player_choice == prize_door:
                stay_wins += 1

            # Strategy 2: Switch
            switch_choice = [d for d in doors if d != player_choice and d != host_opens][0]
            if switch_choice == prize_door:
                switch_wins += 1

        self.monty_sim_results = {
            'switch_wins': switch_wins,
            'stay_wins': stay_wins,
            'total_sims': num_simulations
        }
        self.update_display() # Update plot and text

    def plot_monty_hall_results(self):
        """Plots the win rates for switching vs. staying."""
        self.ax.clear()
        results = self.monty_sim_results
        total = results['total_sims']

        if total == 0:
            self.ax.set_title("蒙提霍尔问题模拟结果 (无数据)")
            self.canvas.draw_idle()
            return

        stay_rate = results['stay_wins'] / total
        switch_rate = results['switch_wins'] / total

        strategies = ['坚持选择', '更换选择']
        win_rates = [stay_rate, switch_rate]

        bars = self.ax.bar(strategies, win_rates, color=['skyblue', 'lightcoral'])
        self.ax.set_ylabel("获胜概率")
        self.ax.set_title(f"蒙提霍尔问题模拟结果 ({total} 次)")
        self.ax.set_ylim(0, 1)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Add percentage labels on bars
        for bar in bars:
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2%}', va='bottom', ha='center') # va: vertical alignment

        self.canvas.draw_idle()

    def display_monty_hall_results(self):
        """Displays explanation and simulation results for Monty Hall."""
        self.result_text.delete(1.0, tk.END)
        description = """
蒙提霍尔问题说明：
在一个游戏节目中，你面前有三扇门。一扇门后面有一辆汽车，另外两扇门后面是山羊。
1. 你选择一扇门（例如，门1）。
2. 主持人（知道汽车在哪扇门后面）打开另一扇有山羊的门（例如，门3）。
3. 主持人问你："你想换成选择另一扇未打开的门（门2）吗？"

问题：你应该坚持原来的选择，还是更换选择？哪种策略获胜的概率更高？

模拟结果显示了大量重复实验后，两种策略的获胜概率。
"""
        self.result_text.insert(tk.END, description)
        self.result_text.insert(tk.END, "\n" + "="*40 + "\n")

        results = self.monty_sim_results
        total = results['total_sims']
        if total > 0:
            stay_rate = results['stay_wins'] / total
            switch_rate = results['switch_wins'] / total
            result_str = f"模拟总次数: {total}\n"
            result_str += f"坚持选择获胜次数: {results['stay_wins']} (概率: {stay_rate:.2%})\n"
            result_str += f"更换选择获胜次数: {results['switch_wins']} (概率: {switch_rate:.2%})\n"
            self.result_text.insert(tk.END, result_str)
        else:
            self.result_text.insert(tk.END, "尚未运行模拟。")

    # --- Coin Toss Specific ---

    def create_cointoss_ui(self):
        """Creates UI elements for Coin Toss simulation."""
        # Number of Flips
        ttk.Label(self.param_frame, text="抛掷次数:").pack(anchor=tk.W, pady=(10, 2))
        flips_scale = ttk.Scale(self.param_frame, from_=10, to=5000, variable=self.cointoss_num_flips_var,
                               orient=tk.HORIZONTAL, command=lambda v: self.cointoss_flips_label.config(text=f"{int(float(v))} 次"))
        flips_scale.pack(fill=tk.X)
        self.cointoss_flips_label = ttk.Label(self.param_frame, text=f"{self.cointoss_num_flips_var.get()} 次")
        self.cointoss_flips_label.pack(anchor=tk.W)

        # Coin Bias (Probability of Heads)
        ttk.Label(self.param_frame, text="正面朝上概率 (Bias):").pack(anchor=tk.W, pady=(10, 2))
        bias_scale = ttk.Scale(self.param_frame, from_=0.0, to=1.0, variable=self.cointoss_bias_var,
                               orient=tk.HORIZONTAL, command=lambda v: self.cointoss_bias_label.config(text=f"{float(v):.2f}"))
        bias_scale.pack(fill=tk.X)
        self.cointoss_bias_label = ttk.Label(self.param_frame, text=f"{self.cointoss_bias_var.get():.2f}")
        self.cointoss_bias_label.pack(anchor=tk.W)

        run_button = ttk.Button(self.param_frame, text="运行模拟", command=self.run_cointoss_simulation)
        run_button.pack(pady=20)

    def run_cointoss_simulation(self):
        """Runs the Coin Toss simulation."""
        num_flips = self.cointoss_num_flips_var.get()
        bias = self.cointoss_bias_var.get()
        if not (0 <= bias <= 1):
            messagebox.showerror("错误", "正面概率必须在 0 和 1 之间。")
            return
        if num_flips <= 0:
            messagebox.showerror("错误", "抛掷次数必须大于 0。")
            return

        heads = 0
        for _ in range(num_flips):
            if random.random() < bias:
                heads += 1

        self.cointoss_results = {
            'heads': heads,
            'tails': num_flips - heads,
            'total_flips': num_flips,
            'bias': bias
        }
        self.update_display()

    def plot_cointoss_results(self):
        """Plots the results of the coin toss simulation."""
        self.ax.clear()
        results = self.cointoss_results
        total = results['total_flips']

        if total == 0:
            self.ax.set_title("抛硬币模拟结果 (无数据)")
            self.canvas.draw_idle()
            return

        heads_freq = results['heads'] / total
        tails_freq = results['tails'] / total
        bias = results['bias']
        expected_heads_freq = bias
        expected_tails_freq = 1 - bias

        outcomes = ['正面 (Heads)', '反面 (Tails)']
        observed_freqs = [heads_freq, tails_freq]
        expected_freqs = [expected_heads_freq, expected_tails_freq]

        bar_width = 0.35
        index = np.arange(len(outcomes))

        bars1 = self.ax.bar(index, observed_freqs, bar_width, label='观测频率', color='skyblue')
        bars2 = self.ax.bar(index + bar_width, expected_freqs, bar_width, label='期望频率 (根据Bias)', color='lightcoral')

        self.ax.set_ylabel("频率")
        self.ax.set_title(f"抛硬币模拟结果 ({total} 次, 正面概率={bias:.2f})")
        self.ax.set_xticks(index + bar_width / 2)
        self.ax.set_xticklabels(outcomes)
        self.ax.set_ylim(0, 1)
        self.ax.legend()
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Add percentage labels
        for bar in bars1 + bars2:
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2%}', va='bottom', ha='center')

        self.canvas.draw_idle()

    def display_cointoss_results(self):
        """Displays explanation and results for Coin Toss."""
        self.result_text.delete(1.0, tk.END)
        description = """
抛硬币模拟：
模拟重复抛掷一枚可能不均匀的硬币。
- 设定总抛掷次数。
- 设定硬币正面朝上的概率 (Bias)。 Bias=0.5 代表均匀硬币。
- 模拟将显示观测到的正面和反面频率，并与基于 Bias 的期望频率进行比较。
"""
        self.result_text.insert(tk.END, description)
        self.result_text.insert(tk.END, "\n" + "="*40 + "\n")

        results = self.cointoss_results
        total = results['total_flips']
        if total > 0:
            bias = results['bias']
            obs_h_freq = results['heads'] / total
            obs_t_freq = results['tails'] / total
            exp_h_freq = bias
            exp_t_freq = 1 - bias

            result_str = f"模拟参数:\n"
            result_str += f"  抛掷次数: {total}\n"
            result_str += f"  设定正面概率 (Bias): {bias:.3f}\n"
            result_str += "观测结果:\n"
            result_str += f"  正面次数: {results['heads']} (频率: {obs_h_freq:.3f})\n"
            result_str += f"  反面次数: {results['tails']} (频率: {obs_t_freq:.3f})\n"
            result_str += "期望结果 (基于Bias):\n"
            result_str += f"  期望正面频率: {exp_h_freq:.3f}\n"
            result_str += f"  期望反面频率: {exp_t_freq:.3f}\n"
            self.result_text.insert(tk.END, result_str)
        else:
            self.result_text.insert(tk.END, "尚未运行模拟。")

    # --- Dice Roll Specific ---

    def create_dice_ui(self):
        """Creates UI elements for Dice Roll simulation."""
        # Number of Rolls
        ttk.Label(self.param_frame, text="投掷次数:").pack(anchor=tk.W, pady=(10, 2))
        rolls_scale = ttk.Scale(self.param_frame, from_=10, to=10000, variable=self.dice_num_rolls_var,
                               orient=tk.HORIZONTAL, command=lambda v: self.dice_rolls_label.config(text=f"{int(float(v))} 次"))
        rolls_scale.pack(fill=tk.X)
        self.dice_rolls_label = ttk.Label(self.param_frame, text=f"{self.dice_num_rolls_var.get()} 次")
        self.dice_rolls_label.pack(anchor=tk.W)

        # Number of Dice
        ttk.Label(self.param_frame, text="骰子数量:").pack(anchor=tk.W, pady=(10, 2))
        # Using Combobox for limited choices, could use Scale/Entry for more
        dice_combo = ttk.Combobox(self.param_frame, textvariable=self.dice_num_dice_var,
                                  values=[1, 2, 3], width=5, state="readonly")
        dice_combo.pack(anchor=tk.W)
        dice_combo.current(1) # Default to 2 dice

        run_button = ttk.Button(self.param_frame, text="运行模拟", command=self.run_dice_simulation)
        run_button.pack(pady=20)

    def run_dice_simulation(self):
        """Runs the Dice Roll simulation."""
        num_rolls = self.dice_num_rolls_var.get()
        num_dice = self.dice_num_dice_var.get()
        if num_rolls <= 0 or num_dice <= 0:
            messagebox.showerror("错误", "投掷次数和骰子数量必须大于 0。")
            return

        counts = Counter()
        for _ in range(num_rolls):
            roll_sum = sum(random.randint(1, 6) for _ in range(num_dice))
            counts[roll_sum] += 1

        self.dice_results = {
            'counts': counts,
            'total_rolls': num_rolls,
            'num_dice': num_dice
        }
        self.update_display()

    def plot_dice_results(self):
        """Plots the results of the dice roll simulation."""
        self.ax.clear()
        results = self.dice_results
        total = results['total_rolls']
        num_dice = results['num_dice']
        counts = results['counts']

        if total == 0:
            self.ax.set_title("掷骰子模拟结果 (无数据)")
            self.canvas.draw_idle()
            return

        min_sum = num_dice
        max_sum = num_dice * 6
        possible_sums = list(range(min_sum, max_sum + 1))
        observed_freqs = [counts.get(s, 0) / total for s in possible_sums]

        bars = self.ax.bar(possible_sums, observed_freqs, color='mediumpurple')

        self.ax.set_ylabel("频率")
        self.ax.set_xlabel(f"点数和 ({num_dice}个骰子)")
        self.ax.set_title(f"掷骰子模拟结果 ({total} 次)")
        self.ax.set_xticks(possible_sums)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Add percentage labels
        for bar in bars:
            yval = bar.get_height()
            if yval > 0.001: # Don't label tiny bars
                self.ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2%}', va='bottom', ha='center', fontsize=8)

        self.canvas.draw_idle()

    def display_dice_results(self):
        """Displays explanation and results for Dice Roll."""
        self.result_text.delete(1.0, tk.END)
        description = """
掷骰子模拟：
模拟重复投掷一个或多个标准的六面骰子，并记录点数之和的分布。
- 设定总投掷次数。
- 设定每次投掷使用的骰子数量。
- 模拟将显示观测到的各种点数和的频率。
"""
        self.result_text.insert(tk.END, description)
        self.result_text.insert(tk.END, "\n" + "="*40 + "\n")

        results = self.dice_results
        total = results['total_rolls']
        if total > 0:
            num_dice = results['num_dice']
            counts = results['counts']
            min_sum = num_dice
            max_sum = num_dice * 6

            result_str = f"模拟参数:\n"
            result_str += f"  投掷次数: {total}\n"
            result_str += f"  骰子数量: {num_dice}\n"
            result_str += "观测结果 (点数和: 次数 (频率)):\n"
            for s in range(min_sum, max_sum + 1):
                count = counts.get(s, 0)
                freq = count / total
                result_str += f"  {s}: {count} ({freq:.3f})\n"
            self.result_text.insert(tk.END, result_str)
        else:
            self.result_text.insert(tk.END, "尚未运行模拟。")

    # --- Roulette Specific ---

    def create_roulette_ui(self):
        """Creates UI elements for Roulette simulation."""
        # Number of Spins
        ttk.Label(self.param_frame, text="轮盘转动次数:").pack(anchor=tk.W, pady=(10, 2))
        spins_scale = ttk.Scale(self.param_frame, from_=10, to=10000, variable=self.roulette_num_spins_var,
                               orient=tk.HORIZONTAL, command=lambda v: self.roulette_spins_label.config(text=f"{int(float(v))} 次"))
        spins_scale.pack(fill=tk.X)
        self.roulette_spins_label = ttk.Label(self.param_frame, text=f"{self.roulette_num_spins_var.get()} 次")
        self.roulette_spins_label.pack(anchor=tk.W)

        run_button = ttk.Button(self.param_frame, text="运行模拟", command=self.run_roulette_simulation)
        run_button.pack(pady=20)

    def run_roulette_simulation(self):
        """Runs the Roulette simulation (European wheel)."""
        num_spins = self.roulette_num_spins_var.get()
        if num_spins <= 0:
            messagebox.showerror("错误", "转动次数必须大于 0。")
            return

        counts = Counter()
        red_count, black_count, green_count = 0, 0, 0
        even_count, odd_count = 0, 0 # Excluding 0 for even/odd

        for _ in range(num_spins):
            result = random.choice(ROULETTE_NUMBERS)
            counts[result] += 1
            if result in ROULETTE_RED:
                red_count += 1
            elif result in ROULETTE_BLACK:
                black_count += 1
            else: # Must be 0
                green_count += 1

            if result != 0:
                if result % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1

        self.roulette_results = {
            'counts': counts,
            'red': red_count,
            'black': black_count,
            'green': green_count,
            'even': even_count,
            'odd': odd_count,
            'total_spins': num_spins
        }
        self.update_display()

    def plot_roulette_results(self):
        """Plots the results of the roulette simulation."""
        self.ax.clear()
        results = self.roulette_results
        total = results['total_spins']
        counts = results['counts']

        if total == 0:
            self.ax.set_title("轮盘赌模拟结果 (无数据)")
            self.canvas.draw_idle()
            return

        numbers = ROULETTE_NUMBERS
        observed_freqs = [counts.get(n, 0) / total for n in numbers]
        expected_freq = 1 / len(numbers)

        # Assign colors to bars
        bar_colors = []
        for n in numbers:
            if n in ROULETTE_RED: bar_colors.append('red')
            elif n in ROULETTE_BLACK: bar_colors.append('black')
            else: bar_colors.append('green')

        bars = self.ax.bar(numbers, observed_freqs, color=bar_colors, edgecolor='gray')
        self.ax.axhline(expected_freq, color='blue', linestyle='--', label=f'期望频率 ({expected_freq:.3f})')

        self.ax.set_ylabel("频率")
        self.ax.set_xlabel("号码")
        self.ax.set_title(f"轮盘赌模拟结果 ({total} 次) - 号码分布")
        self.ax.set_xticks(numbers)
        self.ax.set_xticklabels([str(n) for n in numbers], rotation=90, fontsize=8)
        self.ax.legend()
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.fig.tight_layout() # Adjust layout

        self.canvas.draw_idle()

    def display_roulette_results(self):
        """Displays explanation and results for Roulette."""
        self.result_text.delete(1.0, tk.END)
        description = """
轮盘赌模拟 (欧式轮盘: 0-36)：
模拟重复转动欧式轮盘，记录各个号码出现的频率以及颜色、奇偶等结果。
- 设定总转动次数。
- 模拟将显示观测到的各种结果的频率，图表显示每个号码的频率。
"""
        self.result_text.insert(tk.END, description)
        self.result_text.insert(tk.END, "\n" + "="*40 + "\n")

        results = self.roulette_results
        total = results['total_spins']
        if total > 0:
            exp_num_freq = 1 / len(ROULETTE_NUMBERS)
            exp_red_freq = len(ROULETTE_RED) / len(ROULETTE_NUMBERS)
            exp_black_freq = len(ROULETTE_BLACK) / len(ROULETTE_NUMBERS)
            exp_green_freq = len(ROULETTE_GREEN) / len(ROULETTE_NUMBERS)
            # Even/Odd exclude 0
            exp_even_freq = len([n for n in ROULETTE_NUMBERS if n != 0 and n % 2 == 0]) / len(ROULETTE_NUMBERS)
            exp_odd_freq = len([n for n in ROULETTE_NUMBERS if n != 0 and n % 2 != 0]) / len(ROULETTE_NUMBERS)


            result_str = f"模拟参数:\n"
            result_str += f"  转动次数: {total}\n"
            result_str += "观测结果 (颜色):\n"
            result_str += f"  红色: {results['red']} (频率: {results['red']/total:.3f}, 期望: {exp_red_freq:.3f})\n"
            result_str += f"  黑色: {results['black']} (频率: {results['black']/total:.3f}, 期望: {exp_black_freq:.3f})\n"
            result_str += f"  绿色(0): {results['green']} (频率: {results['green']/total:.3f}, 期望: {exp_green_freq:.3f})\n"
            result_str += "观测结果 (奇偶, 不含0):\n"
            result_str += f"  偶数: {results['even']} (频率: {results['even']/total:.3f}, 期望: {exp_even_freq:.3f})\n"
            result_str += f"  奇数: {results['odd']} (频率: {results['odd']/total:.3f}, 期望: {exp_odd_freq:.3f})\n"
            result_str += f"号码 0 出现次数: {results['counts'].get(0, 0)} (频率: {results['counts'].get(0, 0)/total:.3f}, 期望: {exp_num_freq:.3f})\n"

            self.result_text.insert(tk.END, result_str)
        else:
            self.result_text.insert(tk.END, "尚未运行模拟。")


    # --- General Update ---

    def update_display(self):
        """Central function to update plot and results based on game type."""
        game_type = self.current_game_type.get()

        try:
            if game_type == "蒙提霍尔问题":
                self.plot_monty_hall_results()
                self.display_monty_hall_results()
            elif game_type == "抛硬币":
                self.plot_cointoss_results()
                self.display_cointoss_results()
            elif game_type == "掷骰子":
                self.plot_dice_results()
                self.display_dice_results()
            elif game_type == "轮盘赌":
                self.plot_roulette_results()
                self.display_roulette_results()
            else:
                 messagebox.showwarning("未实现", f"游戏/谜题类型 '{game_type}' 尚未实现。")
                 self.ax.clear()
                 self.canvas.draw_idle()
                 self.result_text.delete(1.0, tk.END)

        except Exception as e:
            messagebox.showerror("更新错误", f"更新显示时发生意外错误: {e}")
            # Log the full traceback for debugging
            import traceback
            print(f"Error during update_display for {game_type}:")
            traceback.print_exc()
            # Display simplified error to user
            self.ax.clear()
            self.ax.set_title(f"{game_type} (错误)")
            self.canvas.draw_idle()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"更新显示时发生错误: {e}")


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = GamePuzzleApp(root)
    root.mainloop()

# 为了与main.py中的导入兼容
GameApp = GamePuzzleApp
