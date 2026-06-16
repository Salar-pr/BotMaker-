import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stt


def fetch(symbol: str, market: str = 'USD'):
    URL = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={}&market={' \
          '}&apikey=LN6AB4R2IAMHDV8I&datatype=csv'.format(symbol, market)

    Columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    DF = pd.read_csv(URL, sep=',', usecols=Columns, header=0)

    C = (DF['close'].to_numpy())[::-1].copy()

    L = np.log(C)

    return C, L


Ceth, Leth = fetch('ETH')
Cbtc, Lbtc = fetch('BTC')

Cs = np.polyfit(Lbtc, Leth, 1)
P = np.poly1d(Cs)

relation = 'log(ETH) = {}*log(BTC) + {}'.format(str(round(Cs[0], 2)), str(round(Cs[1], 2)))

plt.scatter(Lbtc, Leth, s=4)
plt.plot([10, 12], [P(10), P(12)], label='Linear Regression', linewidth=1.3, c='k')
plt.title(relation)
plt.xlabel('log(BTC Price)')
plt.ylabel('log(ETH Price)')
plt.show()


PCC, _ = stt.pearsonr(Lbtc, Leth)
print(PCC)
