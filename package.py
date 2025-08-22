#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller packaging script
Used to package the TodoList project into a single exe file
"""

import os
import sys
import subprocess
import shutil

from config import PYINSTALLER_PATH, ROOT_PATH


def clean_previous_build():
    """Clean previous build files"""
    print("Cleaning previous build files...")
    dirs_to_remove = ['build', 'dist']
    files_to_remove = []

    # Remove directories
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")

    # Remove files
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed file: {file_name}")


def check_resources():
    """Check if required resource files exist"""
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
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return False

    print("All required resources are available")
    return True


def build_executable():
    """Build the executable using PyInstaller"""
    print("Starting build process...")

    # PyInstaller command
    cmd = [
        str(PYINSTALLER_PATH),
        f'{ROOT_PATH}{os.sep}main.spec'
    ]

    try:
        print("Packaging: ", end="")

        # Run packaging command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        import time
        import threading

        building_finished = False

        def update_progress():
            dots = 0
            while not building_finished:
                time.sleep(0.5)
                if not building_finished:
                    print(".", end="", flush=True)
                    dots += 1
                    if dots % 20 == 0:
                        print()
                        print("Packaging: ", end="")

        progress_thread = threading.Thread(target=update_progress)
        progress_thread.daemon = True
        progress_thread.start()

        stdout, stderr = process.communicate()

        building_finished = True
        progress_thread.join(timeout=1)

        print()

        if process.returncode == 0:
            print("Build completed successfully!")
            print(f"Executable location: {os.path.join('dist', 'Fluent Todo List.exe')}")
            return True
        else:
            print("Build failed!")
            print(f"Error message: {stderr}")
            return False

    except FileNotFoundError:
        print("Error: PyInstaller command not found. Please make sure PyInstaller is installed.")
        print("You can install it with: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"Unexpected error during build: {e}")
        return False


def create_tasks_json():
    """Create a default tasks.json file if not exists"""
    tasks_file = 'src/data/tasks.json'

    if not os.path.exists(tasks_file):
        print("Creating default tasks.json file...")
        os.makedirs(os.path.dirname(tasks_file), exist_ok=True)

        default_content = '[]'
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(default_content)
        print("tasks.json created successfully")


def main():
    """Main function"""
    print("TodoList Packaging Tool")
    print("=" * 30)

    if not os.path.exists('main.py'):
        print("Error: main.py not found. Please run this script in the project root directory.")
        return False

    os.makedirs('src/data', exist_ok=True)
    os.makedirs('src/img', exist_ok=True)

    create_tasks_json()

    if not check_resources():
        return False

    clean_previous_build()

    if build_executable():
        print("\nPackaging finished successfully!")
        print(f"Executable location: {os.path.abspath(os.path.join('dist', 'Fluent Todo List.exe'))}")
        return True
    else:
        print("\nPackaging failed!")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
