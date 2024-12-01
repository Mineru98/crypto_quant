from typing import Dict, List, Literal

import polars as pl

from trading.module import Order
from trading.strategy.base import Strategy


class TestStrategy(Strategy):
    """골든 크로스/데드 크로스 기반의 매매 전략

    n일 이동평균선이 m일 이동평균선을 상향 돌파할 때 매수(골든 크로스),
    하향 돌파할 때 매도(데드 크로스)하는 전략을 구현합니다.
    현재 잔고 기준으로 살 수 있는 최대 수량으로 주문합니다.

    Attributes:
        ready (bool): 전략 실행 준비 상태
        _config (Dict[Literal["short_ma", "long_ma"], int]): 전략 설정 파라미터
        _df (pl.DataFrame): 차트 데이터

    Example:
        >>> config = {"short_ma": 5, "long_ma": 20}
        >>> strategy = TestStrategy(config)
        >>> orders = strategy.execute(state_dict)
    """

    def __init__(
        self,
        config: Dict[Literal["short_ma", "long_ma"], int] = {},
        ready=True,
    ):
        super().__init__(config, ready=ready)

    def description(self) -> Dict[str, str]:
        short_ma = self._config["short_ma"]
        long_ma = self._config["long_ma"]

        return {
            "close": "가격",
            f"ma{short_ma}": f"{short_ma}일 이동평균",
            f"ma{long_ma}": f"{long_ma}일 이동평균",
            # "변동성": "변동성",
        }

    def execute(self, state_dict: Dict[str, float]) -> List[Order]:
        orders = []
        ticker_name = state_dict["ticker_name"]
        price = state_dict["price"]  # 현재 가격
        count = state_dict.get("count", 0.0)  # 보유 수량
        ma_n = state_dict[f"ma{self._config['short_ma']}"]  # n일 이동평균선
        ma_m = state_dict[f"ma{self._config['long_ma']}"]  # m일 이동평균선
        position = state_dict.get("position", False)  # 해당 종목 보유 상태
        balance = state_dict.get("balance", 0.0)  # 남은 잔고
        fee = state_dict.get("fee", 0.0005)  # 수수료
        slippage = state_dict.get("slippage", 0.01)  # 슬리피지
        if position:
            quantity = count
        else:
            quantity = (
                balance / price
                if price >= 1000000
                else balance // price if balance >= price else 0
            )  # 주문 수량(최대)

        if ma_n is None or ma_m is None:
            return orders
        # 매수 타이밍
        if ma_n > ma_m and not position:
            price = price * (1 + slippage)
            fee = price * fee
            while balance < (price * quantity + fee) and quantity > 0:
                if quantity >= 1:
                    quantity = quantity - 1
                else:
                    quantity = quantity * 0.99
            if quantity > 0:
                orders.append(
                    Order(
                        action="buy",
                        quantity=quantity,
                        price=price,
                        ticker_name=ticker_name,
                    )
                )
        # 매도 타이밍
        elif ma_n < ma_m and position:
            orders.append(
                Order(
                    action="sell",
                    quantity=quantity,
                    price=price,
                    ticker_name=ticker_name,
                )
            )

        return orders

    def update(self, df: pl.DataFrame) -> pl.DataFrame:
        short_ma = self._config["short_ma"]
        long_ma = self._config["long_ma"]

        df = df.with_columns(
            [
                pl.col("close")
                .rolling_mean(window_size=short_ma)
                .alias(f"ma{short_ma}"),
                pl.col("close").rolling_mean(window_size=long_ma).alias(f"ma{long_ma}"),
            ]
        )
        df = df.with_columns(
            ((pl.col("high") - pl.col("low")) / pl.col("open") * 100).alias("변동성")
        )
        self._df = df
        return df
