TEMPLATE_CLASS_NAME = """from typing import List

import pandas as pd

from trading.module import Order
from trading.strategy.base import Strategy


class {class_name}(Strategy):
    \"\"\"{strategy_name}
    
    {strategy_description}

    Attributes:
        ready (bool): 전략 실행 준비 상태
        _config (dict): 전략 설정 파라미터
        _df (pd.DataFrame): 차트 데이터

    Example:
        >>> config = {{"short_ma": 5, "long_ma": 20}}
        >>> strategy = {class_name}(config)
        >>> orders = strategy.execute(state_dict)
    \"\"\"

    def __init__(self, config={{}}, ready=False):
        super().__init__(config, ready=ready)

    def execute(self, state_dict) -> List[Order]:
        pass

    def update(self, chart_data: pd.DataFrame) -> pd.DataFrame:
        pass
"""
