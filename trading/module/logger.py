from typing import Any, Dict

import polars as pl


class Logger:
    def __init__(self):
        self.__evaluation = pl.DataFrame()

    def add_info(self, info: Dict[str, Any], date: str):
        df = pl.DataFrame({"Date": date, **info})
        df = df.with_columns(pl.col("*").exclude("Date").cast(pl.Float64))
        self.__evaluation = pl.concat([self.__evaluation, df])

    @property
    def evaluation(self) -> pl.DataFrame:
        return self.__evaluation
