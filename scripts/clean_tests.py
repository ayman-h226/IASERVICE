import os
import shutil

def remove_dir_if_exists(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

if __name__ == "__main__":
    remove_dir_if_exists("__pycache__")
    remove_dir_if_exists(".pytest_cache")
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                full_path = os.path.join(root, d)
                shutil.rmtree(full_path)
    print("Test caches cleaned.")
