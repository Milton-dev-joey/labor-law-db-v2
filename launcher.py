#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
劳动法数据库 v2 - 启动器（macOS 兼容版）
"""
import os
import sys
import subprocess
import time

def setup_environment():
    """设置环境"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    venv_python = os.path.join(app_dir, 'venv', 'bin', 'python')
    
    # 检查虚拟环境
    if not os.path.exists(venv_python):
        print("首次启动，准备环境...")
        print("(这可能需要 1-2 分钟)")
        
        # 创建虚拟环境
        result = subprocess.run(
            [sys.executable, '-m', 'venv', 'venv'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"创建虚拟环境失败: {result.stderr}")
            return None
        
        # 安装依赖
        pip = os.path.join(app_dir, 'venv', 'bin', 'pip')
        print("安装依赖...")
        result = subprocess.run(
            [pip, 'install', 'PyQt6', 'python-docx'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"安装依赖失败: {result.stderr}")
            return None
        
        print("✓ 环境准备完成")
    
    return venv_python

def launch_app(venv_python):
    """启动应用"""
    print("启动劳动法数据库...")
    print("(窗口将在几秒后显示)")
    
    # 使用 Popen 启动，不阻塞
    process = subprocess.Popen(
        [venv_python, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待几秒检查是否成功启动
    time.sleep(3)
    
    if process.poll() is None:
        print("✓ 应用已启动")
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"✗ 启动失败")
        print(f"错误: {stderr or stdout}")
        return False

def main():
    try:
        venv_python = setup_environment()
        if venv_python is None:
            input("\n按回车键退出...")
            return 1
        
        if not launch_app(venv_python):
            input("\n按回车键退出...")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        return 1

if __name__ == '__main__':
    sys.exit(main())
