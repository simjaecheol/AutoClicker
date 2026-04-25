import os
import sys

def get_resource_path(relative_path):
    """
    PyInstaller의 임시 폴더 또는 일반 실행 환경에서의 절대 경로를 반환합니다.
    """
    try:
        # PyInstaller에 의해 임시 폴더가 생성된 경우 (_MEIPASS)
        base_path = sys._MEIPASS
    except AttributeError:
        # 일반 파이썬 실행 환경인 경우 (프로젝트 루트 기준)
        # 현재 파일(src/utils/path_helper.py) 위치에서 프로젝트 루트로 이동
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)
