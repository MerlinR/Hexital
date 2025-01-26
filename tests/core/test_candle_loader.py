from datetime import timedelta
from hexital.core.candle_loader import CandleLoaderRequest

def test_merge_requests_same_timeframe():
    """Test merging requests with the same timeframe"""
    reqs = [
        CandleLoaderRequest(10, timedelta(minutes=1)),
        CandleLoaderRequest(20, timedelta(minutes=1))
    ]
    result = CandleLoaderRequest.merge_requests(reqs)

    assert len(result) == 1
    assert result[0].n_candles == 20
    assert result[0].timeframe == timedelta(minutes=1)
    assert result[0]._skip_last == 0

def test_merge_requests_dependent_timeframes():
    """Test multiple timeframes where larger ones depend on smaller ones"""
    reqs = [
        CandleLoaderRequest(60, timedelta(minutes=1)),  # 60 min = 1 hour
        CandleLoaderRequest(2, timedelta(hours=1))      # 2 hours
    ]
    result = CandleLoaderRequest.merge_requests(reqs)

    assert len(result) == 2
    assert result[0].n_candles == 60
    assert result[0].timeframe == timedelta(minutes=1)
    assert result[1].n_candles == 2
    assert result[1].timeframe == timedelta(hours=1)
    assert result[1]._skip_last == 1  # Can build 1 hour from 60 minutes

def test_merge_requests_complete_coverage():
    """Test case where larger timeframe can be completely built from smaller one"""
    reqs = [
        CandleLoaderRequest(120, timedelta(minutes=1)),  # 120 min = 2 hours
        CandleLoaderRequest(2, timedelta(hours=1))       # 2 hours
    ]
    result = CandleLoaderRequest.merge_requests(reqs)

    assert len(result) == 1
    assert result[0].n_candles == 120
    assert result[0].timeframe == timedelta(minutes=1)

def test_merge_requests_incompatible_timeframes():
    """Test handling of timeframes that aren't multiples of each other"""
    reqs = [
        CandleLoaderRequest(10, timedelta(minutes=7)),   # 7 min
        CandleLoaderRequest(5, timedelta(minutes=13))    # 13 min
    ]
    result = CandleLoaderRequest.merge_requests(reqs)

    assert len(result) == 2
    assert all(req._skip_last == 0 for req in result)
    # Verify timeframes are preserved
    timeframes = {req.timeframe for req in result}
    assert timeframes == {timedelta(minutes=7), timedelta(minutes=13)}

def test_merge_requests_empty_list():
    """Test handling of empty request list"""
    result = CandleLoaderRequest.merge_requests([])
    assert result == []

def test_merge_requests_single_request():
    """Test handling of single request"""
    req = CandleLoaderRequest(10, timedelta(minutes=5))
    result = CandleLoaderRequest.merge_requests([req])

    assert len(result) == 1
    assert result[0].n_candles == 10
    assert result[0].timeframe == timedelta(minutes=5)
    assert result[0]._skip_last == 0


if __name__ == "__main__":
    print("Running tests...")
    test_merge_requests_same_timeframe()
    test_merge_requests_dependent_timeframes()
    test_merge_requests_complete_coverage()
    test_merge_requests_incompatible_timeframes()
    test_merge_requests_empty_list()
    test_merge_requests_single_request()
    print("All tests passed!")
