#!/bin/bash
# 启动劳动法数据库应用

cd "$(dirname "$0")"
source venv/bin/activate
python main.py
