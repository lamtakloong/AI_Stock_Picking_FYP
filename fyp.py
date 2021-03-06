import pandas as pd
import numpy as np





############  TA  #############
def RSI(Close, periods=20):
    length = len(Close)
    rsies = [np.nan]*length
    #The data length does not exceed the period and cannot be calculated;
    if length <= periods:
        return rsies
    #Used for fast calculation;
    up_avg = 0
    down_avg = 0

    # First calculate the first RSI,
    # Periods+1 data before use,
    # Form periods of spread sequence;
    first_c = Close[:periods+1]
    for i in range(1, len(first_c)):
        # Price increased;
        if first_c[i] >= first_c[i-1]:
            up_avg += first_c[i] - first_c[i-1]
        # Price drop;
        else:
            down_avg += first_c[i-1] - first_c[i]
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsies[periods] = 100 - 100/(1+rs)

    #Fast calculation will be used later;
    for j in range(periods+1, length):
        up = 0
        down = 0
        if Close[j] >= Close[j-1]:
            up = Close[j] - Close[j-1]
            down = 0
        else:
            up = 0
            down = Close[j-1] - Close[j]
        #The calculation formula of moving average;
        up_avg = (up_avg*(periods - 1) + up)/periods
        down_avg = (down_avg*(periods - 1) + down)/periods
        rs = up_avg/down_avg
        rsies[j] = 100 - 100/(1+rs)
    return rsies  