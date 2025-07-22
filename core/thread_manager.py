"""
线程管理器 - 处理长时间运行的计算任务
提供线程池、任务队列和进度反馈功能，确保UI不会卡顿
"""

import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict
import logging
import tkinter as tk
from functools import wraps

from themes.futuristic_theme import COLORS, FONTS


class TaskResult:
    """任务执行结果"""
    
    def __init__(self, task_id: str, success: bool, result: Any = None, error: Optional[Exception] = None):
        self.task_id = task_id
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = time.time()


class ProgressOverlay:
    """进度遮罩层 - 显示计算进度"""
    
    def __init__(self, parent: tk.Widget, message: str = "正在计算..."):
        self.parent = parent
        self.message = message
        self.overlay = None
        self.progress_bar = None
        self.message_label = None
        self.is_visible = False
        
    def show(self):
        """显示进度遮罩"""
        if self.is_visible:
            return
            
        # 创建半透明遮罩
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("")
        self.overlay.attributes('-alpha', 0.9)
        self.overlay.configure(bg=COLORS["overlay"])
        
        # 移除窗口装饰
        self.overlay.overrideredirect(True)
        
        # 设置遮罩位置和大小
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        self.overlay.geometry(f"{parent_width}x{parent_height}+{parent_x}+{parent_y}")
        
        # 创建内容框架
        content_frame = tk.Frame(
            self.overlay,
            bg=COLORS["bg_medium"],
            bd=2,
            relief=tk.RAISED
        )
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 消息标签
        self.message_label = tk.Label(
            content_frame,
            text=self.message,
            font=FONTS["subtitle"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            padx=20,
            pady=10
        )
        self.message_label.pack(pady=(20, 10))
        
        # 进度条（不确定进度）
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=COLORS["accent_primary"],
            troughcolor=COLORS["bg_light"],
            borderwidth=0,
            lightcolor=COLORS["accent_primary"],
            darkcolor=COLORS["accent_primary"]
        )
        
        self.progress_bar = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            style="Custom.Horizontal.TProgressbar",
            length=200
        )
        self.progress_bar.pack(pady=(0, 20), padx=20)
        self.progress_bar.start(10)  # 动画速度
        
        # 设置为模态
        self.overlay.transient(self.parent.winfo_toplevel())
        self.overlay.grab_set()
        
        self.is_visible = True
        if self.overlay:
            self.overlay.update()
    
    def update_message(self, message: str):
        """更新进度消息"""
        if self.message_label:
            self.message_label.config(text=message)
            self.overlay.update()
    
    def hide(self):
        """隐藏进度遮罩"""
        if not self.is_visible:
            return
            
        if self.progress_bar:
            self.progress_bar.stop()
            
        if self.overlay:
            self.overlay.grab_release()
            self.overlay.destroy()
            
        self.is_visible = False


class ThreadManager:
    """线程管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.result_queue = queue.Queue()
        self.active_tasks: Dict[str, Future] = {}
        self.task_counter = 0
        
        # 日志
        self.logger = logging.getLogger(__name__)
        
        # 启动结果处理线程
        self.result_thread = threading.Thread(target=self._process_results, daemon=True)
        self.result_thread.start()
        
        self.logger.info(f"线程管理器初始化完成，最大工作线程数: {max_workers}")
    
    def submit_task(self, 
                   func: Callable,
                   callback: Optional[Callable[[TaskResult], None]] = None,
                   progress_parent: Optional[tk.Widget] = None,
                   progress_message: str = "正在计算...",
                   *args, **kwargs) -> str:
        """提交计算任务"""
        
        # 生成任务ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        # 显示进度遮罩
        overlay = None
        if progress_parent:
            overlay = ProgressOverlay(progress_parent, progress_message)
            overlay.show()
        
        # 包装任务函数
        def wrapped_task():
            try:
                result = func(*args, **kwargs)
                task_result = TaskResult(task_id, True, result)
            except Exception as e:
                self.logger.error(f"任务执行失败 {task_id}: {e}")
                task_result = TaskResult(task_id, False, None, e)
            
            # 将结果放入队列
            self.result_queue.put((task_result, callback, overlay))
            return task_result
        
        # 提交任务
        future = self.executor.submit(wrapped_task)
        self.active_tasks[task_id] = future
        
        self.logger.info(f"任务已提交: {task_id}")
        return task_id
    
    def _process_results(self):
        """处理任务结果（在主线程中执行回调）"""
        while True:
            try:
                task_result, callback, overlay = self.result_queue.get(timeout=1)
                
                # 移除活动任务
                if task_result.task_id in self.active_tasks:
                    del self.active_tasks[task_result.task_id]
                
                # 隐藏进度遮罩
                if overlay:
                    overlay.hide()
                
                # 执行回调
                if callback:
                    try:
                        callback(task_result)
                    except Exception as e:
                        self.logger.error(f"回调执行失败: {e}")
                
                self.logger.info(f"任务完成: {task_result.task_id}")
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"结果处理失败: {e}")
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            future = self.active_tasks[task_id]
            success = future.cancel()
            if success:
                del self.active_tasks[task_id]
                self.logger.info(f"任务已取消: {task_id}")
            return success
        return False
    
    def get_active_task_count(self) -> int:
        """获取活动任务数量"""
        return len(self.active_tasks)
    
    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self.executor.shutdown(wait=wait)
        self.logger.info("线程管理器已关闭")


# 装饰器：自动异步执行
def async_task(progress_message: str = "处理中...", 
               show_progress: bool = True):
    """装饰器：将函数标记为异步执行"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从kwargs中提取特殊参数
            callback = kwargs.pop('_callback', None)
            progress_parent = kwargs.pop('_progress_parent', None) if show_progress else None
            
            # 获取全局线程管理器
            thread_manager = get_thread_manager()
            
            return thread_manager.submit_task(
                func, callback, progress_parent, progress_message, *args, **kwargs
            )
        
        return wrapper
    return decorator


# 全局线程管理器实例
_thread_manager: Optional[ThreadManager] = None

def get_thread_manager() -> ThreadManager:
    """获取全局线程管理器实例"""
    global _thread_manager
    if _thread_manager is None:
        from core.config_manager import config_manager
        max_workers = config_manager.get_config("performance.max_threads", 4)
        _thread_manager = ThreadManager(max_workers)
    return _thread_manager

def shutdown_thread_manager():
    """关闭全局线程管理器"""
    global _thread_manager
    if _thread_manager:
        _thread_manager.shutdown()
        _thread_manager = None 