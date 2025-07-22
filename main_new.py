"""
MathVision 2.0 - 优化后的主应用
使用单窗口多页面架构，提供更流畅的交互体验
"""

import tkinter as tk
import logging
import os
from typing import Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cache/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 导入核心模块
from core.page_manager import PageManager, BasePage, NavigationBar
from core.config_manager import config_manager
from core.thread_manager import get_thread_manager, shutdown_thread_manager
from core.search_manager import search_manager, SearchWidget

# 导入主题和组件
from themes.futuristic_theme import COLORS, FONTS
from components.cards import InteractiveCard
from components.buttons import FuturisticButton

# 导入各个功能模块


class MainPage(BasePage):
    """主页面 - 显示主要功能卡片"""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        
    def initialize(self):
        """初始化主页面"""
        # 创建标题
        title_frame = tk.Frame(self, bg=COLORS["bg_light"])
        title_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0))
        
        title_label = tk.Label(
            title_frame,
            text="数学可视化教学工具",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="探索数学之美，让学习更直观",
            font=FONTS["subtitle"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # 创建搜索组件
        search_frame = tk.Frame(self, bg=COLORS["bg_light"])
        search_frame.grid(row=1, column=0, sticky="ew", pady=20)
        
        search_widget = SearchWidget(search_frame, search_manager)
        search_widget.pack()
        
        # 创建功能卡片
        self._create_feature_cards()
    
    def _create_feature_cards(self):
        """创建主要功能卡片"""
        cards_frame = tk.Frame(self, bg=COLORS["bg_light"])
        cards_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        
        # 配置网格权重
        for i in range(2):  # 2行
            cards_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):  # 2列
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # 卡片数据
        cards_data = [
            {
                "title": "高等数学",
                "description": "函数、微积分、微分方程等可视化",
                "icon": "gaoshup.ico",
                "action": lambda: self.controller.show_page("AdvancedMathPage")
            },
            {
                "title": "线性代数", 
                "description": "矩阵运算、特征值分析等",
                "icon": "xiandaip.ico",
                "action": lambda: self.controller.show_page("LinearAlgebraPage")
            },
            {
                "title": "概率统计",
                "description": "概率分布、统计推断等",
                "icon": "gailvp.ico", 
                "action": lambda: self.controller.show_page("ProbabilityPage")
            },
            {
                "title": "AI 数据分析",
                "description": "智能数据分析和可视化",
                "icon": "AIP.ico",
                "action": lambda: self.controller.show_page("AIPage")
            }
        ]
        
        # 创建卡片
        for i, card_data in enumerate(cards_data):
            row = i // 2
            col = i % 2
            
            card = InteractiveCard(
                cards_frame,
                title=card_data["title"],
                description=card_data["description"],
                icon_path=card_data["icon"],
                command=card_data["action"],
                width=300,
                height=200
            )
            card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")


class AdvancedMathPage(BasePage):
    """高等数学页面"""
    
    def initialize(self):
        # 页面标题
        title_label = tk.Label(
            self,
            text="高等数学",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 模块按钮
        modules_frame = tk.Frame(self, bg=COLORS["bg_light"])
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        modules = [
            ("函数可视化", "函数图像和性质分析", lambda: self._open_module("kehe")),
            ("微分方程", "方向场和解的可视化", lambda: self._open_module("weifen")),
            ("海塞矩阵", "多元函数的二阶导数分析", lambda: self._open_module("haisen")),
            ("方程求解", "各种方程的数值解法", lambda: self._open_module("fang"))
        ]
        
        for i, (title, desc, action) in enumerate(modules):
            button = FuturisticButton(
                modules_frame,
                text=f"{title}\n{desc}",
                command=action,
                width=400,
                height=80
            )
            button.pack(pady=10)
    
    def _open_module(self, module_name):
        """打开模块"""
        # 这里可以使用线程管理器来加载模块
        thread_manager = get_thread_manager()
        
        def load_module():
            # 模拟加载时间
            import time
            time.sleep(1)
            return f"模块 {module_name} 加载完成"
        
        def on_complete(result):
            if result.success:
                print(result.result)
                # 这里可以打开具体的模块窗口
            else:
                print(f"加载失败: {result.error}")
        
        thread_manager.submit_task(
            load_module,
            callback=on_complete,
            progress_parent=self,
            progress_message=f"正在加载 {module_name} 模块..."
        )


class LinearAlgebraPage(BasePage):
    """线性代数页面"""
    
    def initialize(self):
        title_label = tk.Label(
            self,
            text="线性代数",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 模块按钮
        modules_frame = tk.Frame(self, bg=COLORS["bg_light"])
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        modules = [
            ("矩阵运算", "基本矩阵操作和计算", self._open_matrix_operations),
            ("特征值分析", "特征值和特征向量计算", self._open_eigenvalue),
            ("矩阵变换", "几何变换可视化", self._open_matrix_transform),
            ("高斯消元", "线性方程组求解", self._open_gaussian)
        ]
        
        for title, desc, action in modules:
            button = FuturisticButton(
                modules_frame,
                text=f"{title}\n{desc}",
                command=action,
                width=400,
                height=80
            )
            button.pack(pady=10)
    
    def _open_matrix_operations(self):
        # 打开矩阵运算模块
        pass
    
    def _open_eigenvalue(self):
        # 打开特征值分析模块
        pass
    
    def _open_matrix_transform(self):
        # 打开矩阵变换模块
        pass
    
    def _open_gaussian(self):
        # 打开高斯消元模块
        pass


class ProbabilityPage(BasePage):
    """概率统计页面"""
    
    def initialize(self):
        title_label = tk.Label(
            self,
            text="概率统计",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        info_label = tk.Label(
            self,
            text="概率分布、假设检验、置信区间等统计学概念的可视化",
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"]
        )
        info_label.pack(pady=10)


class AIPage(BasePage):
    """AI数据分析页面"""
    
    def initialize(self):
        title_label = tk.Label(
            self,
            text="AI 数据分析",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 创建AI分析器的嵌入版本
        self.ai_frame = tk.Frame(self, bg=COLORS["bg_light"])
        self.ai_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 这里可以嵌入AI分析器的界面
        info_label = tk.Label(
            self.ai_frame,
            text="智能数据分析功能即将推出...",
            font=FONTS["subtitle"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"]
        )
        info_label.pack(expand=True)


class MathVisionApp:
    """主应用类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.page_manager: Optional[PageManager] = None
        self.navbar: Optional[NavigationBar] = None
        
        self._setup_window()
        self._setup_components()
        self._register_pages()
        self._register_search_items()
        self._setup_keyboard_shortcuts()
    
    def _setup_window(self):
        """设置主窗口"""
        self.root.title("数学可视化教学工具 2.0")
        
        # 从配置获取窗口大小
        width = config_manager.get_config("window.width", 1200)
        height = config_manager.get_config("window.height", 800)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 600)
        
        # 设置窗口背景
        self.root.configure(bg=COLORS["bg_light"])
        
        # 设置窗口图标
        try:
            if os.path.exists("logo.ico"):
                self.root.iconbitmap("logo.ico")
        except:
            pass
    
    def _setup_components(self):
        """设置组件"""
        # 创建页面管理器
        self.page_manager = PageManager(self.root)
        
        # 创建导航栏
        self.navbar = NavigationBar(self.root, self.page_manager)
        self.navbar.pack(side=tk.TOP, fill=tk.X)
    
    def _register_pages(self):
        """注册页面"""
        if not self.page_manager:
            return
            
        # 注册各个页面
        self.page_manager.register_page("MainPage", MainPage)
        self.page_manager.register_page("AdvancedMathPage", AdvancedMathPage)
        self.page_manager.register_page("LinearAlgebraPage", LinearAlgebraPage) 
        self.page_manager.register_page("ProbabilityPage", ProbabilityPage)
        self.page_manager.register_page("AIPage", AIPage)
        
        # 显示主页
        self.page_manager.show_page("MainPage")
    
    def _register_search_items(self):
        """注册搜索项"""
        if not self.page_manager:
            return
            
        # 注册页面到搜索
        search_manager.register_page(
            "高等数学", "函数、微积分、微分方程等", "数学模块",
            "AdvancedMathPage", self.page_manager,
            ["高等数学", "微积分", "函数", "导数", "积分"]
        )
        
        search_manager.register_page(
            "线性代数", "矩阵运算、特征值分析等", "数学模块", 
            "LinearAlgebraPage", self.page_manager,
            ["线性代数", "矩阵", "特征值", "向量"]
        )
        
        search_manager.register_page(
            "概率统计", "概率分布、统计推断等", "数学模块",
            "ProbabilityPage", self.page_manager,
            ["概率", "统计", "分布", "假设检验"]
        )
        
        search_manager.register_page(
            "AI数据分析", "智能数据分析和可视化", "工具模块",
            "AIPage", self.page_manager,
            ["AI", "人工智能", "数据分析", "机器学习"]
        )
    
    def _setup_keyboard_shortcuts(self):
        """设置键盘快捷键"""
        # 全局快捷键
        self.root.bind("<Control-h>", lambda e: self.page_manager.show_page("MainPage"))
        self.root.bind("<Control-1>", lambda e: self.page_manager.show_page("AdvancedMathPage"))
        self.root.bind("<Control-2>", lambda e: self.page_manager.show_page("LinearAlgebraPage"))
        self.root.bind("<Control-3>", lambda e: self.page_manager.show_page("ProbabilityPage"))
        self.root.bind("<Control-4>", lambda e: self.page_manager.show_page("AIPage"))
        self.root.bind("<Alt-Left>", lambda e: self.page_manager.go_back())
        self.root.bind("<Escape>", lambda e: self.page_manager.show_page("MainPage"))
    
    def run(self):
        """运行应用"""
        try:
            logging.info("MathVision 2.0 启动")
            self.root.mainloop()
        except Exception as e:
            logging.error(f"应用运行错误: {e}")
        finally:
            # 清理资源
            shutdown_thread_manager()
            logging.info("MathVision 2.0 关闭")


def main():
    """主函数"""
    try:
        app = MathVisionApp()
        app.run()
    except Exception as e:
        logging.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 