from abc import ABC, abstractmethod
from typing import Dict, List

import polars as pl

from trading.module import Order


class Strategy(ABC):
    def __init__(self, config, ready=False):
        self._config = config
        self._df = None
        self._ready = ready

    @property
    def __name__(self):
        return self.__class__.__name__

    @property
    def ready(self):
        return self._ready

    @abstractmethod
    def description(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def execute(self, state_dict) -> List[Order]:
        pass

    @abstractmethod
    def update(self, chart_data: pl.DataFrame) -> pl.DataFrame:
        pass
