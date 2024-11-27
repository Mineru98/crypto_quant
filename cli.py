# -*- coding:utf-8 -*-
import os

import fire
from dotenv import load_dotenv

from trading.constant import TEMPLATE_CLASS_NAME
from trading.strategy import get_all_strategies


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
        strategies = get_all_strategies()

        print("=== 사용 가능한 전략 목록 ===")
        idx = 1
        for strategy in strategies:
            if hasattr(strategy, "ready") and strategy.ready:
                print(f"{idx}. {strategy.__name__}")
                if strategy.__doc__:
                    doc_first_line = strategy.__doc__.split("\n")[0].strip()
                    print(f"   설명: {doc_first_line}")
                idx += 1

    def make(self, name: str):
        """전략을 생성합니다.

        Example:
            $ python cli.py make --name=<name>
            $ python cli.py make --name <name>
        """
        if name[0] == name[0].upper() and name.endswith("Strategy"):
            filename = name.replace("Strategy", "").lower()
            if os.path.exists(f"trading/strategy/{filename}.py"):
                print(f"전략 {filename}은 이미 존재합니다.")
            else:
                strategy_name = input("전략 이름: ")
                if strategy_name == "":
                    strategy_name = "전략 이름"
                strategy_description = input("전략 설명: ")
                if strategy_description == "":
                    strategy_description = "전략 설명"
                with open(
                    f"trading/strategy/{filename}.py", "w", encoding="utf-8"
                ) as f:
                    f.write(
                        TEMPLATE_CLASS_NAME.format(
                            class_name=name,
                            strategy_name=strategy_name,
                            strategy_description=strategy_description,
                        )
                    )
        else:
            print("전략 이름은 대문자로 시작하고 Strategy로 끝나야 합니다.")

    def delete(self, name: str):
        """전략을 삭제합니다.

        Example:
            $ python cli.py delete --name=<name>
            $ python cli.py delete --name <name>
        """
        strategies = get_all_strategies()
        strategies = list(map(lambda x: x.__name__, strategies))
        if name in strategies:
            os.remove(f"trading/strategy/{name.replace('Strategy', '').lower()}.py")
        else:
            print(f"전략 {name}은 존재하지 않습니다.")


if __name__ == "__main__":
    fire.Fire(Backtest)
