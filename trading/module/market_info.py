class MarketInfo:
    def __init__(self, slippage: float, fee: float):
        self.__slippage = slippage
        self.__fee = fee

    @property
    def slippage(self):
        return self.__slippage

    @property
    def fee(self):
        return self.__fee
