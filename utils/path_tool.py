import os

def get_project_root() -> str:
    """
    获取工程所在的根目录
    :return: 字符串根目录
    """
    # 获取当前文件的绝对路径，然后获取其父目录，再获取父目录的父目录，即为项目根目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_abs_path(relative_path: str) -> str:
    return os.path.join(get_project_root(), relative_path)

if __name__ == '__main__':
    print(get_abs_path('config/config.yaml'))