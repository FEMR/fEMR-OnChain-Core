import sys
import os

# Fix for Amazon Linux 2 EB venv lib64 missing pkg_resources
for path in list(sys.path):
    if 'lib64' in path:
        lib_path = path.replace('lib64', 'lib')
        if os.path.isdir(lib_path) and lib_path not in sys.path:
            sys.path.insert(0, lib_path)
