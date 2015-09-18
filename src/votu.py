# Votanto utils

import os

def ensure_directory(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
