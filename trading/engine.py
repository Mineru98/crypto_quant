from trading.account import Account
from trading.broker import Broker
from trading.module import Logger
from trading.strategy import Strategy


class Engine:
    def __init__(
        self, strategy, chart_data, strategy_config, market_info, initial_margin
    ):
        self._strategy_config = strategy_config
        self._strategy: Strategy = strategy(config=strategy_config)
        self._df = self._strategy.update(chart_data)
        self._account = Account()
        self._broker = Broker(self._account)  # 거래 실행 모듈 계좌 사용
        self._logger = Logger()  # 백테스팅 정보 로깅)

    def run(self):
        iterator = self._df.iter_rows()
        cols = self._df.columns

        for i, data in enumerate(iterator):
            data = dict(zip(cols, data))
            ...

            # 미체결 주문 처리(이전 data에서 주문 넣고, 현재 data로 처리되므로 미래시점 체결)
            self._broker.execute_orders(data)

            # 현재 가격 기준으로 포트폴리오 최신화
            self._account.update(data)

            state_dict = {
                # 계좌정보, 현재 주문정보, 현제 data, 가격정보 등 전략에서 필요로 하는 정보 추출
            }

            actions = self._strategy.execute(
                state_dict
            )  # 해당 정보로 전략의 execute 메서드 실행시 매수 또는 매도 액션 return

            self._broker.order(actions)  # broker 가 체결 처리

            # Logger에 필요한 정보 넣기(거래 내역 및 잔고 등)
            # self._logger.add_...info(...)
            # self._logger.add_...info(...)

    def get_result(self):
        ...
        # draw using self._logger
