import os


def ensure_folder(root: str, *paths: str) -> str:
    path = os.path.join(root, *paths)
    if os.path.isfile(path):
        raise FileExistsError()
    os.makedirs(path, exist_ok=True)
    return path


def ensure_file(root: str, *paths: str) -> str:
    path = os.path.join(root, *paths)
    if os.path.isdir(path):
        raise IsADirectoryError()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
