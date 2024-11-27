from typing import Any, Dict


class Position:
    def __init__(self):
        self.__balance = 0.0
        self.__target_coin = {}

    def add(self, coin_name: str, count: float, amount: float):
        """투자종목 추가

        Args:
            coin_name (str): 종목명
            count (float): 보유 수량
            amount (float): 누적 매수 금액
        """
        self.__target_coin[coin_name] = {"count": count, "amount": amount}

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

    def to_json(self) -> Dict[str, Any]:
        """Position 객체의 모든 property를 dictionary 형태로 반환
        Returns:
            dict: Position의 모든 property를 포함하는 dictionary
        """
        return {"balance": self.__balance, **self.__target_coin}
