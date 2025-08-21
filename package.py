#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
用于将 TodoList 项目打包成单个 exe 文件
"""

import os
import sys
import subprocess
import shutil

from config import PYINSTALLER_PATH, ROOT_PATH


def clean_previous_build():
    """清理之前的构建文件"""
    print("正在清理之前的构建文件...")
    dirs_to_remove = ['build', 'dist']
    files_to_remove = []

    # 删除目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除目录: {dir_name}")

    # 删除文件
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"已删除文件: {file_name}")


def check_resources():
    """检查必要的资源文件是否存在"""
    required_files = [
        'src/data/tasks.json',
        'src/img/todo.ico',
        'src/img/todo.svg',
        'main.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("错误: 以下文件缺失:")
        for file in missing_files:
            print(f"  - {file}")
        return False

    print("所有资源文件检查通过")
    return True


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("开始构建可执行文件...")

    # PyInstaller 命令参数
    cmd = [
        str(PYINSTALLER_PATH),
        f'{ROOT_PATH}{os.sep}main.spec'
    ]

    try:
        print("正在打包: ", end="")

        # 执行打包命令
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时更新进度直到完成
        import time
        import threading

        # 标记打包过程是否完成
        building_finished = False

        def update_progress():
            dots = 0
            while not building_finished:
                time.sleep(0.5)
                if not building_finished:
                    print(".", end="", flush=True)
                    dots += 1
                    if dots % 20 == 0:  # 每20个点换行
                        print()
                        print("正在打包: ", end="")

        # 启动进度更新线程
        progress_thread = threading.Thread(target=update_progress)
        progress_thread.daemon = True
        progress_thread.start()

        # 等待进程完成
        stdout, stderr = process.communicate()

        # 标记打包完成
        building_finished = True

        # 等待进度线程结束
        progress_thread.join(timeout=1)

        # 清理进度显示
        print()

        if process.returncode == 0:
            print("打包成功完成!")
            print(f"可执行文件位置: {os.path.join('dist', 'Fluent Todo List.exe')}")
            return True
        else:
            print("打包失败!")
            print(f"错误信息: {stderr}")
            return False

    except FileNotFoundError:
        print("错误: 未找到 pyinstaller 命令，请确保已安装 PyInstaller")
        print("可以使用以下命令安装: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"打包过程中发生错误: {e}")
        return False



def create_tasks_json():
    """创建默认的 tasks.json 文件（如果不存在）"""
    tasks_file = 'src/data/tasks.json'

    if not os.path.exists(tasks_file):
        print("创建默认 tasks.json 文件...")
        os.makedirs(os.path.dirname(tasks_file), exist_ok=True)

        default_content = '[]'  # 空的 JSON 数组
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(default_content)
        print("tasks.json 创建完成")


def main():
    """主函数"""
    print("TodoList 打包工具")
    print("=" * 30)

    # 确保在正确的目录中
    if not os.path.exists('main.py'):
        print("错误: 未找到 main.py 文件，请在项目根目录运行此脚本")
        return False

    # 创建必要的目录结构
    os.makedirs('src/data', exist_ok=True)
    os.makedirs('src/img', exist_ok=True)

    # 创建默认数据文件
    create_tasks_json()

    # 检查资源文件
    if not check_resources():
        return False

    # 清理之前的构建
    clean_previous_build()

    # 执行打包
    if build_executable():
        print("\n打包完成!")
        print(f"可执行文件位置: {os.path.abspath(os.path.join('dist', 'Fluent Todo List.exe'))}")
        return True
    else:
        print("\n打包失败!")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
