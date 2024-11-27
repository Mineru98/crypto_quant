from typing import List

from trading.module import Order, Transaction


class Broker:
    def __init__(self, account, market_info):
        pass

    def place_order(self, actions: List[Order]):
        # 주문 queue에 넣어서 engine에서 주문 queue에 있는건 처리하는 방식(미래에 체결되게)
        for order in actions:
            # validation check
            self._qeueue.put(order)

    def execute_orders(self, data) -> List[Transaction]:
        # data: Engine에서 체결에 필요한 정보(가격 등..)
        transactions = []
        # queue에 쌓여있는 주문들 다 가져와서 처리
        # 청산시 차액만큼 deposit 이용해 Position 및 계좌 잔량 증감
        return transactions
