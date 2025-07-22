"""
搜索管理器 - 提供全局搜索功能
支持模糊搜索、智能排序和快速导航
"""

import tkinter as tk
from typing import List, Dict, Callable, Optional, Tuple
from difflib import SequenceMatcher
import logging

from themes.futuristic_theme import COLORS, FONTS


class SearchItem:
    """搜索项"""
    
    def __init__(self, 
                 title: str,
                 description: str,
                 category: str,
                 keywords: List[str],
                 action: Callable,
                 icon: Optional[str] = None):
        self.title = title
        self.description = description
        self.category = category
        self.keywords = keywords
        self.action = action
        self.icon = icon
        
        # 计算搜索权重用的文本
        self.search_text = f"{title} {description} {' '.join(keywords)}".lower()
    
    def get_similarity(self, query: str) -> float:
        """计算与查询的相似度"""
        query = query.lower()
        
        # 精确匹配权重最高
        if query in self.title.lower():
            return 1.0
        
        if query in self.description.lower():
            return 0.8
        
        # 关键字匹配
        for keyword in self.keywords:
            if query in keyword.lower():
                return 0.6
        
        # 模糊匹配
        similarity = SequenceMatcher(None, query, self.search_text).ratio()
        return similarity * 0.4


class SearchWidget(tk.Frame):
    """搜索组件"""
    
    def __init__(self, parent, search_manager, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)
        self.search_manager = search_manager
        
        # 搜索状态
        self.is_expanded = False
        self.search_results = []
        
        self._create_search_ui()
    
    def _create_search_ui(self):
        """创建搜索界面"""
        # 搜索入口
        search_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 搜索图标
        search_icon = tk.Label(
            search_frame,
            text="🔍",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["accent_primary"]
        )
        search_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["accent_primary"],
            bd=1,
            relief=tk.FLAT,
            width=25
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 绑定事件
        self.search_var.trace('w', self._on_search_change)
        self.search_entry.bind('<Return>', self._on_search_enter)
        self.search_entry.bind('<Escape>', self._hide_results)
        self.search_entry.bind('<Down>', self._select_first_result)
        
        # 搜索结果容器（初始隐藏）
        self.results_frame = tk.Frame(self, bg=COLORS["bg_light"], bd=1, relief=tk.SOLID)
        # 不要pack，需要时再显示
        
        # 结果列表
        self.results_listbox = tk.Listbox(
            self.results_frame,
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent_primary"],
            selectforeground=COLORS["bg_dark"],
            bd=0,
            highlightthickness=0,
            height=8
        )
        self.results_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定结果选择事件
        self.results_listbox.bind('<Double-Button-1>', self._on_result_select)
        self.results_listbox.bind('<Return>', self._on_result_select)
        self.results_listbox.bind('<Escape>', self._hide_results)
    
    def _on_search_change(self, *args):
        """搜索内容变化时的处理"""
        query = self.search_var.get().strip()
        
        if not query:
            self._hide_results()
            return
        
        # 执行搜索
        results = self.search_manager.search(query)
        self._show_results(results)
    
    def _show_results(self, results: List[Tuple[SearchItem, float]]):
        """显示搜索结果"""
        self.search_results = results
        
        # 清空结果列表
        self.results_listbox.delete(0, tk.END)
        
        if not results:
            self.results_listbox.insert(0, "未找到匹配结果")
            self.results_listbox.config(state=tk.DISABLED)
        else:
            self.results_listbox.config(state=tk.NORMAL)
            for item, score in results[:10]:  # 最多显示10个结果
                display_text = f"{item.title} - {item.description}"
                self.results_listbox.insert(tk.END, display_text)
        
        # 显示结果框架
        if not self.is_expanded:
            self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.is_expanded = True
    
    def _hide_results(self, event=None):
        """隐藏搜索结果"""
        if self.is_expanded:
            self.results_frame.pack_forget()
            self.is_expanded = False
    
    def _on_search_enter(self, event):
        """回车键处理"""
        if self.search_results:
            self._execute_first_result()
    
    def _select_first_result(self, event):
        """选择第一个结果"""
        if self.search_results:
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(0)
            self.results_listbox.focus_set()
    
    def _on_result_select(self, event):
        """选择搜索结果"""
        selection = self.results_listbox.curselection()
        if selection and self.search_results:
            index = selection[0]
            if index < len(self.search_results):
                item, score = self.search_results[index]
                self._execute_result(item)
    
    def _execute_first_result(self):
        """执行第一个搜索结果"""
        if self.search_results:
            item, score = self.search_results[0]
            self._execute_result(item)
    
    def _execute_result(self, item: SearchItem):
        """执行搜索结果"""
        try:
            # 清空搜索框
            self.search_var.set("")
            self._hide_results()
            
            # 执行动作
            item.action()
            
        except Exception as e:
            logging.error(f"执行搜索结果失败: {e}")


class SearchManager:
    """搜索管理器"""
    
    def __init__(self):
        self.items: List[SearchItem] = []
        self.categories: Dict[str, List[SearchItem]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_item(self, item: SearchItem):
        """注册搜索项"""
        self.items.append(item)
        
        # 按类别组织
        if item.category not in self.categories:
            self.categories[item.category] = []
        self.categories[item.category].append(item)
        
        self.logger.info(f"搜索项已注册: {item.title}")
    
    def register_page(self, 
                     title: str,
                     description: str,
                     category: str,
                     page_name: str,
                     page_manager,
                     keywords: Optional[List[str]] = None):
        """注册页面到搜索"""
        if keywords is None:
            keywords = [title.lower()]
        
        action = lambda: page_manager.show_page(page_name)
        
        item = SearchItem(
            title=title,
            description=description,
            category=category,
            keywords=keywords,
            action=action
        )
        
        self.register_item(item)
    
    def register_function(self,
                         title: str,
                         description: str,
                         category: str,
                         function: Callable,
                         keywords: Optional[List[str]] = None):
        """注册功能函数到搜索"""
        if keywords is None:
            keywords = [title.lower()]
        
        item = SearchItem(
            title=title,
            description=description,
            category=category,
            keywords=keywords,
            action=function
        )
        
        self.register_item(item)
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[SearchItem, float]]:
        """执行搜索"""
        if not query.strip():
            return []
        
        results = []
        
        for item in self.items:
            similarity = item.get_similarity(query)
            if similarity > 0.1:  # 最低相似度阈值
                results.append((item, similarity))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self.categories.keys())
    
    def get_items_by_category(self, category: str) -> List[SearchItem]:
        """获取指定类别的搜索项"""
        return self.categories.get(category, [])


# 全局搜索管理器实例
search_manager = SearchManager() 