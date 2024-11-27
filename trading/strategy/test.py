from typing import List

import pandas as pd

from trading.module import Order

from .base import Strategy


class TestStrategy(Strategy):
    """골든 크로스/데드 크로스 기반의 매매 전략

    5일 이동평균선이 20일 이동평균선을 상향 돌파할 때 매수(골든 크로스),
    하향 돌파할 때 매도(데드 크로스)하는 전략을 구현합니다.

    Attributes:
        ready (bool): 전략 실행 준비 상태
        _config (dict): 전략 설정 파라미터
        _df (pd.DataFrame): 차트 데이터

    Example:
        >>> config = {"short_ma": 5, "long_ma": 20}
        >>> strategy = TestStrategy(config)
        >>> orders = strategy.execute(state_dict)
    """

    def __init__(self, config, ready=True):
        super().__init__(config, ready)

    def execute(self, state_dict) -> List[Order]:
        orders = []
        price = state_dict["price"]
        ma5 = state_dict["ma5"]
        ma20 = state_dict["ma20"]
        position = state_dict.get("position", 0)

        if ma5 > ma20 and position == 0:
            # Buy signal
            orders.append(Order(action="buy", quantity=10, price=price))
        elif ma5 < ma20 and position == 1:
            # Sell signal
            orders.append(Order(action="sell", quantity=10, price=price))

        return orders

    def update(self, chart_data: pd.DataFrame) -> pd.DataFrame:
        short_ma = 5
        long_ma = 20

        chart_data[f"ma{short_ma}"] = (
            chart_data["close"].rolling(window=short_ma).mean()
        )
        chart_data[f"ma{long_ma}"] = chart_data["close"].rolling(window=long_ma).mean()
        self._df = chart_data
        return chart_data
