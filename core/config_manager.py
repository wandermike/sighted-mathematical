"""
配置管理器 - 统一管理主题、设计令牌和应用设置
支持动态主题切换和用户自定义配置
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging


@dataclass
class DesignTokens:
    """设计令牌 - 定义应用的视觉设计规范"""
    
    # 颜色系统
    colors: Dict[str, str]
    
    # 字体系统
    fonts: Dict[str, tuple]
    
    # 间距系统
    spacing: Dict[str, int]
    
    # 圆角系统
    radii: Dict[str, int]
    
    # 阴影系统
    shadows: Dict[str, str]
    
    # 动画时间
    animation: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignTokens':
        """从字典创建实例"""
        return cls(**data)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "app_config.json")
        self.themes_dir = os.path.join(config_dir, "themes")
        
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(self.themes_dir, exist_ok=True)
        
        # 应用配置
        self.app_config = {}
        self.current_theme = "futuristic"
        self.design_tokens: Optional[DesignTokens] = None
        
        # 日志
        self.logger = logging.getLogger(__name__)
        
        # 加载配置
        self._load_config()
        self._load_theme()
    
    def _load_config(self):
        """加载应用配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.app_config = json.load(f)
            else:
                # 创建默认配置
                self.app_config = self._get_default_config()
                self._save_config()
                
            self.current_theme = self.app_config.get("theme", "futuristic")
            self.logger.info("应用配置加载成功")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.app_config = self._get_default_config()
    
    def _save_config(self):
        """保存应用配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_config, f, indent=2, ensure_ascii=False)
            self.logger.info("应用配置保存成功")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "theme": "futuristic",
            "language": "zh_CN",
            "window": {
                "width": 1200,
                "height": 800,
                "remember_size": True,
                "remember_position": True
            },
            "performance": {
                "enable_animations": True,
                "animation_speed": "normal",
                "max_threads": 4,
                "cache_enabled": True
            },
            "accessibility": {
                "high_contrast": False,
                "large_fonts": False,
                "keyboard_navigation": True
            },
            "debugging": {
                "log_level": "INFO",
                "show_fps": False,
                "show_memory_usage": False
            }
        }
    
    def _load_theme(self):
        """加载主题"""
        theme_file = os.path.join(self.themes_dir, f"{self.current_theme}.json")
        
        try:
            if os.path.exists(theme_file):
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                self.design_tokens = DesignTokens.from_dict(theme_data)
            else:
                # 创建默认主题
                self.design_tokens = self._get_default_theme()
                self._save_theme()
                
            self.logger.info(f"主题加载成功: {self.current_theme}")
            
        except Exception as e:
            self.logger.error(f"加载主题失败: {e}")
            self.design_tokens = self._get_default_theme()
    
    def _save_theme(self):
        """保存当前主题"""
        if not self.design_tokens:
            return
            
        theme_file = os.path.join(self.themes_dir, f"{self.current_theme}.json")
        
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(self.design_tokens.to_dict(), f, indent=2, ensure_ascii=False)
            self.logger.info(f"主题保存成功: {self.current_theme}")
        except Exception as e:
            self.logger.error(f"保存主题失败: {e}")
    
    def _get_default_theme(self) -> DesignTokens:
        """获取默认主题（从现有的futuristic_theme.py导入）"""
        from themes.futuristic_theme import COLORS, FONTS, SPACING, RADII, SHADOWS, ANIMATION
        
        return DesignTokens(
            colors=COLORS,
            fonts={k: v for k, v in FONTS.items()},  # 转换为普通字典
            spacing=SPACING,
            radii=RADII,
            shadows=SHADOWS,
            animation=ANIMATION
        )
    
    def switch_theme(self, theme_name: str) -> bool:
        """切换主题"""
        old_theme = self.current_theme
        self.current_theme = theme_name
        
        try:
            self._load_theme()
            self.app_config["theme"] = theme_name
            self._save_config()
            self.logger.info(f"主题切换成功: {old_theme} -> {theme_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"主题切换失败: {e}")
            self.current_theme = old_theme
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.app_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.app_config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        self._save_config()
    
    def get_colors(self) -> Dict[str, str]:
        """获取当前主题的颜色"""
        return self.design_tokens.colors if self.design_tokens else {}
    
    def get_fonts(self) -> Dict[str, tuple]:
        """获取当前主题的字体"""
        return self.design_tokens.fonts if self.design_tokens else {}
    
    def get_spacing(self) -> Dict[str, int]:
        """获取当前主题的间距"""
        return self.design_tokens.spacing if self.design_tokens else {}
    
    def apply_accessibility_settings(self, widget):
        """应用无障碍设置到组件"""
        if self.get_config("accessibility.high_contrast", False):
            # 应用高对比度
            pass
            
        if self.get_config("accessibility.large_fonts", False):
            # 应用大字体
            pass
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """获取性能设置"""
        return {
            "enable_animations": self.get_config("performance.enable_animations", True),
            "animation_speed": self.get_config("performance.animation_speed", "normal"),
            "max_threads": self.get_config("performance.max_threads", 4),
            "cache_enabled": self.get_config("performance.cache_enabled", True)
        }


# 全局配置管理器实例
config_manager = ConfigManager() 