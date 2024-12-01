from typing import Literal


class Order:
    def __init__(
        self,
        action: Literal["buy", "sell"],
        quantity: int,
        price: float,
        ticker_name: str,
    ):
        self.__action = action
        self.__ticker_name = ticker_name
        self.__quantity = quantity
        self.__realized_price = price
        self.__order_price = price
        self.__fee = 0.05

    @property
    def ticker_name(self) -> str:
        """종목명"""
        return self.__ticker_name

    @property
    def action(self) -> Literal["buy", "sell"]:
        """주문 종류"""
        return self.__action

    @property
    def quantity(self) -> int:
        """주문 수량"""
        return self.__quantity

    @property
    def order_price(self) -> float:
        """주문 가격"""
        return self.__order_price

    @property
    def realized_price(self) -> float:
        """체결 가격"""
        return self.__realized_price

    @realized_price.setter
    def realized_price(self, price: float):
        self.__realized_price = price

    @property
    def fee(self) -> float:
        """수수료"""
        return self.__fee

    @fee.setter
    def fee(self, fee: float):
        self.__fee = fee

    def __str__(self) -> str:
        return f"action : {self.action}, quantity : {self.quantity}, ticker_name : {self.ticker_name}, order_price : {self.order_price}, realized_price : {self.realized_price}, fee : {self.fee}"
