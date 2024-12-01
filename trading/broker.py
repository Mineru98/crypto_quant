from collections import deque
from typing import Dict, List, Literal

import polars as pl

from trading.account import Account
from trading.module import MarketInfo, Order, Transaction


class Broker:
    """실제 거래 모듈

    별도로 추상화를 하여 live와 백테스팅 분리가 필요
    """

    def __init__(
        self, account: Account, market_info: Dict[Literal["slippage", "fee"], float]
    ):
        self.__account = account
        self.__market_info = MarketInfo(
            slippage=market_info["slippage"], fee=market_info["fee"]
        )
        self.__queue: deque[Order] = deque()
        self.transactions: List[Transaction] = []

    @property
    def fee(self):
        return self.__market_info.fee

    @property
    def slippage(self):
        return self.__market_info.slippage

    def execute_orders(
        self,
        data: Dict[
            Literal["Date", "high", "open", "close", "low", "volume", "value"], float
        ],
    ) -> List[Transaction]:
        for _ in range(len(self.__queue)):
            # 큐 pop
            order = self.__queue.popleft()
            copy_order = order
            # 수수료 적용
            order.fee = self.__market_info.fee
            # 체결 가격(이때, 미래 참조를 하게 되는 것이므로 미래시점 체결)
            order.realized_price = data["close"]

            # 예상 구매 금액
            price = data["close"] * order.quantity * (1 + self.__market_info.slippage)
            # 수수료 금액
            fee = price * order.fee
            self.__account.update(
                price, order.quantity, order.ticker_name, order.action
            )
            # 체결 처리
            if order.action == "buy":
                if self.__account.balance >= price - fee:
                    self.__account.deposit(-price - fee)
                else:
                    self.__queue.append(copy_order)
            else:
                self.__account.deposit(price - fee)

    def place_order(self, actions: List[Order]):
        # 다음 tick에 체결되는 주문들을 queue에 넣어둠
        for order in actions:
            self.__queue.append(order)
