# - NestedSource


#     def _find_reading(
#         self, source: Source | None = None, index: Optional[int] = None
#     ) -> Reading | NullReadingType:
#         if not source or (isinstance(source, str) and source == self.name):
#             if not self._readings or (
#                 index is not None and not valid_index(index, len(self._readings))
#             ):
#                 return None
#             return self._readings[self._active_index] if index is None else self._readings[index]
#         elif isinstance(source, str) and self.sub_indicators.get(source):
#             return self.sub_indicators[source].reading(index=index)
#         elif isinstance(source, str):
#             if not self.candles or (
#                 index is not None and not valid_index(index, len(self.candles))
#             ):
#                 return None
#             return getattr(
#                 self.candles[self._active_index if index is None else index], source, None
#             )
#         elif isinstance(source, Indicator):
#             return source.reading(index=index)
#         elif isinstance(source, NestedSource):
#             return source.reading(index)

#     def _find_readings(self, source: Source | None = None) -> List[Reading | NullReadingType]:
#         if not source or (isinstance(source, str) and source == self.name):
#             return self._readings
#         elif isinstance(source, str) and self.sub_indicators.get(source):
#             return self.sub_indicators[source]._find_readings()
#         elif isinstance(source, str) and self.candles and getattr(self.candles[0], source, None):
#             return [getattr(v, source) for v in self.candles]
#         elif isinstance(source, Indicator):
#             return source._readings
#         elif isinstance(source, NestedSource):
#             return source._readings
#         return []

#     def exists(self, source: Optional[Source] = None) -> bool:
#         value = self._find_reading(source)
#         if isinstance(value, dict):
#             return any(not is_none(v) for v in value.values())
#         return not is_none(value)

#     def prev_exists(self, source: Optional[Source] = None) -> bool:
#         if self._active_index == 0:
#             return False
#         value = self._find_reading(source, self._active_index - 1)
#         if isinstance(value, dict):
#             return any(not is_none(v) for v in value.values())
#         return not is_none(value)

#     def prev_reading(
#         self, source: Optional[Source] = None, default: Optional[T] = None
#     ) -> Reading | T:
#         if self._active_index == 0:
#             return default
#         value = self._find_reading(source, self._active_index - 1)
#         return value if not is_none(value) else default

#     def reading(
#         self,
#         source: Source | None = None,
#         index: Optional[int] = None,
#         default: Optional[T] = None,
#     ) -> Reading | T:
#         """Simple method to get an indicator reading from the index
#         Name can use '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""
#         value = self._find_reading(source, index)
#         return value if not is_none(value) else default

#     def reading_count(self, source: Source | None = None, index: Optional[int] = None) -> int:
#         """Returns how many instance of the given indicator exist"""
#         return reading_count(
#             self._find_readings(source),
#             index if index is not None else self._active_index,
#         )

#     def reading_period(
#         self, period: int, source: Source | None = None, index: Optional[int] = None
#     ) -> bool:
#         """Will return True if the given indicator goes back as far as amount,
#         It's true if exactly or more than. Period will be period -1"""

#         return reading_period(
#             self._find_readings(source),
#             period,
#             index if index is not None else self._active_index,
#         )

#     def candles_sum(
#         self,
#         length: int = 1,
#         source: Source | None = None,
#         index: Optional[int] = None,
#         include_latest: bool = True,
#     ) -> float | None:
#         return candles_sum(
#             self._find_readings(source),
#             length,
#             index if index is not None else self._active_index,
#             include_latest,
#         )

#     def candles_average(
#         self,
#         length: int = 1,
#         source: Source | None = None,
#         index: Optional[int] = None,
#         include_latest: bool = True,
#     ) -> float | None:
#         return candles_average(
#             self._find_readings(source),
#             length,
#             index if index is not None else self._active_index,
#             include_latest,
#         )

#     def get_readings_period(
#         self,
#         length: int = 1,
#         source: Source | None = None,
#         index: Optional[int] = None,
#         include_latest: bool = False,
#     ) -> List[float | int]:
#         return get_readings_period(
#             self._find_readings(source),
#             length,
#             index if index is not None else self._active_index,
#             include_latest,
#         )


# class NestedSource:
#     indicator: Indicator
#     nested_name: str

#     def __init__(self, indicator: Indicator, nested_name: str):
#         self.indicator = indicator
#         self.nested_name = nested_name

#     def reading(self, index: Optional[int] = None) -> Reading:
#         value = self.indicator.reading(index=index)
#         if isinstance(value, dict):
#             return value.get(self.nested_name)
#         return value

#     @property
#     def _readings(self) -> List[Reading | NullReadingType]:
#         return [v.get(self.nested_name) for v in self.indicator.readings if isinstance(v, dict)]

#     @property
#     def readings(self) -> List[Reading]:
#         return [
#             v.get(self.nested_name) if isinstance(v, dict) else is_null_conv(v)
#             for v in self.indicator.readings
#         ]

#     @property
#     def timeframe(self) -> timedelta | None:
#         return self.indicator._timeframe

#     def __str__(self):
#         return f"{self.indicator.name}.{self.nested_name}"


# Source: TypeAlias = str | Indicator | NestedSource
