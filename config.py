import sys
from pathlib import Path

ROOT_PATH = Path(__file__).parent
SRC_PATH = ROOT_PATH / 'src'
IMG_PATH = SRC_PATH / 'img'
DATA_FILE = SRC_PATH / 'data' / 'tasks.json'
PYTHON_PATH = Path(sys.executable).parent
PYINSTALLER_PATH = PYTHON_PATH / 'pyinstaller'