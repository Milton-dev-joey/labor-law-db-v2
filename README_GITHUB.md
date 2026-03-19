# 劳动法数据库 v2

> 专为法律工作者设计的劳动法查询与案件管理工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 简介

劳动法数据库 v2 是一款基于 PyQt6 开发的桌面应用，包含：

- 📚 **415部劳动法相关法律** - 全文检索、分类浏览
- 📁 **案例管理** - 现实案件与参考案例管理
- ⚖️ **案件工作台** - 专业案件管理与文书生成
  - 案件信息录入（当事主体、法院、日期、律师等）
  - 案件卡片列表（紧急度标记、筛选搜索）
  - 文书自动生成（授权委托书、法定代表人证明、答辩状）
  - 常用信息库（公司信息、代理人信息快速调用）

## 🖥️ 系统要求

- **macOS 10.14+** (M1/M2 Intel 均支持)
- **Python 3.8+**

## 🚀 安装与启动

### 方式一：源代码运行（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/labor-law-db-v2.git
cd labor-law-db-v2

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python main.py
```

### 方式二：双击启动（简单）

双击 `启动劳动法数据库v2.command` 文件即可启动

## 📸 功能截图

（待添加）

## 📁 项目结构

```
labor-law-db-v2/
├── main.py                      # 主入口
├── requirements.txt             # 依赖列表
├── src/
│   ├── database.py              # 数据库操作
│   ├── main_window.py           # 主窗口
│   ├── case_workbench/          # 案件工作台模块
│   │   ├── models.py            # 数据模型
│   │   ├── common_info.py       # 常用信息库
│   │   ├── document_generator.py # 文书生成
│   │   ├── workbench_widget.py  # 工作台界面
│   │   └── template_manager.py  # 模板管理
│   └── widgets/                 # UI组件
├── assets/
│   └── laws.db                  # 法律数据库
└── venv/                        # 虚拟环境
```

## 🎯 核心功能

### 1. 法律法规检索
- 全文 FTS5 索引搜索
- 按位阶分类浏览（宪法/法律/行政法规/地方法规）
- 条文高亮显示

### 2. 案件工作台
- 案件信息完整录入
- 举证期限/开庭日期提醒
- 紧急案件红色标记
- 案由自动匹配专题

### 3. 文书生成
- **授权委托书** - 自动生成，支持律师信息调用
- **法定代表人身份证明书** - 公司信息自动填充
- **答辩状** - 段落组合选择，模板自定义
- 一键导出 Word (.docx)

### 4. 常用信息库
- 录入常用公司信息（名称、信用代码、住所、法定代表人）
- 录入代理人信息（姓名、性别、身份证号、电话、执业证号）
- 生成文书时快速调用

## 📝 使用说明

### 案件工作台使用流程

1. **进入案件工作台**
   - 点击工具栏 "⚖️ 案件工作台"

2. **录入常用信息**（首次使用）
   - 点击 "📋 常用信息"
   - 选择 "录入常用公司信息" 或 "录入代理人信息"
   - 填写信息并保存

3. **新建案件**
   - 点击 "➕ 新建案件"
   - 填写案件信息
   - 保存

4. **生成文书**
   - 右键案件 → "生成文书"
   - 选择文书类型
   - 配置信息 → 预览 → 导出Word

## 🛠️ 开发相关

### 技术栈
- **GUI:** PyQt6
- **数据库:** SQLite3 + FTS5全文索引
- **文档生成:** python-docx

### 开发文档
详见 `memory/labor-law-db/` 目录：
- [PROJECT_SUMMARY.md](memory/labor-law-db/PROJECT_SUMMARY.md) - 项目总览
- [DEVELOPER_GUIDE.md](memory/labor-law-db/DEVELOPER_GUIDE.md) - 开发指南
- [ARCHITECTURE.md](memory/labor-law-db/ARCHITECTURE.md) - 技术架构

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**Made with ❤️ for Legal Professionals**
