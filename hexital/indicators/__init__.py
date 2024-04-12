from .adx import ADX
from .amorph import Amorph
from .atr import ATR
from .counter import Counter
from .ema import EMA
from .hla import HighLowAverage
from .hma import HMA
from .kc import KC
from .macd import MACD
from .obv import OBV
from .rma import RMA
from .roc import ROC
from .rsi import RSI
from .sma import SMA
from .stdev import STDEV
from .stoch import STOCH
from .supertrend import Supertrend
from .tr import TR
from .vwap import VWAP
from .vwma import VWMA
from .wma import WMA

INDICATOR_MAP = {
    "Amorph": Amorph,
    "Counter": Counter,
    "ADX": ADX,
    "ATR": ATR,
    "EMA": EMA,
    "HLA": HighLowAverage,
    "HMA": HMA,
    "KC": KC,
    "MACD": MACD,
    "OBV": OBV,
    "RMA": RMA,
    "ROC": ROC,
    "RSI": RSI,
    "SMA": SMA,
    "STDEV": STDEV,
    "STOCH": STOCH,
    "Supertrend": Supertrend,
    "TR": TR,
    "VWAP": VWAP,
    "VWMA": VWMA,
    "WMA": WMA,
}
