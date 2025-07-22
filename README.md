<<<<<<< HEAD
# sighted-mathematical
数学可视化项目-九章视界团队（Mathematical Visualization Project）<br>
此项目由西安电子科技大学数学与统计学院提供经费并申请省级创新训练项目<br>
项目已获得全国大学生计算机设计大赛西北赛区贰等奖以及西安电子科技大学星火杯校级一等奖与挑战杯校级三等奖<br>
目前项目已在 GitHub 开源，欢迎感兴趣的同学和开发者提出修改建议并加入我们，共同完善这一项目！<br>
main branch 中包含python版本（目前最新版）<br>
第一版matlab版本见master branch<br>
=======
# MathVision 可视化数学工具集

MathVision 是一个基于 Tkinter、Matplotlib 等库打造的交互式数学可视化平台，集成了概率论、线性代数、高等数学等多个子模块，可用于教学演示与自学探索。

## 特性一览

- 线性代数：矩阵变换、特征值可视化、高斯消元动画等
- 概率统计：概率分布动态绘制、蒙特卡洛模拟、贝叶斯直观演示
- 高等数学：方向场、微积分函数可视化、泰勒展开演示
- AI 数据分析：集成 pandas-ai，自然语言驱动的数据分析
- 现代 UI：自定义未来感主题、卡片式布局、动效过渡

## 运行环境

- Python ≥ 3.9
- 见 `requirements.txt` 依赖列表（可使用 `pip install -r requirements.txt` 安装）

> 注意：Tkinter 在大多数 Python 发行版中自带，如缺失请自行安装。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/<your-username>/MathVision.git
cd MathVision

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行主程序
python main.py
```

## 项目结构

```
.
├── core/              # 核心管理器（页面、配置、线程等）
├── components/        # UI 组件（按钮、卡片等）
├── effects/           # 动画与过渡效果
├── themes/            # 主题配色与字体
├── assets/            # 静态资源（图标等）
├── exports/           # 导出图片、缓存输出
├── <module>.py        # 各领域可视化子模块脚本
└── main.py            # 入口程序
```

## 打包发布

本项目已提供 PyInstaller 规格文件 `MathVisualization.spec`，可执行：

```bash
pyinstaller MathVisualization.spec
```

打包生成的可执行文件位于 `dist/` 目录。

## 贡献指南

欢迎提 PR 或 Issue！建议遵守以下规范：

1. 先创建分支再提交代码，命名格式 `feature/<name>` 或 `fix/<name>`。
2. 代码通过 `autoflake` 自动移除未使用内容，并保持 `black`/`isort` 风格。
3. 提交信息使用动词祈使句，如 `Add Gaussian elimination animation`。

## 许可证

MIT License © 2024 MathVision Contributors 
>>>>>>> 6c8c93f (Initial cleaned version)
