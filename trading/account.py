import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from pyupbit import Upbit

from trading.module import Position


class Account:
    def __init__(self, target_coin: List[str] = ["KRW-DOGE"]):
        """계좌 초기화

        Args:
            target_coin (List[str], optional): 투자 종목. Defaults to ["KRW-DOGE"].
        """
        load_dotenv()
        self.client = Upbit(
            os.environ["UPBIT_API_ACCESS_KEY"], os.environ["UPBIT_API_SECRET_KEY"]
        )
        self.__queue = []
        self.__target_coin = target_coin
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
