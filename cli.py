# -*- coding:utf-8 -*-
import json
import os
import re
from typing import List

import fire
from dotenv import load_dotenv
from groq import Groq

from trading.constant import TEMPLATE_CLASS_NAME
from trading.strategy import get_all_strategies


class Backtest:
    def __init__(self):
        load_dotenv()
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    def __recommend_strategy(self, strategies: List[str]):
        strategies = "\n- ".join(strategies)
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "you are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"""### 요청 사항
- 내가 이미 구현한 백테스팅 전략들은 제외하고, 백테스팅 전략들을 추천해줘.
- 반드시 한글로 작성해줘.

### 내가 구현한 전략들
{strategies}

### 출력 형식
```json
[
    {{
        "name": str,
        "description": str
    }}
]
```""",
                },
            ],
            model="llama-3.1-70b-versatile",
        )
        res = chat_completion.choices[0].message.content.strip()
        code_block_pattern = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)
        match = code_block_pattern.search(res)
        try:
            if match:
                json_content = match.group(1)
                return json.loads(json_content)
            return []
        except:
            return []

    def __make_strategy(self, name: str, description: str, reference_code: str):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "you are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"### 요청 사항\n\n- 다음 레퍼런스 코드를 보고 {name} 전략을 구현해줘.\n- 전략 이름은 {name}이고, 설명은 {description}이야.\n\n### 레퍼런스 코드\n\n{reference_code}",
                },
            ],
            model="llama-3.2-90b-vision-preview",
        )
        res = chat_completion.choices[0].message.content.strip()
        code_block_pattern = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL)
        match = code_block_pattern.search(res)
        try:
            if match:
                content = match.group(1)
                return content
            return ""
        except:
            return ""

    def get_key(self):
        print("UPBIT_API_ACCESS_KEY", os.environ["UPBIT_API_ACCESS_KEY"])
        print("UPBIT_API_ACCESS_KEY", os.environ["UPBIT_API_ACCESS_KEY"])
        print("GROQ_API_KEY", os.environ["GROQ_API_KEY"])

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
                strategies = get_all_strategies()
                strategies = list(
                    map(
                        lambda x: "{} : {}".format(
                            x.__name__, x.__doc__.split("\n")[0].strip()
                        ),
                        strategies,
                    )
                )
                recommended_strategies = self.__recommend_strategy(strategies)
                if len(recommended_strategies) > 0:
                    for idx, recommended_strategy in enumerate(recommended_strategies):
                        print(
                            f"{idx + 1}. {recommended_strategy['name']} : {recommended_strategy['description']}\n"
                        )
                    strategy_idx = int(input("추천된 전략 중 하나를 선택해주세요: "))
                    strategy_name = recommended_strategies[strategy_idx - 1]["name"]
                    strategy_description = recommended_strategies[strategy_idx - 1][
                        "description"
                    ]
                else:
                    strategy_name = input("전략 이름: ")
                    if strategy_name == "":
                        strategy_name = "전략 이름"
                    strategy_description = input("전략 설명: ")
                    if strategy_description == "":
                        strategy_description = "전략 설명"
                code = self.__make_strategy(
                    strategy_name,
                    strategy_description,
                    TEMPLATE_CLASS_NAME.format(
                        class_name=name,
                        strategy_name=strategy_name,
                        strategy_description=strategy_description,
                    ),
                )
                if code != "":
                    with open(
                        f"trading/strategy/{filename}.py", "w", encoding="utf-8"
                    ) as f:
                        f.write(code)
                else:
                    print("전략 생성에 실패했습니다.")
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
