from .adx import ADX
from .amorph import Amorph
from .atr import ATR
from .ema import EMA
from .hla import HighLowAverage
from .kc import KC
from .macd import MACD
from .obv import OBV
from .rma import RMA
from .roc import ROC
from .rsi import RSI
from .sma import SMA
from .stoch import STOCH
from .supertrend import Supertrend
from .tr import TR
from .vwap import VWAP
from .vwma import VWMA
from .wma import WMA

INDICATOR_MAP = {
    "Amorph": Amorph,
    "ADX": ADX,
    "ATR": ATR,
    "EMA": EMA,
    "HLA": HighLowAverage,
    "KC": KC,
    "MACD": MACD,
    "OBV": OBV,
    "RMA": RMA,
    "ROC": ROC,
    "RSI": RSI,
    "SMA": SMA,
    "STOCH": STOCH,
    "Supertrend": Supertrend,
    "TR": TR,
    "VWAP": VWAP,
    "VWMA": VWMA,
    "WMA": WMA,
}
