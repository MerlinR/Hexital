# Alternatives

## Talipp
Talipp (a.k.a. tali++) is a popular Python library implementing financial indicators for technical analysis. This is the only popular library which focuses incremental computation.

**Pros**

- Incremental computation
- Fast computation
- Extremely easy to setup
- Good Documentation

**Cons**

- Input to Indicator's is list of single values, having to alter what you append into an indicator.
- Relatively limited
- No useful analysis or candle pattern methods

Talipp is an fantastic technical analysis library and the only other one i know of that's incremental, it's fast and very easy to setup and use. Talipp was the inspiration for Hexital. It's a great library and well maintained, however the input type, the interaction with the output, the lack of ability managing multiple indicators; left a lot to be desired.


*Source: [Talipp](https://nardew.github.io/talipp/latest/)*


## Pandas-TA (pandas)
Pandas-TA is arguably the most popular and well rounded Python library for calculating technical analysis, it can use TA-lib (A very fast C technical analysis library) if installed. It uses Pandas/Numpy which means it can work well with many other tools, it's very quick at calculating large sets of indicators. It's very well maintained with loads of dev involvement in the Issue's. It has an vast and ever growing amount of Indicators, it can also calculate Candle Patterns and supports strategies for bulk Indicator calculations.

**Pros**

- Very Fast
- Vast amount of Indicator's and Candle patterns
- Can use TA-lib for faster performance and more indicators
- Well Maintained
- Pandas-TA Strategies for bulk Indicator calculations

**Cons**

- Bulk Calculations
- Very slow incremental calculations due to append to Pandas and bulk calc

Pandas-TA is by far the most popular and most rounded Python technical analysis library. It's also one of the fastest with optional multiprocessing. If you **want** to be using Pandas this is the library to use. If you are focusing on backtesting this is the fastest library. Pandas-TA only flaw is that it can only do bulk calculations, that combined with Numpy/Pandas very slow appending to existing dataframes; makes Pandas-TA extremely slow when running incrementally. This problem gets exponentially worse as we get more candles.

*Source: [Pandas-TA](https://github.com/twopirllc/pandas-ta)*


## TA - Technical Analysis (pandas)
Another very popular Pandas Python technical analysis library, well maintained with a good amount of indicators. It's one of the older libraries that sticks to the Unix philosophy of 'Do one thing and do it well'. Calculate Indicators.

**Pros**

- Large amount of Indicator's
- Lightweight/simple - What you see is what you get
- Lots of control over indicator output - Manually setup indicator features you want to output

**Cons**

- Raw results, no handling of NaN's
- Finicky to setup, the fine tuning of each value from each indicator is messy
- Bulk Calculations
- Very slow incremental calculations due to append to Pandas and bulk calc


I have personally not used TA in depth, However it's well regarded and has a large user base. You also get a lot of fine tuning on what features and results you want from each indicator, however this also means far more setup for each indicator.
*Source: [TA](https://github.com/bukosabino/ta)*

## Not maintained

### Tulip Indicators (Numpy)
Tulip Indicators is maintained, however the python binding's is not.

*Source: [Tulip Indicators](https://tulipindicators.org/)*

### Finta (Pandas)
This repository has been archived by the owner on Sep 2, 2022.

*Source: [Finta](https://github.com/peerchemist/finta)*

### Pyti (pandas)
Last Updated May 8, 2018.

*Source: [Pyti](https://github.com/kylejusticemagnuson/pyti)*