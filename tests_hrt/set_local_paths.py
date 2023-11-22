import os
import sys

sys_paths = [
    rf"E:\github\{os.getlogin()}\hhnk-threedi-tools",
    rf"E:\github\{os.getlogin()}\hhnk-research-tools",
]
for sys_path in sys_paths:
    if sys_path not in sys.path:
        if os.path.exists(sys_path):
            sys.path.insert(0, sys_path)
