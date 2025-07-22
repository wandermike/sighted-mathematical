"""
MathVision 2.0 - 优化后的主应用
使用单窗口多页面架构，提供更流畅的交互体验
"""

import tkinter as tk


class SimpleApp:
    """简化的应用类用于演示新架构"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_page = None
        self.pages = {}
        
        self._setup_window()
        self._create_navbar()
        self._setup_pages()
    
    def _setup_window(self):
        """设置主窗口"""
        self.root.title("数学可视化教学工具 2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg="#254575")
    
    def _create_navbar(self):
        """创建导航栏"""
        navbar = tk.Frame(self.root, bg="#1A3056", height=60)
        navbar.pack(side=tk.TOP, fill=tk.X)
        navbar.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(
            navbar,
            text="数学可视化教学工具 2.0",
            font=("Arial", 18, "bold"),
            bg="#1A3056",
            fg="#FFFFFF"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 导航按钮
        nav_buttons = [
            ("主页", "main"),
            ("高等数学", "advanced"),
            ("线性代数", "linear"),
            ("概率统计", "probability")
        ]
        
        for text, page_id in nav_buttons:
            btn = tk.Button(
                navbar,
                text=text,
                font=("Arial", 12),
                bg="#72FFDE",
                fg="#0F2544",
                bd=0,
                padx=15,
                pady=5,
                cursor="hand2",
                command=lambda p=page_id: self.show_page(p)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=15)
    
    def _setup_pages(self):
        """设置页面"""
        # 主容器
        self.container = tk.Frame(self.root, bg="#254575")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # 创建页面
        self._create_main_page()
        self._create_advanced_page()
        self._create_linear_page()
        self._create_probability_page()
        
        # 显示主页
        self.show_page("main")
    
    def _create_main_page(self):
        """创建主页"""
        page = tk.Frame(self.container, bg="#254575")
        
        # 标题
        title = tk.Label(
            page,
            text="欢迎使用数学可视化教学工具",
            font=("Arial", 24, "bold"),
            bg="#254575",
            fg="#FFFFFF"
        )
        title.pack(pady=50)
        
        # 功能卡片区域
        cards_frame = tk.Frame(page, bg="#254575")
        cards_frame.pack(expand=True)
        
        # 创建功能卡片
        cards_data = [
            ("高等数学", "函数、微积分、微分方程等"),
            ("线性代数", "矩阵运算、特征值分析等"),
            ("概率统计", "概率分布、统计推断等"),
            ("AI分析", "智能数据分析和可视化")
        ]
        
        for i, (title, desc) in enumerate(cards_data):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(
                cards_frame,
                bg="#1A3056",
                relief=tk.RAISED,
                bd=2,
                width=250,
                height=150
            )
            card.grid(row=row, column=col, padx=20, pady=20)
            card.pack_propagate(False)
            
            card_title = tk.Label(
                card,
                text=title,
                font=("Arial", 16, "bold"),
                bg="#1A3056",
                fg="#72FFDE"
            )
            card_title.pack(pady=(20, 5))
            
            card_desc = tk.Label(
                card,
                text=desc,
                font=("Arial", 10),
                bg="#1A3056",
                fg="#A0A8C0",
                wraplength=200
            )
            card_desc.pack(pady=5)
        
        self.pages["main"] = page
    
    def _create_advanced_page(self):
        """创建高等数学页面"""
        page = tk.Frame(self.container, bg="#254575")
        
        title = tk.Label(
            page,
            text="高等数学模块",
            font=("Arial", 20, "bold"),
            bg="#254575",
            fg="#FFFFFF"
        )
        title.pack(pady=30)
        
        modules = [
            "函数可视化",
            "微分方程求解",
            "积分计算",
            "极限分析"
        ]
        
        for module in modules:
            btn = tk.Button(
                page,
                text=module,
                font=("Arial", 14),
                bg="#30C5FF",
                fg="#0F2544",
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2",
                width=20
            )
            btn.pack(pady=10)
        
        self.pages["advanced"] = page
    
    def _create_linear_page(self):
        """创建线性代数页面"""
        page = tk.Frame(self.container, bg="#254575")
        
        title = tk.Label(
            page,
            text="线性代数模块",
            font=("Arial", 20, "bold"),
            bg="#254575",
            fg="#FFFFFF"
        )
        title.pack(pady=30)
        
        info = tk.Label(
            page,
            text="矩阵运算、特征值分析、向量空间等功能",
            font=("Arial", 12),
            bg="#254575",
            fg="#A0A8C0"
        )
        info.pack(pady=20)
        
        self.pages["linear"] = page
    
    def _create_probability_page(self):
        """创建概率统计页面"""
        page = tk.Frame(self.container, bg="#254575")
        
        title = tk.Label(
            page,
            text="概率统计模块",
            font=("Arial", 20, "bold"),
            bg="#254575",
            fg="#FFFFFF"
        )
        title.pack(pady=30)
        
        info = tk.Label(
            page,
            text="概率分布、假设检验、置信区间等统计学概念",
            font=("Arial", 12),
            bg="#254575",
            fg="#A0A8C0"
        )
        info.pack(pady=20)
        
        self.pages["probability"] = page
    
    def show_page(self, page_id):
        """显示指定页面"""
        # 隐藏当前页面
        if self.current_page:
            self.current_page.pack_forget()
        
        # 显示新页面
        if page_id in self.pages:
            page = self.pages[page_id]
            page.pack(fill=tk.BOTH, expand=True)
            self.current_page = page
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = SimpleApp()
    app.run()


if __name__ == "__main__":
    main() 