import tkinter as tk
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
        step_time = duration // steps if steps else duration
        
        # 确保控件可见
        if isinstance(widget, (tk.Toplevel, tk.Tk)):
            current_widget = widget
        else:
            current_widget = widget.winfo_toplevel()
            widget.pack(fill=tk.BOTH, expand=True)
        
        current_widget.attributes('-alpha', 0.0)

        def _fade(i=0):
            if not current_widget.winfo_exists():
                return
            alpha = i / steps
            current_widget.attributes('-alpha', alpha)
            if i < steps:
                current_widget.after(step_time, lambda: _fade(i + 1))
        _fade()
    
    @staticmethod
    def slide_in(widget, direction="left", duration=300, target_container=None):
        """将控件以滑入效果显示
        
        参数:
            widget: 要显示的控件
            direction: 滑入方向，可以是 "left", "right", "up", "down"
            duration: 动画持续时间（毫秒）
            target_container: 目标容器，默认为widget的master
        """
        parent = target_container if target_container else widget.master
        width = parent.winfo_width() or 800
        height = parent.winfo_height() or 600

        if direction == "left":
            start_x, start_y, dx, dy = width, 0, -1, 0
        elif direction == "right":
            start_x, start_y, dx, dy = -width, 0, 1, 0
        elif direction == "up":
            start_x, start_y, dx, dy = 0, height, 0, -1
        else:  # down
            start_x, start_y, dx, dy = 0, -height, 0, 1

        widget.place(x=start_x, y=start_y, width=width, height=height)

        steps = 15
        step_time = duration // steps if steps else duration

        def _move(i=0):
            if not widget.winfo_exists():
                return
            progress = i / steps
            x = start_x + dx * width * progress
            y = start_y + dy * height * progress
            widget.place(x=x, y=y, width=width, height=height)
            if i < steps:
                widget.after(step_time, lambda: _move(i + 1))
            else:
                widget.place_forget()
                widget.pack(fill=tk.BOTH, expand=True)

        _move()
    
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
        
        overlay = tk.Frame(old_frame.master, bg=COLORS["bg_dark"])
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        steps = 10
        step_time = duration // (2 * steps) if steps else duration

        def _fade_out(i=0):
            if i > steps or not overlay.winfo_exists():
                old_frame.pack_forget()
                new_frame.pack(fill=tk.BOTH, expand=True)
                _fade_in()
                return
            alpha = 1 - (i / steps)
            overlay.configure(bg=TransitionManager._adjust_alpha(COLORS["bg_dark"], alpha))
            overlay.after(step_time, lambda: _fade_out(i + 1))

        def _fade_in(i=0):
            if i > steps or not overlay.winfo_exists():
                overlay.destroy()
                return
            alpha = i / steps
            overlay.configure(bg=TransitionManager._adjust_alpha(COLORS["bg_dark"], alpha))
            overlay.after(step_time, lambda: _fade_in(i + 1))

        _fade_out()
    
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
