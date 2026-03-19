#!/bin/bash
# 劳动法数据库 v2 - App 启动脚本

# 获取应用目录
APP_DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"

# 打开终端运行（确保 GUI 能正常显示）
osascript << EOF
tell application "Terminal"
    do script "cd '$APP_DIR'; python3 启动器.py &> /dev/null &"
    activate
end tell
EOF
