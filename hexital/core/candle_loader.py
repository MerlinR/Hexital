import asyncio
from datetime import datetime, timedelta
from .candle import Candle
from typing import TYPE_CHECKING, Optional
from functools import cached_property

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .hexital import Hexital

class LoaderConfigHints:
    default: 'LoaderConfig'

@dataclass
class LoaderConfig(LoaderConfigHints):
    ma_warmup_factor: float = 2  # ema, rma, hma, etc

LoaderConfig.default = LoaderConfig()

@dataclass
class CandleLoaderRequest:
    n_candles: int
    timeframe: timedelta

    _skip_last: int = field(init=False, default=0)

    def requested_duration(self) -> timedelta:
        return self.timeframe * (self.n_candles - self._skip_last)

    @staticmethod
    def merge_requests(reqs: list['CandleLoaderRequest']) -> list['CandleLoaderRequest']:
        # Group requests by timeframe
        requests_by_timeframe: dict[timedelta, CandleLoaderRequest] = {}

        # Sort requests by timeframe (smallest first) to handle dependencies
        reqs.sort(key=lambda r: r.timeframe)

        for req in reqs:
            # Check if we already have a request for this timeframe
            if req.timeframe in requests_by_timeframe:
                existing_req = requests_by_timeframe[req.timeframe]
                # Keep the request with more candles
                if req.n_candles > existing_req.n_candles:
                    requests_by_timeframe[req.timeframe] = req
                continue

            # For each smaller timeframe we've processed
            skip_count = 0
            for smaller_tf, smaller_req in requests_by_timeframe.items():
                # Check if current timeframe is a multiple of smaller timeframe
                if req.timeframe.total_seconds() % smaller_tf.total_seconds() == 0:
                    multiplier = int(req.timeframe.total_seconds() / smaller_tf.total_seconds())
                    # Calculate how many larger timeframe candles we can build from smaller ones
                    covered_candles = smaller_req.n_candles // multiplier
                    skip_count = max(skip_count, covered_candles)

            # If we can build all needed candles from smaller timeframes, skip this request
            if skip_count >= req.n_candles:
                continue

            # Adjust request to skip candles we can build from smaller timeframes
            new_req = CandleLoaderRequest(req.n_candles, req.timeframe)
            new_req._skip_last = skip_count
            requests_by_timeframe[req.timeframe] = new_req

        # Convert back to list, only including requests that need fetching
        final_reqs = [req for req in requests_by_timeframe.values() if req.n_candles > req._skip_last]
        return final_reqs

@dataclass
class CandleLoaderRequestResult:
    candles: list[Candle]
    timeframe: timedelta

@dataclass
class CandleLoader:
    h: Optional['Hexital'] = None

    async def load_past(self, request: CandleLoaderRequest) -> list[Candle]:
        """
        This is intended to be implemented by the loader implementation.
        """
        raise NotImplementedError

    async def load_requests(self, requests: list[CandleLoaderRequest]) -> list[CandleLoaderRequestResult]:
        " Will return largest timeframe first "

        requests = CandleLoaderRequest.merge_requests(requests)  # now sorted ascending by timeframe
        results = await asyncio.gather(*[self.load_past(req) for req in requests])

        check_result = True
        if check_result:
            for req, r in zip(requests, results):
                assert r[0].timeframe
                assert len(r) * r[0].timeframe == req.requested_duration()
                assert req.n_candles - req._skip_last == len(r)

        ret = []
        for req, r in reversed(list(zip(requests, results))):
            ret.append(CandleLoaderRequestResult(r, req.timeframe))
        return ret

