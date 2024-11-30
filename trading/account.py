import os
from collections import deque
from typing import Any, Dict, Literal

from dotenv import load_dotenv
from pyupbit import Upbit

from trading.module import Position, get_active_targets


class Account:
    __balance = 0.0
    __is_live = False

    def __init__(self, is_live=False, balance=1000000.0):
        """계좌 초기화

        Args:
            is_live (bool, optional): 실제 거래 여부. Defaults to False.
            balance (float, optional): 현금 잔고. Defaults to 1,000,000
        """
        load_dotenv()
        self.__is_live = is_live
        if self.__is_live:
            self.__balance = self.client.get_balance("KRW")
        else:
            self.__balance = balance
        # 업비트 클라이언트 정의
        self.client = Upbit(
            os.environ["UPBIT_API_ACCESS_KEY"], os.environ["UPBIT_API_SECRET_KEY"]
        )
        self.__queue = deque()
        # 현재 active 상태 목록
        self.__target_coin = get_active_targets()
        self.__position = Position()

    @property
    def balance(self) -> float:
        """현금 잔고

        Returns:
            float: 현금 잔고
        """
        if self.__is_live:
            return self.client.get_balance("KRW")
        else:
            return self.__balance

    def has_position(self, ticker_name: str) -> bool:
        return self.__position.info()[ticker_name]["count"] > 0

    def info(self) -> Dict[str, Any]:
        # 현금 잔고 로드
        self.__position.balance = self.balance
        # 매수 코인 잔고 현황 로드
        for coin in self.__target_coin:
            self.__position.add(
                coin, self.client.get_balance(coin), self.client.get_amount(coin)
            )
        # 지갑 상황 반환
        return self.__position.summary()

    def update(
        self,
        price_info: Dict[
            Literal["high", "open", "close", "low", "volume", "value"], float
        ],
        ticker_name: str,
    ):
        # 내 잔고 가치 최신화
        self.__position.update_price(price_info["close"], ticker_name)

    def deposit(self, amt: float):
        """잔고 증감

        Args:
            amt (float): 증감 금액
        """
        self.__balance += amt
