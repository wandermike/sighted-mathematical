import tkinter as tk
import math
import random
from themes.futuristic_theme import COLORS

def fade_in(widget, duration=500):
    """将控件以淡入效果显示（非阻塞）"""
    if not hasattr(widget.winfo_toplevel(), 'attributes'):
        # 不支持透明度时直接显示
        widget.pack(fill=tk.BOTH, expand=True)
        return

    # 保存原始透明度
    try:
        original_alpha = widget.winfo_toplevel().attributes('-alpha')
    except Exception:
        original_alpha = 1.0

    steps = 20
    step_time = duration // steps

    # 初始化透明度
    widget.winfo_toplevel().attributes('-alpha', 0.0)
    widget.pack(fill=tk.BOTH, expand=True)

    def _step(i=0):
        if not widget.winfo_exists():
            return
        alpha = (i / steps) * original_alpha
        widget.winfo_toplevel().attributes('-alpha', alpha)
        if i < steps:
            widget.after(step_time, lambda: _step(i + 1))

    _step()


def slide_in(widget, direction="left", duration=300):
    """将控件以滑入效果显示（非阻塞）"""
    parent = widget.master
    width = parent.winfo_width() or 800
    height = parent.winfo_height() or 600

    # 根据方向设置初始偏移
    if direction == "left":
        start_x, start_y = width, 0
        dx, dy = -1, 0
    elif direction == "right":
        start_x, start_y = -width, 0
        dx, dy = 1, 0
    elif direction == "up":
        start_x, start_y = 0, height
        dx, dy = 0, -1
    else:  # down
        start_x, start_y = 0, -height
        dx, dy = 0, 1

    widget.place(x=start_x, y=start_y, width=width, height=height)

    steps = 20
    step_time = duration // steps

    def _step(i=0):
        if not widget.winfo_exists():
            return
        progress = i / steps
        x = start_x + dx * width * progress
        y = start_y + dy * height * progress
        widget.place(x=x, y=y, width=width, height=height)
        if i < steps:
            widget.after(step_time, lambda: _step(i + 1))
        else:
            widget.place_forget()
            widget.pack(fill=tk.BOTH, expand=True)

    _step()

class ParticleSystem:
    """粒子系统，用于创建背景动画效果"""
    def __init__(self, canvas, num_particles=30, particle_size=3, 
                 colors=[COLORS["accent_primary"], COLORS["accent_secondary"]]):
        self.canvas = canvas
        self.particles = []
        self.colors = colors
        
        # 创建粒子
        for _ in range(num_particles):
            x = random.randint(0, self.canvas.winfo_width() or 800)
            y = random.randint(0, self.canvas.winfo_height() or 600)
            size = random.randint(1, particle_size)
            speed = random.uniform(0.2, 1.0)
            angle = random.uniform(0, 2 * math.pi)
            color = random.choice(colors)
            
            particle = {
                "id": self.canvas.create_oval(x, y, x+size, y+size, 
                                            fill=color, outline=""),
                "x": x,
                "y": y,
                "size": size,
                "speed": speed,
                "angle": angle,
                "color": color
            }
            self.particles.append(particle)
    
    def update(self):
        """更新粒子位置和状态"""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 600
        
        for particle in self.particles:
            # 计算新位置
            dx = math.cos(particle["angle"]) * particle["speed"]
            dy = math.sin(particle["angle"]) * particle["speed"]
            
            particle["x"] += dx
            particle["y"] += dy
            
            # 检查边界
            if (particle["x"] < -particle["size"] or 
                particle["x"] > width + particle["size"] or
                particle["y"] < -particle["size"] or 
                particle["y"] > height + particle["size"]):
                # 重置位置
                if random.choice([True, False]):
                    # 从左右边界重新进入
                    particle["x"] = -particle["size"] if dx > 0 else width + particle["size"]
                    particle["y"] = random.randint(0, height)
                else:
                    # 从上下边界重新进入
                    particle["x"] = random.randint(0, width)
                    particle["y"] = -particle["size"] if dy > 0 else height + particle["size"]
                
                # 更新速度和角度
                particle["speed"] = random.uniform(0.2, 1.0)
                particle["angle"] = random.uniform(0, 2 * math.pi)
            
            # 更新Canvas上的粒子
            x, y = particle["x"], particle["y"]
            size = particle["size"]
            self.canvas.coords(particle["id"], x, y, x+size, y+size)
        
        # 30毫秒后再次调用
        self.canvas.after(30, self.update)
