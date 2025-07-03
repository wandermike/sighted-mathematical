import tkinter as tk
import time
from themes.futuristic_theme import COLORS

class TransitionManager:
    """管理界面转换和元素过渡的类"""
    
    @staticmethod
    def fade_in(widget, duration=300, delay=0):
        """将控件以淡入效果显示
        
        参数:
            widget: 要淡入的控件
            duration: 动画持续时间(毫秒)
            delay: 开始前的延迟时间(毫秒)
        """
        if not hasattr(widget.winfo_toplevel(), 'attributes'):
            # 对于不支持透明度的控件，直接显示
            widget.pack(fill=tk.BOTH, expand=True)
            return
            
        # 设置初始透明度为0
        widget.winfo_toplevel().attributes('-alpha', 0.0)
        
        # 延迟执行
        if delay > 0:
            widget.after(delay, lambda: TransitionManager._perform_fade_in(widget, duration))
        else:
            TransitionManager._perform_fade_in(widget, duration)
    
    @staticmethod
    def _perform_fade_in(widget, duration):
        """执行实际的淡入动画"""
        steps = 15
        step_time = duration // steps
        
        # 确保控件可见
        if isinstance(widget, tk.Toplevel) or isinstance(widget, tk.Tk):
            current_widget = widget
        else:
            current_widget = widget.winfo_toplevel()
            widget.pack(fill=tk.BOTH, expand=True)
        
        # 执行动画
        for i in range(steps + 1):
            alpha = i / steps
            try:
                current_widget.attributes('-alpha', alpha)
                current_widget.update()
                time.sleep(step_time / 1000)
            except Exception:
                # 忽略可能的错误
                pass
    
    @staticmethod
    def slide_in(widget, direction="left", duration=300, target_container=None):
        """将控件以滑入效果显示
        
        参数:
            widget: 要显示的控件
            direction: 滑入方向，可以是 "left", "right", "up", "down"
            duration: 动画持续时间（毫秒）
            target_container: 目标容器，默认为widget的master
        """
        # 获取父容器
        parent = target_container if target_container else widget.master
        width = parent.winfo_width() or 800
        height = parent.winfo_height() or 600
        
        # 设置初始位置
        if direction == "left":
            widget.place(x=width, y=0, width=width, height=height)
        elif direction == "right":
            widget.place(x=-width, y=0, width=width, height=height)
        elif direction == "up":
            widget.place(x=0, y=height, width=width, height=height)
        elif direction == "down":
            widget.place(x=0, y=-height, width=width, height=height)
        
        # 开始动画
        steps = 15
        step_time = duration // steps
        
        for i in range(steps + 1):
            progress = i / steps
            
            if direction == "left":
                x = width * (1 - progress)
                y = 0
            elif direction == "right":
                x = -width * (1 - progress)
                y = 0
            elif direction == "up":
                x = 0
                y = height * (1 - progress)
            elif direction == "down":
                x = 0
                y = -height * (1 - progress)
            
            widget.place(x=x, y=y, width=width, height=height)
            parent.update()
            time.sleep(step_time / 1000)
        
        # 完成动画后使用pack替代place
        widget.place_forget()
        widget.pack(fill=tk.BOTH, expand=True)
    
    @staticmethod
    def fade_between_frames(old_frame, new_frame, duration=300):
        """在两个框架之间平滑切换
        
        参数:
            old_frame: 当前显示的框架
            new_frame: 要切换到的新框架
            duration: 动画持续时间（毫秒）
        """
        # 确保新框架已创建但未显示
        new_frame.pack_forget()
        
        # 创建叠加层
        overlay = tk.Frame(old_frame.master, bg=COLORS["bg_dark"])
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 淡出当前框架
        steps = 10
        step_time = duration // (2 * steps)  # 一半时间用于淡出，一半用于淡入
        
        # 淡出动画
        for i in range(steps + 1):
            alpha = 1 - (i / steps)
            overlay.configure(bg=TransitionManager._adjust_alpha(COLORS["bg_dark"], alpha))
            old_frame.master.update()
            time.sleep(step_time / 1000)
        
        # 切换框架
        old_frame.pack_forget()
        new_frame.pack(fill=tk.BOTH, expand=True)
        
        # 淡入动画
        for i in range(steps + 1):
            alpha = i / steps
            overlay.configure(bg=TransitionManager._adjust_alpha(COLORS["bg_dark"], alpha))
            new_frame.master.update()
            time.sleep(step_time / 1000)
        
        # 移除叠加层
        overlay.destroy()
    
    @staticmethod
    def _adjust_alpha(color, alpha):
        """调整颜色的透明度"""
        # 对于tkinter，我们不能真正改变颜色的alpha通道
        # 这里我们通过混合背景色和前景色来模拟透明效果
        bg_color = "#000000"  # 假设背景是黑色
        
        # 解析颜色
        r1, g1, b1 = TransitionManager._hex_to_rgb(color)
        r2, g2, b2 = TransitionManager._hex_to_rgb(bg_color)
        
        # 混合颜色
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))
        
        # 返回新颜色
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """将HEX颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
