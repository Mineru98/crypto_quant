from typing import Any, Dict


class Position:
    def __init__(self):
        self.__balance = 0.0
        self.__target_coin = {}

    def add(
        self,
        ticker_name: str,
        count: float,
        amount: float,
        current_price: float = 0,
    ):
        """투자종목 추가

        Args:
            ticker_name (str): 종목명
            current_price (float): 현재 가격
            count (float): 보유 수량
            amount (float): 누적 매수 금액
        """
        self.__target_coin[ticker_name] = {
            "current_price": current_price,
            "count": count,
            "amount": amount,
        }

    def update_price(self, price: float, ticker_name: str):
        """투자종목 최신화

        Args:
            price (float): 현재 가격
            ticker_name (str): 종목명
        """
        self.__target_coin[ticker_name]["current_price"] = price

    @property
    def balance(self):
        """잔액
        Returns:
            float: 잔액
        """
        return self.__balance

    @balance.setter
    def balance(self, value: float):
        self.__balance = value

    def summary(self) -> Dict[str, Any]:
        """포트폴리오 요약

        Returns:
            Dict[str, Any]: 포트폴리오 요약
        """
        total_purchase = sum(info["amount"] for info in self.__target_coin.values())
        total_evaluation = sum(
            info["current_price"] * info["count"]
            for info in self.__target_coin.values()
        )

        return {
            "총 매수": total_purchase,
            "평가손익": total_evaluation,
            "총 평가": total_purchase + total_evaluation,
            "수익률": (total_evaluation - total_purchase) / total_purchase * 100,
            "현금 잔액": self.balance,
        }
