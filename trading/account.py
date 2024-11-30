import os
from collections import deque
from typing import Any, Dict

from dotenv import load_dotenv
from pyupbit import Upbit

from trading.module import Position, get_active_targets


class Account:
    def __init__(self):
        """계좌 초기화

        Args:
            target_coin (List[str], optional): 투자 종목. Defaults to ["KRW-DOGE"].
        """
        load_dotenv()
        # 업비트 클라이언트 정의
        self.client = Upbit(
            os.environ["UPBIT_API_ACCESS_KEY"], os.environ["UPBIT_API_SECRET_KEY"]
        )
        self.__queue = deque()
        # 현재 active 상태 목록
        self.__target_coin = get_active_targets()
        self.__position = Position()

    @property
    def balance(self):
        """현금 잔고

        Returns:
            float: 현금 잔고
        """
        return self.client.get_balance("KRW")

    def info(self) -> Dict[str, Any]:
        # 현금 잔고 로드
        self.__position.balance = self.client.get_balance("KRW")
        # 매수 코인 잔고 현황 로드
        for coin in self.__target_coin:
            self.__position.add(
                coin, self.client.get_balance(coin), self.client.get_amount(coin)
            )
        # 지갑 상황 반환
        return self.__position.to_json()

    def update(self, price_info):
        pass

    def deposit(self, amt: float):
        pass
