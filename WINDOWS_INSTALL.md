# 劳动法数据库 v2 - Windows安装指南

## 📋 系统要求

- **Windows 10/11** (64位)
- **Python 3.8+** (如果未安装)

---

## 🚀 安装步骤

### 步骤1：安装Python（如未安装）

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11 或更高版本
3. 安装时勾选 **"Add Python to PATH"**
4. 点击 Install Now

验证安装：
```cmd
python --version
```

### 步骤2：下载程序

1. 访问 https://github.com/Milton-dev-joey/labor-law-db-v2/releases
2. 下载：
   - `Source code (zip)` - 源代码
   - `laws_db.zip` - 数据库文件

### 步骤3：解压文件

1. 解压 `Source code (zip)` 到任意目录（如 `D:\labor-law-db-v2`）
2. 解压 `laws_db.zip`，将 `laws.db` 放入 `assets/` 文件夹

目录结构应如下：
```
labor-law-db-v2/
├── assets/
│   └── laws.db          <-- 数据库文件
├── src/
├── main.py
├── 启动.bat              <-- Windows启动脚本
└── requirements.txt
```

### 步骤4：启动程序

**方法一：双击启动（推荐）**
```
双击 "启动.bat" 文件
```

**方法二：命令行启动**
```cmd
cd D:\labor-law-db-v2
启动.bat
```

---

## 🔧 手动安装（如果启动脚本失败）

```cmd
cd D:\labor-law-db-v2

REM 创建虚拟环境
python -m venv venv

REM 激活虚拟环境
venv\Scripts\activate.bat

REM 安装依赖
pip install PyQt6 python-docx lxml

REM 启动
python main.py
```

---

## 🐛 常见问题

### 问题1：提示 "python 不是内部或外部命令"
**解决**：Python未添加到PATH，重新安装Python并勾选 "Add Python to PATH"

### 问题2：提示 "No module named 'PyQt6'"
**解决**：依赖未安装，双击"启动.bat"会自动安装

### 问题3：提示找不到数据库
**解决**：确保 `assets/laws.db` 文件存在，从Release下载并解压

### 问题4：中文显示乱码
**解决**：Windows区域设置中启用 "Beta: 使用 Unicode UTF-8 提供全球语言支持"

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| 启动.bat | Windows启动脚本 |
| main.py | 主程序入口 |
| assets/laws.db | 法律数据库（必需） |
| venv/ | Python虚拟环境（自动创建） |

---

## 🆘 技术支持

如有问题，请提交 Issue：
https://github.com/Milton-dev-joey/labor-law-db-v2/issues

---

*Windows版本说明*
