import importlib
import inspect
import os
from typing import List, Type

from .base import Strategy
from .test import TestStrategy


def get_all_strategies() -> List[Type[Strategy]]:
    """trading/strategy 디렉토리에 있는 모든 전략 클래스를 반환합니다.

    Returns:
        List[Type[Strategy]]: Strategy 클래스들의 리스트
    """
    strategies: List[Type[Strategy]] = []
    # 현재 디렉토리의 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # .py 파일들을 찾습니다 (base.py 제외)
    for file in os.listdir(current_dir):
        if file.endswith(".py") and file != "base.py" and file != "__init__.py":
            # 파일 이름에서 .py 확장자 제거
            module_name = file[:-3]
            # 모듈을 동적으로 임포트
            module = importlib.import_module(
                f".{module_name}", package="trading.strategy"
            )

            # 모듈에서 Strategy를 상속받은 클래스들을 찾습니다
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Strategy)
                    and obj != Strategy
                ):
                    strategies.append(obj())
    return strategies
