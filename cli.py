# -*- coding:utf-8 -*-
import os

import fire
from dotenv import load_dotenv

from trading.strategy import print_all_strategies


class Backtest:
    def __init__(self):
        load_dotenv()

    def get_key(self):
        print("API_ACCESS_KEY", os.environ["API_ACCESS_KEY"])
        print("API_SECRET_KEY", os.environ["API_SECRET_KEY"])

    def run(self):
        """백테스트를 실행합니다.

        Example:
            $ python cli.py run
        """
        pass

    def show(self):
        """만들어 진 전략들을 보여줍니다.

        Example:
            $ python cli.py show
        """
        print_all_strategies()


if __name__ == "__main__":
    fire.Fire(Backtest)
