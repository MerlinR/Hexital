from .adx import ADX
from .amorph import Amorph
from .aroon import AROON
from .atr import ATR
from .bbands import BBANDS
from .counter import Counter
from .donchian import Donchian
from .ema import EMA
from .highest_lowest import HighestLowest
from .hla import HighLowAverage
from .hma import HMA
from .kc import KC
from .macd import MACD
from .obv import OBV
from .rma import RMA
from .roc import ROC
from .rsi import RSI
from .sma import SMA
from .stdev import StandardDeviation
from .stdevthres import StandardDeviationThreshold
from .stoch import STOCH
from .supertrend import Supertrend
from .tr import TR
from .tsi import TSI
from .vwap import VWAP
from .vwma import VWMA
from .wma import WMA

INDICATOR_MAP = {
    "Amorph": Amorph,
    "Counter": Counter,
    "aroon": AROON,
    "ADX": ADX,
    "ATR": ATR,
    "BBANDS": BBANDS,
    "donchian": Donchian,
    "EMA": EMA,
    "HL": HighestLowest,
    "HLA": HighLowAverage,
    "HMA": HMA,
    "KC": KC,
    "MACD": MACD,
    "OBV": OBV,
    "RMA": RMA,
    "ROC": ROC,
    "RSI": RSI,
    "SMA": SMA,
    "STDEV": StandardDeviation,
    "STDEVTHRES": StandardDeviationThreshold,
    "STOCH": STOCH,
    "Supertrend": Supertrend,
    "TR": TR,
    "TSI": TSI,
    "VWAP": VWAP,
    "VWMA": VWMA,
    "WMA": WMA,
}
