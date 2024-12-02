from typing import Dict, List, Literal, Optional

import koreanize_matplotlib
import matplotlib.pyplot as plt
import polars as pl
from tqdm import tqdm

from trading.account import Account
from trading.broker import Broker
from trading.constant import PALETTE
from trading.module import Logger
from trading.strategy import Strategy


class Engine:
    def __init__(
        self,
        strategy: Strategy,
        chart_data: pl.DataFrame,
        strategy_config: Dict[Literal["short_ma", "long_ma"], int],
        market_info: Dict[Literal["slippage", "fee"], float],
        initial_margin: float,
        is_live: bool = False,
    ):
        """엔진 초기화

        Args:
            strategy (Strategy): 전략 클래스
            chart_data (pl.DataFrame): 차트 데이터
            strategy_config (Dict[Literal["short_ma", "long_ma"], int]): 전략 설정 파라미터
            market_info (Dict[Literal["slippage", "fee"], float]): 슬리피지와 거래수수료 파라미터
            is_live (bool, optional): 실제 거래 여부. Defaults to False.
        """
        self.__strategy_config = strategy_config
        self.__strategy: Strategy = strategy(config=strategy_config)
        self.__df = self.__strategy.update(chart_data)
        self.__account = Account(is_live=is_live, balance=initial_margin)
        self.__broker = Broker(self.__account, market_info)  # 거래 실행 모듈 계좌 사용
        self.__logger = Logger()  # 백테스팅 정보 로깅

    def run(self, ticker_name: str = "KRW-AVAX"):
        iterator = self.__df.iter_rows()
        cols: List[
            Literal["Date", "high", "open", "close", "low", "volume", "value"]
        ] = self.__df.columns

        pbar = tqdm(total=len(self.__df), desc="백테스팅 진행률")
        for i, data in enumerate(iterator):
            pbar.update(1)
            if i == len(self.__df) - 1:
                pbar.close()
            data = dict(zip(cols, data))

            # 미체결 주문 처리(이전 data에서 주문 넣고, 현재 data로 처리되므로 미래시점 체결)
            self.__broker.execute_orders(data)

            # 현재 가격 기준으로 포트폴리오 최신화
            self.__account.update_price(data["close"], ticker_name)
            state_dict = {
                "ticker_name": ticker_name,
                "price": data["close"],
                "position": self.__account.has_position(ticker_name),
                "balance": self.__account.balance,
                "count": self.__account.get_count(ticker_name),
                "fee": self.__broker.fee,
                "slippage": self.__broker.slippage,
                **data,
            }

            # 해당 정보로 전략의 execute 메서드 실행시 매수 또는 매도 액션 return
            actions = self.__strategy.execute(state_dict)

            # broker 가 체결 처리
            self.__broker.place_order(actions)

            # Logger에 필요한 정보 넣기(거래 내역 및 잔고 등)
            self.__logger.add_info(self.__account.info(), data["Date"])

    def get_result(self, file_name: Optional[str] = None):
        # 서브플롯 생성
        fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(20, 12), height_ratios=[2, 1])
        fig.subplots_adjust(hspace=0.3)

        # 제목에 슬리피지와 수수료율 표시
        fig.suptitle(
            f"슬리피지: {self.__broker.slippage*100}%, 수수료율: {self.__broker.fee*100}%",
            fontsize=12,
        )

        # 첫 번째 서브플롯 - 가격과 변동성
        i = 0
        for key, value in self.__strategy.description().items():
            ax1.plot(self.__df["Date"], self.__df[key], label=value, color=PALETTE[i])
            i += 1

        ax1.set_xlabel("날짜")
        ax1.set_ylabel("가격 (KRW)")
        ax1.tick_params(axis="y")
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: format(int(x), ","))
        )

        ax2 = ax1.twinx()
        ax2.fill_between(
            self.__df["Date"],
            self.__df["변동성"],
            alpha=0.1,
            color="blue",
            label="변동성",
        )
        ax2.set_ylabel("변동성 (%)")
        ax2.tick_params(axis="y")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        # 두 번째 서브플롯 - 평가금
        ax3.plot(
            self.__logger.evaluation["Date"],
            self.__logger.evaluation["총 평가"],
            label="평가금",
            color=PALETTE[i],
        )
        ax3.set_xlabel("날짜")
        ax3.set_ylabel("평가금 (KRW)")
        ax3.tick_params(axis="y")
        ax3.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: format(int(x), ","))
        )
        ax3.legend(loc="upper left")
        if file_name is not None:
            plt.savefig(file_name)
        else:
            plt.show()
