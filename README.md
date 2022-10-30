# portfolio-screener

A screener tool that uses the [Börsdata API](https://github.com/Borsdata-Sweden/API) and [borsdata-sdk](https://github.com/JoelRoxell/borsdata-sdk) to screen for companies in your portfolio by looking at difference to mean of a KPI such as P/E. At the moment, only P/E is available.

How to use:
1. Clone this repo 
2. Acquire Börsdata API key and place key in root of repo in a file called `authkey.txt`.
3. Install [borsdata-sdk](https://github.com/JoelRoxell/borsdata-sdk)
4. Run the screener: `py pe-screener.py`
