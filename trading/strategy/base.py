from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from trading.module import Order


class Strategy(ABC):
    def __init__(self, config, ready=False):
        self.config = config
        self._df = None
        self._ready = ready

    @property
    def ready(self):
        return self._ready

    @abstractmethod
    def execute(self, state_dict) -> List[Order]:
        pass

    @abstractmethod
    def update(self, chart_data: pd.DataFrame) -> pd.DataFrame:
        pass